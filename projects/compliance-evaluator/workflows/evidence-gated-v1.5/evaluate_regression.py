#!/usr/bin/env python3
"""Reuse the frozen quarantine-aware v1.4 evaluator for v1.5 terminal records."""
from __future__ import annotations
import importlib.util,sys
from pathlib import Path
W=Path(__file__).resolve().parent; P=W.parents[1]
S=importlib.util.spec_from_file_location('v14_evaluator',W.parent/'evidence-gated-v1.4'/'evaluate_regression.py')
if S is None or S.loader is None: raise RuntimeError('Could not load evaluator')
M=importlib.util.module_from_spec(S); S.loader.exec_module(M)
M.RESULTS_DIR=P/'results/evidence-gated-v1.5'; M.PREDICTIONS_PATH=M.RESULTS_DIR/'predictions.json'; M.EVALUATION_PATH=M.RESULTS_DIR/'evaluation.json'; M.COMPARISON_PATH=M.RESULTS_DIR/'regression-comparison.json'; M.REPORT_PATH=M.RESULTS_DIR/'README.md'; M.META_PATH=W/'workflow-v1.5.meta.json'
if __name__=='__main__':
    try: raise SystemExit(M.main())
    except Exception as e: print(f'ERROR: {e}',file=sys.stderr); raise SystemExit(1)
