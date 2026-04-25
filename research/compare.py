"""
Batch runner: simulate a list of RunConfigs and return a tidy comparison table.

Usage:
    from compare import run_set
    rows = run_set(configs)   # list[RunConfig]
    print(rows)               # pd.DataFrame, one row per config
"""
from __future__ import annotations

import pandas as pd

from model_config import RunConfig
from simulator import simulate
from metrics import compute_metrics


def run_set(configs: list[RunConfig]) -> pd.DataFrame:
    """Run each config, compute metrics, return one-row-per-config DataFrame.

    Columns: label + all keys returned by compute_metrics().
    """
    rows = []
    for cfg in configs:
        df = simulate(cfg)
        m  = compute_metrics(df, cfg)
        rows.append({"label": cfg.label, **m})
    return pd.DataFrame(rows).set_index("label")
