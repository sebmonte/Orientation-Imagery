import mne, os
import numpy as np
import matplotlib

subjects = subjects = [f"S{i:02}" for i in range(1, 21)]
for subject in subjects:
    subjid = subject
    bids_top_dir = '/System/Volumes/Data/misc/data12/sjapee/Sebastian-OrientationImagery/Data/Bids/'
    bids_dir = bids_top_dir.rstrip('/')
    save_path = '/System/Volumes/Data/misc/data12/sjapee/Sebastian-OrientationImagery/Data/Bids/derivatives/preprocessed/ICA-Removed'

    for run_nr in range(1, 5):
        run_str = f'run-{str(run_nr).zfill(2)}'
        base_name = f'sub-{subjid}_ses-1_task-OrientationImagery_run-{str(run_nr).zfill(2)}'
        raw_fn = f'{bids_dir}/sub-{subjid}/ses-1/meg/{base_name}.ds'

        preproc_path = f"{bids_dir}/derivatives/preprocessed/ICA/{base_name}"
        print(preproc_path)
        raw = mne.io.read_raw_fif(f"{preproc_path}_step1a-raw.fif", preload=True)
        ica = mne.preprocessing.read_ica(f"{preproc_path}_step1a-ica.fif")
        ica.plot_components()
        input("Hit any button to continue")
        ica.plot_sources(raw, show_scrollbars=False)
        input("Hit any button to continue")

        ica.apply(raw)
        print(f'RUN: {run_nr}, REMOVED: {ica.exclude}')
        ica.save(f"{save_path}/sub-{subjid}_ses-1_task-OrientationImagery_run-{str(run_nr).zfill(2)}_step1b-ica.fif", overwrite=True)
        raw.save(f"{save_path}/sub-{subjid}_ses-1_task-OrientationImagery_run-{str(run_nr).zfill(2)}_step1b-raw.fif", overwrite=True)
    
