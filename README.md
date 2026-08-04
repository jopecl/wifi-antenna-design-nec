# 2.4 GHz Wi-Fi Antenna Design — NEC2 models, optimisation and measurement

Four antennas designed for the 2.4 GHz Wi-Fi band, simulated in NEC2, numerically
optimised, 3D-printed, built and then measured on a VNA. Radiocommunications
coursework, 3rd year, Universitat Pompeu Fabra (2025).

The four are **different antennas, not iterations of one design** — a half-wave
dipole, a Yagi-Uda array, a PIFA, and a Yagi with a parabolic reflector — each
chosen to illustrate a different trade-off between gain, size and bandwidth.

## What is here

The `.nec` files are the real deliverable. They are plain-text NEC2 models:
`SY` lines declare symbolic dimensions in metres, `GW` lines place wires, `FR`
sets the frequency, `EX` the excitation. They are readable directly and are
what the optimiser mutated.

## The four designs

### 1. Half-wave dipole — `models/01-dipole/`

The reference case. Three variants (`dipole-01/02/03.NEC`) establishing the
baseline resonant length at 2.4 GHz (λ = 0.125 m).

### 2. Yagi-Uda array — `models/02-yagi-uda/`

A driven element with one reflector behind it and three directors in front,
each an 11-segment wire. The optimiser was allowed to move the element lengths
and spacings.

**Final design (`yagi-opt3-jose.nec`), all dimensions in metres:**

| Parameter | Value | Meaning |
|---|---:|---|
| `LA` | 0.054163 | driven element length |
| `LR` | 0.057543 | reflector length (longest — it must be inductive) |
| `LD` | 0.050129 | director length (shortest — capacitive) |
| `deltaR` | 0.027018 | driven-to-reflector spacing |
| `deltaD` | 0.027037 | director-to-director spacing |
| `R` | 0.001 | wire radius |

The length ordering reflector > driven > director is the textbook Yagi
condition, and the optimiser converged to it from a symmetric start.

**Optimiser result** (`optimizer-logs/lab1-yagi-Optimizer.log`, final run):

| SWR | R<sub>a</sub> | X<sub>a</sub> | Efficiency |
|---:|---:|---:|---:|
| **1.4102** | 68.872 Ω | −7.396 Ω | 100 % |

The log shows the search rejecting a bad excursion early (run 1-2 hit SWR
2.7124 at R = 50.395 Ω) before settling; the step size shrinks from 10 % to
0.02 % as it converges.

### 3. PIFA — `models/03-pifa/`

A planar inverted-F antenna: a folded, ground-plane-backed structure with a
much smaller footprint than the dipole, at the cost of bandwidth. Modelled as a
wire grid, `NL` × `NW` cells.

**Final design (`PIFA_optimized3.nec`):**

| Parameter | Value | Meaning |
|---|---:|---|
| `DW` | 4.24 mm | grid cell width |
| `DL` | 3.227 mm | grid cell length |
| `NL` × `NW` | 10 × 6 | grid divisions (L = 32.3 mm, W = 25.4 mm) |
| `H` | 9.985 mm | height above ground plane |

**Optimiser result** (`optimizer-logs/lab2-pifa-Optimizer.log`, final run):

| SWR | R<sub>a</sub> | X<sub>a</sub> | Efficiency |
|---:|---:|---:|---:|
| **1.0286** | 51.079 Ω | 0.930 Ω | 100 % |

This is a near-perfect match — 51.1 Ω against a 50 Ω feed with essentially zero
reactance. The PIFA optimised far better than the Yagi did (SWR 1.03 vs 1.41)
because the optimiser had three free geometric parameters interacting locally,
whereas the Yagi's element spacings trade impedance match against directivity.

The intermediate files (`PIFA_manualcut`, `PIFA_manualcut2`,
`PIFA_frequencyscaled2`, `2.2`, `3`) record the design path: manual cut-and-try
first, then frequency scaling, then numerical optimisation.

### 4. Yagi with parabolic reflector — `models/04-yagi-reflector/`

The Yagi placed at the focus of a parabolic reflector, for maximum gain.
This is the only design with a full simulated frequency sweep.

**Measured from the NEC2 sweep** (`data/yagi_reflector_sweep.csv`): the file
holds 42 frequency blocks — one initial single-frequency run at 2400 MHz that
records impedance only and no radiation pattern, followed by a **41-point sweep
from 2100 to 2700 MHz in 15 MHz steps**. The gain figures below come from the
41-point sweep.

| | |
|---|---|
| **Peak gain** | **15.69 dBi** at 2325–2340 MHz |
| Gain at 2400 MHz (Wi-Fi) | **15.43 dBi** |
| Feed impedance at 2400 MHz | 61.4 + 5.2j Ω |
| Efficiency | 100 % across the whole sweep (no loss modelled) |
| −3 dB gain bandwidth | roughly 2205 → 2460 MHz (≈ 255 MHz) |

The design peaks slightly *below* the Wi-Fi band, costing 0.26 dB at 2400 MHz —
worth noting as a real imperfection rather than glossing over. Above 2460 MHz
the gain collapses hard (13.85 dB at 2460, 9.54 dB at 2505) as the reactance
runs away (+48j at 2505 MHz). The reactance crosses zero near 2220 MHz and
again near 2415 MHz, the two resonances of the coupled structure.

Adding the reflector takes the array from a Yagi's typical ~10 dBi to 15.7 dBi.

## Structure

```
models/
  01-dipole/           3 dipole variants
  02-yagi-uda/         base, frequency-scaled, and 3 optimiser outputs
  03-pifa/             10 PIFA variants, manual → scaled → optimised
  04-yagi-reflector/   Yagi, Yagi+reflector, frequency-scaled
optimizer-logs/        raw optimiser logs + .opt/.ref parameter files
hardware/              STL and STP files actually sent to the 3D printer
  yagi-uda-mount.stl, extensió_antena.stl, nut_bolt_washer.stl, PIFA.stl/.stp
data/                  extracted sweep CSV + VNA measurement spreadsheets
src/parse_nec_output.py   NEC2 .out → frequency sweep CSV (stdlib only)
notebooks/             drawings.ipynb (FreeCAD geometry), plots.ipynb (measurements)
docs/                  the three lab reports + manufacturer datasheets
```

## How to run

```bash
# Re-extract the sweep summary from a raw NEC2 output (no dependencies):
python src/parse_nec_output.py path/to/YAGI_REFLECTOR.out -o data/sweep.csv
```

To re-simulate, load any `.nec` file into a NEC2 engine (4nec2, xnec2c,
nec2c). To regenerate the printable geometry, run `notebooks/drawings.ipynb`
**inside FreeCAD** — it imports `FreeCAD`, `Part`, `Mesh` and `TechDraw`, which
only exist in FreeCAD's bundled Python, not in a normal venv.

## Authors

- José Mª Pérez Clar

Manufacturer datasheets under `docs/` are third-party. The NEC2 dipole example
that these models were derived from is Radiocommunications course material, UPF.
