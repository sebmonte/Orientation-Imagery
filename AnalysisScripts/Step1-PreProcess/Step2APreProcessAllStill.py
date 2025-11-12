import mne
import pandas as pd
import numpy as np
import glob
import pylab
import pandas as pd
import pickle
import matplotlib.pyplot as plt
import os
#*****************************#
### PARAMETERS ###
#*****************************#
pre_stim_time               = -.2
post_stim_time              = .6
#Assign location of bids folder
bids_top_dir = '/System/Volumes/Data/misc/data12/sjapee/Sebastian-OrientationImagery/Data/Bids/'
raw_ICA_path = bids_top_dir + 'derivatives/preprocessed/ICA-Removed'
output_evoked_folder = '/System/Volumes/Data/misc/data12/sjapee/Sebastian-OrientationImagery/!Important Data/evoked'
save_evoked = False
event_id = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
subjects = [f"S{i:02}" for i in range(1, 21)]
for S in subjects:
    print('Processing Subject...', S)
    stim_duration = .3
    run_length = 4
    first_run_file = 1
    last_run_file = 4
    bids_dir = bids_top_dir + f'bids_dir/sub-{S}/ses-1/meg/sub-{S}_ses-1_task-OrientationImagery'


    dsets = []
    for i in range(1, 5):
        pattern = f'{raw_ICA_path}/sub-{S}_ses-1_task-OrientationImagery_run-{i:02}_step1b-raw.fif'
        matches = glob.glob(pattern)
        
        if matches:
            dsets.append(matches[0])
        else:
            print(f"No files found for pattern: {pattern}")
    all_epochs = []
    all_events = []
    for i in dsets:
        raw = mne.io.read_raw_fif(i)
        events = mne.events_from_annotations(raw)[0]
        epochs = mne.Epochs(raw, events, event_id=event_id,tmin=pre_stim_time, tmax=post_stim_time, preload=True, baseline=(None,0), picks = 'mag')
        print("Number of events:", len(events))
        print("Number of epochs:", len(epochs))
        print(np.nonzero(list(map(len, epochs.drop_log)))[0])
        [n for n, dl in enumerate(epochs.drop_log) if len(dl)]
        all_epochs.append(epochs)
        all_events.append(events)
    pattern = f'{bids_dir}*events.tsv'  # Find all event files in bids directory
    matches = glob.glob(pattern)

    matches.sort()
    print(matches)

    out = []

    for event_files in matches[4:]:
        out.append(pd.read_csv(event_files,sep='\t'))
    all_metadata = pd.concat(out).reset_index(drop=True)

    all_metadata
    dev_head_t_ref = all_epochs[0].info['dev_head_t']
    for i in range(0, 4):
        all_epochs[i].info['dev_head_t'] = dev_head_t_ref
    epochs_stacked = mne.concatenate_epochs(all_epochs)
    epochs_stacked.metadata = all_metadata
    evoked = epochs_stacked.average()
    if evoked:
        plt.savefig(f'output_evoked_folder')

    ###Create metadata###
    runs = [all_epochs[0], all_epochs[1], all_epochs[2], all_epochs[3]]  
    # Get number of trials in each run
    run_lengths = [len(r) for r in runs]
    # Create run number array that matches the actual number of trials per run
    run_nr = np.concatenate([[i] * l for i, l in enumerate(run_lengths)])
    # Assign run numbers to metadata
    epochs_stacked.metadata['run_nr'] = run_nr
    block_type = [k.split('/')[1] for k in epochs_stacked.metadata.trial_type]
    print(block_type)
    condition = [k.split('/')[2] for k in epochs_stacked.metadata.trial_type]
    epochs_stacked.metadata['block_type'] = block_type
    epochs_stacked.metadata['condition'] = condition
    file_name = f'sub-{S}_Still_preprocessed-epo.fif'
    directory = f'{bids_top_dir}/derivatives/preprocessed/'
    os.makedirs(directory, exist_ok=True)
    # Save
    #epochs_stacked.save(f'{directory}{file_name}', overwrite=True)




