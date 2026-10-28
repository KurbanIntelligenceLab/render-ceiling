# Reproducibility guide

The [results map](results/README.md) links every figure and table to its finished output and supporting data.

## Python API

```python
from render_ceiling import ReconstructionInput, Reconstructor

inputs = ReconstructionInput.from_json("examples/silicon_projections.json")
result = Reconstructor(method="atomic").run(inputs)
print(result.selected_configuration)
print(result.prediction["cart"])
print(result.prediction["label"])
# result.to_dict() and result.to_json() serialize NumPy values.
```

`ReconstructionInput(observations, cameras, lattice)` also accepts arrays directly. It validates five finite orthonormal cameras, a nonsingular lattice, complete species-labelled views and three-dimensional observability in each held-out fold. Every view must have the same species counts. The [example input](examples/silicon_projections.json) is a small ideal silicon demonstration. All positions and lattice entries use angstroms.

`Reconstructor` accepts `atomic`, `collective` and `huber`; its result contains `method`, `selected_configuration`, `prediction` and `diagnostics`. Atomic reconstruction uses the paper's paired one-SE selector; collective reconstruction selects `atom_or_mode_split`; the Huber comparator reports `huber_adaptive_6`. Diagnostics retain the underlying candidate outputs and selection records. The CLI uses this same interface:

```sh
uv run render-ceiling reconstruct examples/silicon_projections.json --method atomic --output development/prediction.json
```

## Numerical implementations

| Implementation | Purpose |
|---|---|
| [reconstruct.py](src/render_ceiling/reconstruct.py) | Ideal geometric reference and camera matrices |
| [render.py](src/render_ceiling/render.py) | Conventional cells and benchmark rendering |
| [correspondence.py](src/render_ceiling/correspondence.py) | Species-constrained correspondence and symmetry proposals |
| [symmetry_spaces.py](src/render_ceiling/symmetry_spaces.py) | Symmetry-consistent affine spaces |
| [atomic_reconstruction.py](src/render_ceiling/atomic_reconstruction.py) | Atomic decomposition and withheld-view fits |
| [support_refit.py](src/render_ceiling/support_refit.py) | Residual-checked solver and joint support refit |
| [penalty_selection.py](src/render_ceiling/penalty_selection.py) | Paired one-SE, fixed-four and null-guard selectors |
| [robust_triangulation.py](src/render_ceiling/robust_triangulation.py) | Huber comparator |
| [collective_reconstruction.py](src/render_ceiling/collective_reconstruction.py) | Symmetry modes and localized-or-collective selection |

Reconstruction inputs are a list of observation dictionaries with `xy` (N by 2 Cartesian centroids) and `species` (N atomic numbers), a V by 3 by 3 camera array, and a 3 by 3 lattice matrix. Each camera's first two columns give its projection: `cart @ camera[:, :2]`. Observation order can differ between views. Reference coordinates and intervention labels are used only in evaluation records.

`atomic_reconstruction.predict(observations, cameras, lattice)` returns candidate outputs and fold losses. `penalty_selection.choose(result)` selects the primary `paired_1se` configuration. `collective_reconstruction.predict(observations, cameras, lattice)` returns atomic, mode and combined outputs, including `atom_or_mode_split`.

The frozen numerical routines retain their arithmetic and stopping rules; their imports have been consolidated into the package. [Tests](tests/) exercise geometric recovery, departure/error separation and penalty selection.

The [atomic schedule](results/symmetry_selector_refinement/schedule.json), [dataset](results/symmetry_selector_refinement/dataset.json) and [selection](results/symmetry_selector_refinement/selection.json) describe the reserved evaluation. External cohort structures, schedules, raw outputs and analysis roles are stored together in the [first](results/collective_validation/study.json) and [second](results/mode_replication/study.json) cohort records. The [support-refit record](results/physical_readout/study.json) reuses the atomic cohort.

The [diagnostic release guide](release/README.md) identifies prompts, API model identifiers, exact-text inputs and saved predictions. [Primary](data/primary/) and [replication](data/replication/) directories contain structure and split manifests; [certification](data/certification/) contains the additional geometric census structures.

Result records are scoped to the reported evaluations. The `release_scope` metadata identifies the paper items, the original record checksum and the selection applied to each trimmed record. Retained predictions and numerical values are unchanged. External-cohort `analysis` contains the independently verified five-pipeline scores used in Tables 2, S4 and S5.
