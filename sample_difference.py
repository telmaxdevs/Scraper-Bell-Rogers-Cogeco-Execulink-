#!/usr/bin/env python3
"""Sample k random unique rows from a CSV using reservoir sampling.

Writes the sampled rows (preserves header) to an output CSV.

Usage: python sample_difference.py --input difference.csv --k 12000 --output sample_difference_12000.csv
"""
import argparse
import csv
import random
from typing import List


def reservoir_sample_csv(input_path: str, k: int) -> List[List[str]]:
    """Return a list of k sampled rows (each row is a list of strings)."""
    reservoir: List[List[str]] = []
    with open(input_path, newline='', encoding='utf-8', errors='replace') as f:
        reader = csv.reader(f)
        # Read header separately
        try:
            header = next(reader)
        except StopIteration:
            return []

        # Reservoir sampling on the remaining rows
        for i, row in enumerate(reader):
            if i < k:
                reservoir.append(row)
            else:
                j = random.randint(0, i)
                if j < k:
                    reservoir[j] = row

    return [header] + reservoir


def main() -> None:
    parser = argparse.ArgumentParser(description='Sample k unique rows from a CSV (reservoir sampling)')
    parser.add_argument('--input', '-i', default='difference.csv', help='Input CSV path')
    parser.add_argument('--k', '-k', type=int, default=12000, help='Number of unique rows to sample')
    parser.add_argument('--output', '-o', default='sample_difference_12000.csv', help='Output CSV path')
    parser.add_argument('--seed', type=int, default=None, help='Optional random seed for reproducibility')

    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    print(f"Reading from: {args.input}")
    print(f"Sampling k={args.k} rows (unique) using reservoir sampling...")

    # We'll stream the file and sample rows
    # Separate header handling: rewrite header into output
    # Implemented in a memory-friendly way: reservoir holds at most k rows

    # Open input and do reservoir sampling while preserving header
    reservoir: List[List[str]] = []
    header = None
    n_rows = 0
    with open(args.input, newline='', encoding='utf-8', errors='replace') as inf:
        reader = csv.reader(inf)
        try:
            header = next(reader)
        except StopIteration:
            print('Input CSV is empty. Nothing to do.')
            return

        for i, row in enumerate(reader):
            n_rows += 1
            if i < args.k:
                reservoir.append(row)
            else:
                j = random.randint(0, i)
                if j < args.k:
                    reservoir[j] = row

    out_count = min(args.k, n_rows)
    print(f"Total data rows in file: {n_rows}")
    print(f"Writing {out_count} sampled rows to {args.output}")

    with open(args.output, 'w', newline='', encoding='utf-8') as outf:
        writer = csv.writer(outf)
        writer.writerow(header)
        writer.writerows(reservoir[:out_count])

    print('Done.')


if __name__ == '__main__':
    main()
