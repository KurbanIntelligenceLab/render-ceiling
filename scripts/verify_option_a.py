"""Option A verification: every value in the red-marked revisions against checkpoint data.

Checks value equality AND sample/tolerance pairing, so a number that is real but attached to the
wrong sample or wrong delta fails. Exit non-zero on any failure.

HISTORICAL. This script audited the \\textcolor{red}{} revision spans of the ICLR draft at
manuscript/revised_new, which has been removed now that the Digital Discovery submission at
manuscript/render-ceiling-dd is the only live manuscript. MS below therefore points at a path that no
longer exists and the script exits early with a notice rather than a traceback. It is kept because it
documents how the Option A values were checked; the equivalent gate for the current manuscript is
scripts/verify_manuscript_numbers.py plus check [5] of scripts/validate_package.py.
"""
import os as _os, sys as _sys
if not _os.path.isdir("manuscript/revised_new"):
    print("verify_option_a.py: manuscript/revised_new no longer exists (ICLR draft removed). "
          "Use scripts/verify_manuscript_numbers.py for the current manuscript.")
    _sys.exit(0)
import json, re, sys, glob

MS='manuscript/revised_new'
tex=''.join(open(f).read() for f in
            [f'{MS}/main.tex']+sorted(glob.glob(f'{MS}/sections/*.tex')))
red=' '.join(re.findall(r'\\textcolor\{red\}\{(.*?)(?=\\textcolor\{red\}\{|\Z)', tex, re.S))

fr210=json.load(open('/tmp/rcval/frontier.json'))
sc=json.load(open('reports/option_a/ck_2_4_frontier1933.json'))
ph=json.load(open('reports/option_a/ck_2_3_phantoms1933.json'))
kp=json.load(open('reports/option_a/ck_1_1_kappa.json'))
n10=json.load(open('reports/option_a/ck_2_2_noise10.json'))
lad=json.load(open('reports/option_a/ck_3_3_ladder_stats.json'))
prd=json.load(open('reports/option_a/ck_2_1_kappa_prediction.json'))
TAU=0.01
fails=[]

def want(txt, s, why):
    if s not in txt: fails.append(f'{why}: expected "{s}"')

# 1. frontier: every (sample, delta, value) triple asserted in the results table
DL=fr210['delta_axis']; fz=fr210['frozen']
for d,col in ((0.005,0),(0.01,1),(0.05,2),(0.1,3),(0.15,4),(0.5,5)):
    v=fz[DL.index(d)]/210
    want(tex, f'{v:.4f}', f'n=210 frontier delta={d}')
for d in ('0.005','0.01','0.05','0.1','0.15'):
    want(tex, f"{sc['frontier'][d]['acc']:.4f}", f'n=1933 frontier delta={d}')

# 2. sample/tolerance pairing: the two headline frontier numbers must never be presented as a
#    tolerance step relative to each other (they are the same delta on different samples)
a=f"{fz[DL.index(0.15)]/210:.4f}"; b=f"{sc['frontier']['0.15']['acc']:.4f}"
for m in re.finditer(re.escape(a), tex):
    seg=tex[m.start():m.start()+260]
    if b in seg and not re.search(r'scaled|n = 1933|n=1933|sample', seg):
        fails.append(f'{a} and {b} presented together without naming the sample')
    if b in seg and re.search(r'times that|fourfold|four times|4\\times', seg):
        fails.append(f'{a}->{b} presented as a tolerance multiple (same delta, different samples)')
# any multiple-of-tau claim must match the real ratio
for mm in re.finditer(r'([\d.]+) at \$?(\d+)\\?tau', red):
    val, mult = mm.group(1), int(mm.group(2))
    d=mult*TAU
    if d in DL:
        exp=fz[DL.index(d)]/210
        if abs(float(val)-exp)>1e-4:
            fails.append(f'"{val} at {mult}tau" but measured {exp:.4f} at delta={d}')
    else:
        fails.append(f'"{val} at {mult}tau" -> delta={d} not measured')

# 3. kappa
want(tex, str(kp['kappa_frozen_max']), 'kappa frozen max')
want(tex, str(kp['kappa_offaxis_max']), 'kappa offaxis max')
want(tex, f"{kp['band']['half_width_new_kappa']:.4f}", 'band half width')
want(tex, str(kp['band']['closest_interatomic_distance']), 'closest distance')
want(tex, str(kp['band']['closest_distance_over_band_upper_edge']), 'band factor')
want(tex, str(kp['kappa_vs_angular_separation']['5deg']), 'kappa at 5deg')
if '1.7689' in red and 'squar' not in red:
    fails.append('superseded kappa 1.7689 cited without the squaring-slip explanation')

# 4. phantom census
for k,pct in ((2,'15.4'),(3,'1.9')):
    c=ph['census'][f'views_{k}']
    if abs(c['frac_nonempty']*100-float(pct))>0.05:
        fails.append(f'{k}-view nonempty pct: text {pct} vs data {c["frac_nonempty"]*100:.1f}')
    n=c['total_phantoms']
    if str(n) not in tex.replace('{,}','').replace(',',''):
        fails.append(f'{k}-view phantom count {n} absent')
if not ph['Phi0_empty_at_5_views']: fails.append('Phi0 not empty at 5 views but text claims it')

# 5. noise table + crossings
for tag in ('frozen','offaxis','tiled'):
    for s in n10['sigmas']:
        want(tex, f"{n10['per_cell'][f'{tag}_sig{s}']['mean_acc']:.4f}", f'noise {tag} sig={s}')
    cr=prd['measurements']['per_protocol'][tag]['observed_crossing_sigma']
    want(tex, f'{cr:.4f}', f'crossing sigma {tag}')
pf=n10['paired_frozen_vs_offaxis']
for s,exp in (('0.01','0.0015'),('0.02',None)):
    d=pf[s]
    want(tex, str(d['frozen_only']), f'paired frozen_only sig={s}')
    want(tex, str(d['offaxis_only']), f'paired offaxis_only sig={s}')

# 6. ladder at R1=1.0
b1=lad['by_reference']['1.0000']
want(tex, f"{b1['median_perception_share']*100:.1f}", 'median share pct')
want(tex, f"{b1['sign_test_p']:.4f}", 'sign test p')
want(tex, str(b1['S_gt_P_count']), 'S>P count')
for x in b1['bootstrap_ci95']: want(tex, f'{x:.3f}', 'bootstrap CI bound')
# exception must be described consistently with its actual rank
pm=b1['per_model']; byR4=sorted(pm,key=lambda m:-pm[m]['R4'])
exc=b1['exceptions_P_gt_S']
if len(exc)!=1: fails.append(f'expected 1 exception, data has {len(exc)}')
elif byR4.index(exc[0])!=1: fails.append(f'exception rank by R4 is {byR4.index(exc[0])+1}, text says second')

# 7. no stale claims
for bad,why in (('twenty-two structures','retracted tiling claim'),
                ('0.9952','retracted off-axis ceiling'),
                ('0.8476','retracted tiled ceiling'),
                ('$\\kappa = 1.77$','old kappa'),
                ('12 of 14 scored models','old ladder count')):
    if bad in tex: fails.append(f'stale: {why} ("{bad}")')

print(f'checks on {len(red)} chars of red-marked text')
if fails:
    print(f'FAIL ({len(fails)})')
    for f in fails: print('  -',f)
    sys.exit(1)
print('PASS — every revised value matches its checkpoint, with sample and tolerance correctly paired')
