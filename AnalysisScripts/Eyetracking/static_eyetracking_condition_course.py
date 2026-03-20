#!/usr/bin/env python3
"""
Load static-trial eyetracking for participants S01-S20 and plot average
eye position over experiment progression by condition.
"""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import mne

import eyetracking_preprocessing


# Update if your BIDS root is elsewhere.
BIDS_ROOT = Path("/Users/sm6511/Desktop/NIH_Experiment/Bids")
SUBJECTS = [f"S{i:02d}" for i in range(1, 21)]
SFREQ = 1200
EVENT_IDS = list(range(1, 18))
TMIN, TMAX = -1.0, 4.0
ANALYSIS_WINDOW = (0.0, 4.0)
N_PROGRESS_BINS = 10


def get_static_ds_paths(bids_root: Path, subj: str):
    """Return static task ds files (task-OrientationImagery, no Dynamic)."""
    meg_dir = bids_root / f"sub-{subj}" / "ses-1" / "meg"
    pattern = f"sub-{subj}_ses-1_task-OrientationImagery_run-*_meg.ds"
    return sorted(meg_dir.glob(pattern))


def events_file_from_ds(ds_path: Path):
    base = ds_path.name.replace("_meg.ds", "")
    return ds_path.parent / f"{base}_events.tsv"


def parse_condition(trial_type):
    """Match existing convention: condition from trial_type path-like string."""
    if pd.isna(trial_type):
        return "unknown"
    tt = str(trial_type)
    parts = tt.split("/")
    if len(parts) >= 3:
        return parts[2]
    return parts[-1] if parts else "unknown"


def load_run_epochs(ds_path: Path):
    """Preprocess eye data and epoch it around valid events."""
    eyes = eyetracking_preprocessing.process_run(str(ds_path))
    eye_df = eyes[["x_deg", "y_deg", "pupil"]].copy()

    info = mne.create_info(["x_deg", "y_deg", "pupil"], sfreq=SFREQ)
    raw_eye = mne.io.RawArray(eye_df.to_numpy().T, info, first_samp=0)

    raw_meg = mne.io.read_raw_ctf(
        str(ds_path), preload=False, system_clock="ignore", clean_names=True
    )
    events, _ = mne.events_from_annotations(raw_meg)
    events = events[np.isin(events[:, 2], EVENT_IDS)]

    events_tsv = events_file_from_ds(ds_path)
    metadata = None
    if events_tsv.exists():
        metadata = pd.read_csv(events_tsv, sep="\t")
        if len(metadata) >= len(events):
            metadata = metadata.iloc[: len(events)].reset_index(drop=True)
        else:
            events = events[: len(metadata)]
            metadata = metadata.reset_index(drop=True)

        if "trial_type" in metadata.columns:
            metadata["condition"] = metadata["trial_type"].apply(parse_condition)
        else:
            metadata["condition"] = "unknown"

    epochs = mne.Epochs(
        raw_eye,
        events,
        event_id=EVENT_IDS,
        tmin=TMIN,
        tmax=TMAX,
        baseline=(TMIN, 0.0),
        metadata=metadata,
        preload=True,
        reject_by_annotation=False,
    )
    return epochs


def add_progress_bin(df: pd.DataFrame, n_bins=10):
    out = df.copy()
    out["progress"] = out.groupby("subject")["trial_index_within_subject"].transform(
        lambda x: x / max(len(x) - 1, 1)
    )
    out["progress_bin"] = pd.cut(
        out["progress"],
        bins=np.linspace(0, 1, n_bins + 1),
        include_lowest=True,
        labels=[f"bin_{i + 1}" for i in range(n_bins)],
    )
    return out


