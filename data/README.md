# Data

## Included

| File | What it is |
|---|---|
| `yagi_reflector_sweep.csv` | 42 rows extracted from the NEC2 output: an initial 2400 MHz impedance-only run, then a 41-point sweep from 2100 to 2700 MHz in 15 MHz steps. Columns: max gain and its direction, feed impedance, power budget, efficiency. The first row has no gain because that block contains no radiation pattern. |
| `lab1-measurements.xlsx` | VNA measurements for the dipole and Yagi-Uda builds |
| `lab2-measurements.xlsx` | VNA measurements for the PIFA build |

## Excluded (gitignored)

| File | Size | Why |
|---|---:|---|
| `YAGI_REFLECTOR.out` | 15.6 MB | Raw NEC2 output — the full radiation pattern at all 42 frequencies. The CSV above carries everything actually used. |
| `cal_antenna.cal` | 5.2 MB | VNA calibration file, specific to the instrument and session; meaningless elsewhere. |

To regenerate the summary from a raw NEC output:

```bash
python src/parse_nec_output.py path/to/YAGI_REFLECTOR.out -o data/yagi_reflector_sweep.csv
```
