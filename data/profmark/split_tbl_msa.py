#!/usr/bin/env python3
"""
Split a HMMER profmark .tbl + .train.msa into per-MSA Stockholm files.

Only MSAs with status 'ok' in the .tbl file are extracted.
Each alignment is written to <output_dir>/<msa_name>.sto using esl-afetch.
"""

import argparse
import os
import subprocess
import sys


def parse_args():
    p = argparse.ArgumentParser(
        description="Extract 'ok' MSAs from a profmark .tbl + .train.msa pair."
    )
    p.add_argument("tbl",  help="Path to the profmark .tbl file")
    p.add_argument("msa",  help="Path to the profmark .train.msa (Stockholm) file")
    p.add_argument(
        "-o", "--outdir",
        required=True,
        help="Output directory for individual .sto files",
    )
    p.add_argument(
        "--esl-afetch",
        default="esl-afetch",
        metavar="PATH",
        help="Path to the esl-afetch executable (default: esl-afetch)",
    )
    return p.parse_args()


def read_ok_msas(tbl_path):
    """Return a list of MSA names whose status field equals 'ok'."""
    ok_names = []
    with open(tbl_path) as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            # Strip inline comments ('; ...')
            if ";" in line:
                line = line[:line.index(";")]
            fields = line.split()
            # Field indices: 0=name, 1=nseq, 2=alen, 3=nfrag, 4=avg_pid,
            #                5=avg_conn, 6=ntries, 7=status, ...
            if len(fields) < 8:
                continue
            if fields[7] == "ok":
                ok_names.append(fields[0])
    return ok_names


def extract_msas(esl_afetch, msa_path, msa_names, outdir):
    """Run esl-afetch for each name and write to outdir/<name>.sto."""
    ok = 0
    fail = 0
    for name in msa_names:
        out_path = os.path.join(outdir, name + ".sto")
        cmd = [esl_afetch, msa_path, name]
        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
            )
        except subprocess.CalledProcessError as exc:
            print(
                f"WARNING: esl-afetch failed for '{name}': "
                f"{exc.stderr.decode().strip()}",
                file=sys.stderr,
            )
            fail += 1
            continue

        with open(out_path, "wb") as fh:
            fh.write(result.stdout)
        ok += 1

    return ok, fail


def main():
    args = parse_args()

    os.makedirs(args.outdir, exist_ok=True)

    print(f"Reading .tbl: {args.tbl}")
    ok_msas = read_ok_msas(args.tbl)
    print(f"  Found {len(ok_msas)} MSA(s) with status 'ok'")

    if not ok_msas:
        print("Nothing to do.", file=sys.stderr)
        sys.exit(0)

    print(f"Extracting from: {args.msa}")
    print(f"Output directory: {args.outdir}")
    extracted, failed = extract_msas(args.esl_afetch, args.msa, ok_msas, args.outdir)
    print(f"Done: {extracted} extracted, {failed} failed.")


if __name__ == "__main__":
    main()