def main():
    print("BIDS root:", BIDS_ROOT)
    print("Subjects:", SUBJECTS)

    rows = []
    missing_subjects = []

    for subj in SUBJECTS:
        ds_paths = get_static_ds_paths(BIDS_ROOT, subj)
        if len(ds_paths) == 0:
            missing_subjects.append(subj)
            continue

        subj_trial_counter = 0
        for run_idx, ds_path in enumerate(ds_paths, start=1):
            try:
                epochs = load_run_epochs(ds_path)
            except Exception as exc:
                print(f"[WARN] {subj} run-{run_idx:02d} failed: {exc}")
                continue

            analysis_epochs = epochs.copy().crop(*ANALYSIS_WINDOW)
            x_vals = np.nanmean(analysis_epochs.get_data(picks="x_deg"), axis=(1, 2))
            y_vals = np.nanmean(analysis_epochs.get_data(picks="y_deg"), axis=(1, 2))

            if epochs.metadata is not None and "condition" in epochs.metadata.columns:
                conds = epochs.metadata["condition"].astype(str).to_list()
            else:
                conds = ["unknown"] * len(x_vals)

            for i in range(len(x_vals)):
                rows.append(
                    {
                        "subject": subj,
                        "run": run_idx,
                        "trial_index_within_subject": subj_trial_counter + i,
                        "condition": conds[i],
                        "x_mean_deg": x_vals[i],
                        "y_mean_deg": y_vals[i],
                    }
                )

            subj_trial_counter += len(x_vals)

    summary_df = pd.DataFrame(rows)
    print("Loaded trials:", len(summary_df))
    print("Subjects with no static runs found:", missing_subjects)

    if summary_df.empty:
        raise RuntimeError("No data loaded. Check BIDS_ROOT and file naming.")

    plot_df = add_progress_bin(summary_df, n_bins=N_PROGRESS_BINS)
    agg = (
        plot_df.groupby(["condition", "progress_bin"], observed=True)[
            ["x_mean_deg", "y_mean_deg"]
        ]
        .mean()
        .reset_index()
    )

    bin_order = [f"bin_{i + 1}" for i in range(N_PROGRESS_BINS)]
    x_axis = np.arange(N_PROGRESS_BINS)
    conditions = sorted(agg["condition"].dropna().unique())

    fig, axes = plt.subplots(2, 1, figsize=(12, 10), sharex=True)

    for cond in conditions:
        cur = agg[agg["condition"] == cond].set_index("progress_bin").reindex(bin_order)
        axes[0].plot(x_axis, cur["x_mean_deg"].to_numpy(), marker="o", label=cond)
        axes[1].plot(x_axis, cur["y_mean_deg"].to_numpy(), marker="o", label=cond)

    axes[0].set_ylabel("Mean X position (deg)")
    axes[0].set_title("Average horizontal eye position over experiment progression")
    axes[0].axhline(0, color="k", linewidth=0.8, alpha=0.5)

    axes[1].set_ylabel("Mean Y position (deg)")
    axes[1].set_title("Average vertical eye position over experiment progression")
    axes[1].set_xlabel("Progress bin (early -> late trials)")
    axes[1].axhline(0, color="k", linewidth=0.8, alpha=0.5)

    axes[1].set_xticks(x_axis)
    axes[1].set_xticklabels(bin_order, rotation=45)

    for ax in axes:
        ax.legend(loc="upper right", fontsize=8, ncol=2)
        ax.grid(alpha=0.25)

    plt.tight_layout()
    plt.show()

    overall = (
        summary_df.groupby("condition")[["x_mean_deg", "y_mean_deg"]]
        .mean()
        .reset_index()
    )

    plt.figure(figsize=(8, 8))
    for _, row in overall.iterrows():
        plt.scatter(row["x_mean_deg"], row["y_mean_deg"], s=80)
        plt.text(row["x_mean_deg"], row["y_mean_deg"], str(row["condition"]))

    plt.axhline(0, color="k", linewidth=0.8, alpha=0.5)
    plt.axvline(0, color="k", linewidth=0.8, alpha=0.5)
    plt.xlabel("Overall mean X position (deg)")
    plt.ylabel("Overall mean Y position (deg)")
    plt.title("Condition-wise average gaze position (all subjects, static trials)")
    plt.grid(alpha=0.25)
    plt.show()

    print("\nCondition means (deg):")
    print(overall.sort_values("condition").to_string(index=False))


if __name__ == "__main__":
    main()
