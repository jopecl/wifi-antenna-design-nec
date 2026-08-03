"""Extract a frequency sweep summary from a NEC2 ``.out`` file.

A NEC output file repeats a full report — impedance loading, power budget and
the complete radiation pattern — for every frequency in the sweep. For the
Yagi-plus-reflector run that is 42 frequency points and about 15 MB of text,
almost all of it pattern samples that are not needed once the headline figures
are known.

This script walks the file once and pulls out, per frequency: the input
impedance at the feed, the power budget, and the maximum total gain over the
whole pattern. The result is a small CSV that can go in the repository in place
of the raw output.

Standard library only.

    python src/parse_nec_output.py data/YAGI_REFLECTOR.out -o data/yagi_reflector_sweep.csv
"""

import argparse
import csv
import re

FREQ_RE = re.compile(r'FREQUENCY\s*=\s*([\dEe.+-]+)\s*MHZ', re.I)
INPUT_POWER_RE = re.compile(r'INPUT POWER\s*=\s*([\dEe.+-]+)\s*WATTS', re.I)
RADIATED_RE = re.compile(r'RADIATED POWER\s*=\s*([\dEe.+-]+)\s*WATTS', re.I)
EFFICIENCY_RE = re.compile(r'EFFICIENCY\s*=\s*([\d.]+)\s*PERCENT', re.I)
# Radiation-pattern rows: theta, phi, vert dB, horiz dB, total dB, then more.
PATTERN_RE = re.compile(
    r'^\s*(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+'      # theta, phi
    r'(-?\d+\.\d+|-999\.99)\s+'                 # vertical gain
    r'(-?\d+\.\d+|-999\.99)\s+'                 # horizontal gain
    r'(-?\d+\.\d+|-999\.99)\s'                  # total gain
)
# Antenna input parameters table: tag, seg, then voltage/current/impedance pairs.
# NEC prints these in fixed-width columns and adjacent values frequently run
# together when one is negative (e.g. "1.61770E-02-1.36036E-03"), so the row is
# tokenised by matching each scientific-notation number rather than splitting on
# whitespace.
SCI_RE = re.compile(r'[-+]?\d+\.\d+[Ee][-+]?\d+')
INPUT_PARAM_HEAD_RE = re.compile(r'^\s*\d+\s+\d+\s+[-+]?\d+\.\d+[Ee]')


def parse(path):
    """Yield one dict per frequency block in the NEC output file."""
    rows = []
    current = None

    with open(path, encoding='utf-8', errors='replace') as fh:
        in_pattern = False
        for line in fh:
            m = FREQ_RE.search(line)
            if m:
                if current is not None:
                    rows.append(current)
                current = {
                    'frequency_mhz': float(m.group(1)),
                    'max_gain_db': None, 'max_gain_theta': None,
                    'max_gain_phi': None, 'input_power_w': None,
                    'radiated_power_w': None, 'efficiency_pct': None,
                    'impedance_real': None, 'impedance_imag': None,
                }
                in_pattern = False
                continue

            if current is None:
                continue

            if 'POWER GAINS' in line:
                in_pattern = True
                continue
            if 'ANTENNA INPUT PARAMETERS' in line:
                in_pattern = False
                continue

            for regex, key in ((INPUT_POWER_RE, 'input_power_w'),
                               (RADIATED_RE, 'radiated_power_w'),
                               (EFFICIENCY_RE, 'efficiency_pct')):
                m = regex.search(line)
                if m:
                    current[key] = float(m.group(1))

            if current['impedance_real'] is None and INPUT_PARAM_HEAD_RE.match(line):
                # voltage (2), current (2), impedance (2), admittance (2), power
                nums = SCI_RE.findall(line)
                if len(nums) >= 6:
                    current['impedance_real'] = float(nums[4])
                    current['impedance_imag'] = float(nums[5])

            if in_pattern:
                m = PATTERN_RE.match(line)
                if m:
                    total = float(m.group(5))
                    if total > -900 and (current['max_gain_db'] is None
                                         or total > current['max_gain_db']):
                        current['max_gain_db'] = total
                        current['max_gain_theta'] = float(m.group(1))
                        current['max_gain_phi'] = float(m.group(2))

    if current is not None:
        rows.append(current)
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('path', help="NEC2 .out file")
    ap.add_argument('-o', '--output', help="write a CSV here")
    args = ap.parse_args()

    rows = parse(args.path)
    fields = ['frequency_mhz', 'max_gain_db', 'max_gain_theta', 'max_gain_phi',
              'impedance_real', 'impedance_imag', 'input_power_w',
              'radiated_power_w', 'efficiency_pct']

    print("%-12s %-10s %-14s %s" % ("freq (MHz)", "gain (dB)", "Z (ohms)", "eff (%)"))
    for r in rows:
        z = ("%.1f%+.1fj" % (r['impedance_real'], r['impedance_imag'])
             if r['impedance_real'] is not None else "-")
        print("%-12.1f %-10s %-14s %s" % (
            r['frequency_mhz'],
            "%.2f" % r['max_gain_db'] if r['max_gain_db'] is not None else "-",
            z,
            "%.1f" % r['efficiency_pct'] if r['efficiency_pct'] is not None else "-"))

    if args.output:
        with open(args.output, 'w', newline='', encoding='utf-8') as fh:
            w = csv.DictWriter(fh, fieldnames=fields)
            w.writeheader()
            for r in rows:
                w.writerow(r)
        print("\nWrote %d rows to %s" % (len(rows), args.output))


if __name__ == '__main__':
    main()
