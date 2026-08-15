"""visibility_corrected_oracle — visibility-corrected oracle, four conditions, both eval sets, 4 and 5 views.
Conditions (per view, never global):
  O0 all detections present            reproduces oracle_within_sample (harness check)
  O1 informative occlusion removed     target condition
  O2 all occlusion removed             upper bound on visibility cost
  O3 redundant occlusion only removed  control governing interpretability
Site visibility = at least one supercell copy of that site unoccluded in that view.
"""
import os as _o, sys as _s
_s.path.insert(0, _o.path.join(_o.path.dirname(_o.path.abspath(__file__)), _o.pardir, ''))
from _paths import DATA, RESULTS, SRC
import json, sys, time, numpy as np, warnings
warnings.filterwarnings("ignore"); sys.path.insert(0,f"{SRC}")
from pymatgen.core import Structure
from cocr.render import conventional_cell, VIEW_ORDER
from cocr import reconstruct as RC
from cocr.reconstruct import projection_matrices, project, _ray, _ray_intersection

def reconstruct_cond(conv, view_names, vis, tol=0.15):
    """oracle_within_sample's oracle with per-view visibility. Acceptance rule is oracle_within_sample's EXACTLY: anchor on the first
    two views in which the atom is observable, then require EVERY other view to hit an observed
    same-species point OR to have that point REMOVED (an excused miss). With nothing removed this
    reduces to reconstruct_positions term for term."""
    cart=conv.cart_coords; species=np.array([s.symbol for s in conv.species])
    Rs=projection_matrices(view_names); nv=len(Rs); n=len(conv)
    proj=[project(cart,R) for R in Rs]
    obs=[set(np.where(vis[v])[0].tolist()) for v in range(nv)]
    cand=[]
    # anchor pair: oracle_within_sample uses views 0 and 1. Keep that, but allow a later pair when an atom is not
    # observable in view 0 or 1 (removal can make the anchor pair unavailable).
    pairs=[(0,1)]+[(a,b) for a in range(nv) for b in range(a+1,nv) if (a,b)!=(0,1)]
    for v0,v1 in pairs:
        for i in sorted(obs[v0]):
            s0=species[i]; x0a,da=_ray(*proj[v0][i],Rs[v0])
            for j in sorted(obs[v1]):
                if species[j]!=s0: continue
                x0b,db=_ray(*proj[v1][j],Rs[v1])
                X,dist=_ray_intersection(x0a,da,x0b,db)
                if X is None or dist>tol: continue
                ok=True
                for vk in range(nv):
                    if vk in (v0,v1): continue
                    scr=(X@Rs[vk])[:2]
                    so=[k for k in obs[vk] if species[k]==s0]
                    if so and np.linalg.norm(proj[vk][so]-scr,axis=1).min()<=tol: continue
                    sr=[k for k in range(n) if k not in obs[vk] and species[k]==s0]
                    if sr and np.linalg.norm(proj[vk][sr]-scr,axis=1).min()<=tol: continue
                    ok=False; break
                if ok: cand.append((X,s0))
        if cand: break          # oracle_within_sample uses ONE anchor pair; fall through only if it yields nothing
    kept=[]
    for X,s in cand:
        if not any(sy==s and np.linalg.norm(X-Y)<tol for Y,sy in kept): kept.append((X,s))
    pts=np.array([k[0] for k in kept]) if kept else np.zeros((0,3))
    return {"species":[k[1] for k in kept],"cart":pts,"n_recovered":len(kept),
            "n_true":n,"count_match":len(kept)==n}

def site_vis(mask_rec, nc, nviews, cond):
    """Per-site visibility from supercell masks. Tiling is k % nc (verified)."""
    vis=np.ones((nviews,nc),bool)
    for vi,v in enumerate(VIEW_ORDER[:nviews]):
        occ=np.array(mask_rec["per_view"][v]["occ"]); red=np.array(mask_rec["per_view"][v]["red"])
        if cond=="O0": drop=np.zeros(len(occ),bool)
        elif cond=="O1": drop=occ&~red
        elif cond=="O2": drop=occ
        elif cond=="O3": drop=occ&red
        for s in range(nc):
            copies=np.arange(s,len(occ),nc)
            vis[vi,s]=bool((~drop[copies]).any())
    return vis

def run(evjs, stjs, masks, nviews, cond):
    S=json.load(open(stjs)); rows=[json.loads(l) for l in open(evjs)]
    M={r["material_id"]:r for r in masks if "error" not in r}
    out=[]; t0=time.time()
    for idx,r in enumerate(rows):
        mid=r["material_id"]
        try:
            conv=conventional_cell(Structure.from_str(S[mid]["cif"],fmt="cif"))
            vis=site_vis(M[mid], len(conv), nviews, cond)
            rec=reconstruct_cond(conv, VIEW_ORDER[:nviews], vis)
            sym=RC.recover_symmetry(rec, conv.lattice)
            out.append({"material_id":mid,"truth":r["crystal_system"],
                        "cs":sym["crystal_system"],"pg":sym.get("point_group"),
                        "sg":sym.get("space_group_number"),
                        "cs_ok":sym["crystal_system"]==r["crystal_system"],
                        "pg_ok":bool(sym.get("pg_ok", sym.get("point_group")==r.get("point_group"))),
                        "sg_ok":bool(sym.get("sg_ok", sym.get("space_group_number")==r.get("space_group_number"))),
                        "n_recovered":rec["n_recovered"],"n_true":rec["n_true"],
                        "count_match":rec["count_match"],
                        "over":rec["n_recovered"]>rec["n_true"]})
        except Exception as e:
            out.append({"material_id":mid,"error":f"{type(e).__name__}: {str(e)[:90]}"})
        if idx%70==69: print(f"    {cond} {nviews}v: {idx+1}/{len(rows)} {time.time()-t0:.0f}s", flush=True)
    return out

if __name__=="__main__":
    masks=json.load(open(f"{RESULTS}/visibility_corrected_oracle/per_view_masks.json"))
    SETS={"original":(f"{DATA}/e3/eval.jsonl",f"{DATA}/e3/structures.json"),
          "expansion":(f"{DATA}/e3x/eval.jsonl",f"{DATA}/e3x/structures.json")}
    RES={}
    for setname,(ev,stj) in SETS.items():
        for nviews in (4,5):
            for cond in ("O0","O1","O2","O3"):
                key=f"{setname}_{nviews}v_{cond}"
                print(f"  === {key}", flush=True)
                RES[key]=run(ev, stj, masks[setname], nviews, cond)
                json.dump(RES, open(f"{RESULTS}/visibility_corrected_oracle/conditions_raw.json","w"))
    print("ALL CONDITIONS COMPLETE", flush=True)
