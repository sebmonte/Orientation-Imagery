import mne, glob
import os, os.path as op
import pandas as pd
import numpy as np
from hv_proc.utilities import mrk_template_writer
import datetime
import argparse

def log_print_statements(print_statements, logfile_path):
    current_datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Ensure the directory exists
    os.makedirs(os.path.dirname(logfile_path), exist_ok=True)

    # Open the file in append mode, creating it if it doesn't exist
    with open(logfile_path, 'a') as file:
        file.write(f'\nPrep bids at {current_datetime}:\n')
        for statement in print_statements:
            file.write(statement + '\n')
def get_dsets(top_dir):

    dsets = glob.glob(op.join(top_dir,'*Team*.ds'))
    dsets = sorted([i for i in dsets])

    return dsets

def setup_and_load(raw_path, logfile_path):
    raw = mne.io.read_raw_ctf(raw_path,system_clock='ignore',preload=False)
    raw.load_data()

    beh = pd.read_csv(logfile_path)
    return raw, beh

def find_events(raw, log_statements=[]):
    events = mne.find_events(raw, stim_channel='UPPT001',initial_event=False,min_duration = 0.0015)
    # get rid of events that are  the rest-period

    # remove trailing zeros
    raw.crop(0,raw.times[events[-1,0]]+10)

    ## replacing parallel port onsets with photo diode
    pd_dat = raw[raw.ch_names.index('UADC016-2104')][0][0]
    import matplotlib.pyplot as plt
    plt.plot(pd_dat)

    # if np.max(np.abs(pd_dat))>2:  # good idea but does not work if the pd worked for half a run
    if np.mean(np.abs(pd_dat))>0.6: # this should be fine but may not be good if there are a looot of zeros
        # zero-centering & making everything positive
        pd_dat = np.abs(pd_dat-np.mean(pd_dat[0:100]))
        # scaling channel to 0-1
        pd_dat = (pd_dat-np.min(pd_dat)) / (np.max(pd_dat)-np.min(pd_dat))
        plt.plot(pd_dat)
        plt.savefig(f"pd_dat_plot{run}.png", format="png", dpi=300)
        # using the event, we are now looking in the next 50ms of the photodiode channel (digital) when the signal goes above 0.5
        t_samples = int(0.05/(1/raw.info['sfreq']))
        threshold =  .5
        # when we found the events we calculate the trigger delay. 
        try:
            pd_events = [events[i,0]+np.where(pd_dat[events[i,0]:events[i,0]+t_samples]<threshold)[0][0] for i in range(len(events))]
        except:
            pd_events = [events[i,0]+np.where(pd_dat[events[i,0]:events[i,0]+t_samples]>threshold)[0][0] for i in range(len(events))]

        # plt.plot(pd_dat)
        # [plt.plot(i,0,'r*') for i in pd_events]
        # [plt.plot(i,0.01,'g*') for i in events[:,0]]
        # plt.show()


        print(pd_events)
        trigger_delay = 1000. * (pd_events-events[:, 0]) / raw.info['sfreq']

        # sometimes this channel records ON as UP and sometimes as DOWN. This if-loop makes sure we always find the onsets
        if np.mean(trigger_delay)==0:
            pd_events = [events[i,0]+np.where(pd_dat[events[i,0]:events[i,0]+t_samples]>threshold)[0][0] for i in range(len(events))]
            trigger_delay = 1000. * (pd_events-events[:, 0]) / raw.info['sfreq']
        log_statements.append(('Trigger delay removed (μ ± σ): %0.1f ± %0.1f ms')
            % (np.mean(trigger_delay), np.std(trigger_delay)))

        if np.mean(trigger_delay)>10:
            events[:,0] = events[:,0]+5
            log_statements.append(f'photo diode and parallel port triggers are too far apart. using parallel port trigger {dsets[run]}')
        else:
            log_statements.append(f'photo diode used successfully {dsets[run]}')
            events[:, 0] = pd_events
    else: 
        # if the pd channel didn't work, add 5 samples as a standard delay
        events[:,0] = events[:,0]+5
        log_statements.append(f'photo diode did not record anything. using parallel port trigger {dsets[run]}')

    return raw,events,log_statements


def prepMarkers():
    subs   = ['S01']
    block_conditions = {
        'Still': ['0001', '0022', '0045', '0067', '0090', '0112', 
                        '0135', '0157', '0180', '0202', '0225', '0247',
                        '0270', '0292', '0315', '0337', 'catch']}
    
    trial_data = []
    blocks = list(block_conditions.keys())
    for block in blocks:
        conditions = block_conditions[block]
        for condition in conditions:
            block_data = {'Block': block, 'Condition': condition}
            trial_data.append(block_data)

    df = pd.DataFrame(trial_data)
    print(df)
    df['Code'] = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17]
    ids = df['Code']
    conds = df['Block']
    orients = df['Condition']
    event_id = {}
    for i, id in enumerate(ids):
        event_id[id] = f'{subs[0]}/{conds[i]}/{orients[i]}'
    #keys = [f'{sub}/{cond}/{orient}/{id}' for sub in subs for id in ids for cond in conds for orient in orients]
    return event_id

def writeMarkers(event_id, raw, events, stim_duration, currentDset, condition, log_statements):
    annotations = mne.annotations_from_events(events,sfreq=raw.info['sfreq'],event_desc = event_id)
    print(len(annotations))
    annotations.set_durations(stim_duration)
    raw.set_annotations(annotations)
    df = pd.DataFrame(annotations)
    if len(condition)>len(df):
        log_statements.append('WARNING!!! different number of trials in the run file and MEG file')
    mrk_template_writer.main(df,currentDset,stim_column='description')
    return raw, annotations

if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    # Command-line argument for the project path
    parser.add_argument(
        "-proj_path",
        required=True,
        help='path to project root directory e.g. "/misc/data12/sjapee/Sebastian-OrientationImagery/Data/"',
    )
    parser.add_argument(
        "-dataDate",
        required=True,
        help='the date of the data collection, e.g., "20240911"',
    )
    parser.add_argument(
        "-S",
        required=True,
        help='subject identifier, e.g., "Pilot1-SM"',
    )

    args = parser.parse_args()
    proj_path = args.proj_path
    dataDate = args.dataDate
    S = args.S

    # Other variables set within the script
    stim_duration = .3
    run_length = 4
    first_run_file = 1
    last_run_file = 8
    subid = int(S)

    raw_dir = proj_path + f'{dataDate}/' 
    logfile_dir = raw_dir + 'sheets/extracted_data'

    # Prep event IDs
    event_ids = prepMarkers()
    event_id = {v: k for k, v in event_ids.items()}

    # Load datasets
    dsets = []
    for i in range(first_run_file, last_run_file + 1, 2):
        ds = f'00{i}'
        dsets.append(raw_dir + glob.glob('*_' + ds + '.ds', root_dir=raw_dir)[0])

    # Prepare log files
    logfiles = []
    for i in range(1, run_length + 1):
        logfiles.append(logfile_dir + f'Still{str(subid)}{str(i)}.csv')
    
    print("Logfiles:", logfiles)

    # Process runs
    log_statements = []
    for run in range(len(dsets)):
        log_statements.append(dsets[run])
        log_statements.append(logfiles[run])
        raw, beh = setup_and_load(dsets[run], logfiles[run])
        raw, events, log_statements = find_events(raw, log_statements)
        raw, annotations = writeMarkers(event_ids, raw, events, stim_duration, dsets[run], list(beh['Condition']), log_statements)

    # Write log
    log_print_statements(log_statements, f'./logdir/{S}_prepbidsStill.txt')
    print("Log statements:", log_statements)
