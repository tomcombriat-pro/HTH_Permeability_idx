# HTH_Permeability_idx


# Permeability Index from ND2 Time Series

This script computes fluorescence-based permeability indices from Nikon `.nd2` image time series. It supports manual placement of paired ROIs (inside/outside a vessel) or automatic ROI detection, image registration across time points, and line-profile fitting.

## Requirements

Python 3 with:

```bash
pip install numpy matplotlib nd2 scikit-image scipy tqdm colorama
```

The project also requires the local `src/` modules:

- `ROImaker`
- `ROI_filter`
- `ROIPairPicker`
- `LineUtils`
- `ImUtils`
- `FitUtils`

## Usage

```bash
python3 HTH_Permeability_idx.py path/to/experiment_t0min.nd2
```

The script finds matching `.nd2` files in the same folder. Files must share a basename and end with a time suffix such as:

```text
experiment_t0min.nd2
experiment_t5min.nd2
experiment_t10min.nd2
```

During processing, use the interactive windows to place or filter ROI pairs.

## Common options

```bash
python3 HTH_Permeability_idx.py experiment_t0min.nd2 \
  --size_roi 50 \
  --n_roi 2 \
  --auto_ROI False
```

| Option | Description | Default |
|---|---|---:|
| `--size_roi` | ROI radius in pixels | `50` |
| `--distance` | Gap between paired ROIs in pixels | `10` |
| `--n_roi` | Maximum ROI pairs per sub-image | `2` |
| `--auto_ROI` | Attempt automatic ROI detection | `False` |
| `--max_iter` | Maximum iterations for automatic ROI detection | `20` |
| `--upsample` | Registration upsampling factor | `1` |
| `--sanity_registering` | Save registration check images | `False` |

## Output

Results are written to:

```text
<dataset-folder>/res/<basename>/
```

Key outputs include:

- `*_table.txt` — permeability metrics over time
- `*_table_detail.txt` — command, registration shifts, and fit parameters
- `*_overviewROI_*.png` — selected ROI overlays
- `line_IMG*_time*.png` — line-profile fit plots
- `registering_IMG*.png` — optional registration previews
