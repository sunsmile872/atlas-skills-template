#!/usr/bin/env python3
"""Deterministic clinical sample size calculator across small-N and prevalence study designs."""

from __future__ import annotations

import argparse
import math
import sys

Z_ALPHA = {0.10: 1.6449, 0.05: 1.9600, 0.01: 2.5758}
Z_POWER = {0.80: 0.8416, 0.85: 1.0364, 0.90: 1.2816}


def get_zs(alpha: float, power: float) -> tuple[float, float]:
    za = Z_ALPHA.get(round(alpha, 2))
    zb = Z_POWER.get(round(power, 2))
    if za is None or zb is None:
        raise ValueError(f"Supported alpha={list(Z_ALPHA)}, power={list(Z_POWER)}")
    return za, zb


def with_buffer(n: int, dropout: float) -> int:
    return math.ceil(n * (1.0 + dropout))


def auc_se(auc: float, n_pos: int, n_neg: int) -> float:
    q1 = auc / (2.0 - auc)
    q2 = (2.0 * auc ** 2) / (1.0 + auc)
    var = (auc * (1.0 - auc) + (n_pos - 1) * (q1 - auc ** 2) + (n_neg - 1) * (q2 - auc ** 2)) / (n_pos * n_neg)
    return math.sqrt(var)


def main() -> int:
    ap = argparse.ArgumentParser(description="Sample size calculator for clinical study designs.")
    sub = ap.add_subparsers(dest="mode", required=True)

    p_corr = sub.add_parser("correlation", help="Fisher's z correlation sample size")
    p_corr.add_argument("--r", type=float, required=True, help="Expected correlation coefficient (0 < r < 1)")
    p_corr.add_argument("--alpha", type=float, default=0.05)
    p_corr.add_argument("--power", type=float, default=0.80)
    p_corr.add_argument("--dropout", type=float, default=0.10)

    p_pair = sub.add_parser("paired", help="Paired / Crossover study")
    p_pair.add_argument("--dz", type=float, required=True, help="Paired Cohen's d_z")
    p_pair.add_argument("--alpha", type=float, default=0.05)
    p_pair.add_argument("--power", type=float, default=0.80)
    p_pair.add_argument("--dropout", type=float, default=0.15)
    p_pair.add_argument("--crossover", action="store_true", help="Round final N up to an even number for 1:1 AB/BA crossover balance")

    p_two = sub.add_parser("two-arm", help="Two independent groups (equal size)")
    p_two.add_argument("--d", type=float, required=True, help="Cohen's d")
    p_two.add_argument("--alpha", type=float, default=0.05)
    p_two.add_argument("--power", type=float, default=0.80)
    p_two.add_argument("--dropout", type=float, default=0.10)

    p_prev = sub.add_parser("prevalence", help="Cochran single proportion (+/- Finite Population Correction)")
    p_prev.add_argument("--p", type=float, required=True, help="Expected prevalence (0 < p < 1)")
    p_prev.add_argument("--d", type=float, default=0.08, help="Margin of error (default 0.08)")
    p_prev.add_argument("--pool", type=int, default=0, help="Finite clinic population M (0 = infinite)")
    p_prev.add_argument("--dropout", type=float, default=0.10)

    p_auc = sub.add_parser("auc", help="Hanley & McNeil ROC AUC power check")
    p_auc.add_argument("--auc", type=float, required=True, help="Target AUC (> 0.5)")
    p_auc.add_argument("--p", type=float, required=True, help="Expected positive prevalence")
    p_auc.add_argument("--n", type=int, required=True, help="Candidate total N")

    p_epv = sub.add_parser("epv", help="Peduzzi EPV >= 10 minimum N check for logistic regression")
    p_epv.add_argument("--predictors", type=int, required=True)
    p_epv.add_argument("--p", type=float, required=True, help="Event prevalence")
    p_epv.add_argument("--epv", type=int, default=10)

    args = ap.parse_args()

    if args.mode == "correlation":
        za, zb = get_zs(args.alpha, args.power)
        c = 0.5 * math.log((1.0 + args.r) / (1.0 - args.r))
        n_raw = ((za + zb) / c) ** 2 + 3.0
        n0 = math.ceil(n_raw)
        nf = with_buffer(n0, args.dropout)
        print(f"Mode: Correlation (Fisher z) | r={args.r}, alpha={args.alpha}, power={args.power}")
        print(f"  C = {c:.4f} | N_raw = {n_raw:.2f} -> N0 = {n0} | +{int(args.dropout*100)}% buffer = {nf}")

    elif args.mode == "paired":
        za, zb = get_zs(args.alpha, args.power)
        n_raw = ((za + zb) / args.dz) ** 2 + 2.0
        n0 = math.ceil(n_raw)
        nf = with_buffer(n0, args.dropout)
        crossover_note = ""
        if args.crossover:
            if nf % 2 == 1:
                nf += 1
                crossover_note = f" -> Rounded to even for 1:1 AB/BA = {nf} ({nf//2} AB / {nf//2} BA)"
            else:
                crossover_note = f" (even 1:1: {nf//2} AB / {nf//2} BA)"
        print(f"Mode: {'2x2 Crossover' if args.crossover else 'Paired / Crossover'} | dz={args.dz}, alpha={args.alpha}, power={args.power}")
        print(f"  N_raw = {n_raw:.2f} -> N0 = {n0} | +{int(args.dropout*100)}% buffer = {with_buffer(n0, args.dropout)}{crossover_note}")

    elif args.mode == "two-arm":
        za, zb = get_zs(args.alpha, args.power)
        n_arm_raw = 2.0 * ((za + zb) / args.d) ** 2 + 1.0
        n_arm = math.ceil(n_arm_raw)
        total0 = 2 * n_arm
        total_buf = 2 * with_buffer(n_arm, args.dropout)
        print(f"Mode: Two-Arm Parallel | d={args.d}, alpha={args.alpha}, power={args.power}")
        print(f"  n/arm = {n_arm} (Total N0 = {total0}) | +{int(args.dropout*100)}% buffer = {total_buf} ({total_buf//2}/arm)")

    elif args.mode == "prevalence":
        za = Z_ALPHA[0.05]
        n_raw = (za ** 2 * args.p * (1.0 - args.p)) / (args.d ** 2)
        n0 = math.ceil(n_raw)
        if args.pool > 0:
            n_fpc = math.ceil(n0 / (1.0 + (n0 - 1.0) / args.pool))
            print(f"Mode: Prevalence + FPC | p={args.p}, d={args.d}, pool M={args.pool}")
            print(f"  Infinite N0 = {n0} -> FPC N = {n_fpc} | +{int(args.dropout*100)}% buffer = {with_buffer(n_fpc, args.dropout)}")
        else:
            print(f"Mode: Prevalence (Cochran) | p={args.p}, d={args.d}")
            print(f"  N_raw = {n_raw:.2f} -> N0 = {n0} | +{int(args.dropout*100)}% buffer = {with_buffer(n0, args.dropout)}")

    elif args.mode == "auc":
        n_pos = round(args.n * args.p)
        n_neg = args.n - n_pos
        se0 = auc_se(0.50, n_pos, n_neg)
        se1 = auc_se(args.auc, n_pos, n_neg)
        z_pow = (args.auc - 0.50 - 1.96 * se0) / se1
        print(f"Mode: ROC AUC Power (Hanley & McNeil) | N={args.n} (pos={n_pos}, neg={n_neg}), AUC={args.auc}")
        print(f"  z_power = {z_pow:.2f} (>= 0.84 is >= 80% power)")

    elif args.mode == "epv":
        min_events = args.predictors * args.epv
        min_n = math.ceil(min_events / args.p)
        print(f"Mode: Peduzzi EPV | predictors={args.predictors}, EPV>={args.epv}, p={args.p}")
        print(f"  Min events = {min_events} -> Min total N = {min_n}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
