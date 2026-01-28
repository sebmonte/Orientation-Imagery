"""
Applying a sliding window of training times across the static condition data to the movie
Looks specifically at a 30ms timewindow around when an orientation appears,
and computes accuracy for predicting that correctly
Across all orientations and trials
"""

import os, mne, pickle, numpy as np, pandas as pd, time, argparse
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn import svm
from joblib import Parallel, delayed

# Command-line arguments
parser = argparse.ArgumentParser(description="Run sliding-window decoding for 1 subject")
parser.add_argument(
    "--subject",
    type=str,
    required=True,
    help="Subject ID (e.g., S01) or 'all'"
)
args = parser.parse_args()

# Paths and parameters
bids_dir = '/Users/sm6511/Desktop/NIH_Experiment/Bids'
data_path = f'{bids_dir}/derivatives/preprocessed/'
output_dir = '/Users/sm6511/Desktop/Orientation-Imagery/Results/Figure2'
os.makedirs(f"{output_dir}/data", exist_ok=True)
os.makedirs(f"{output_dir}/plots", exist_ok=True)

all_subjects = [f"S{i:02}" for i in range(1, 21)]

if args.subject.lower() == "all":
    subjects = all_subjects
else:
    subjects = [args.subject]

ordered_conditions = [
    '0001','0022','0045','0067','0090','0112','0135','0157',
    '0180','0202','0225','0247','0270','0292','0315','0337'
]
input_numbers = [0, 22, 45, 67, 90, 112, 135, 157, 180, 202, 225, 247, 270, 292, 315, 337]
movies = [22, 67, 112, 157, 202, 247, 292, 337]

specifyTime = True  # average across training window

#Functions
def select_conditions(epochs_stacked, column_name, items_to_select):
    if isinstance(items_to_select, list):
        return epochs_stacked[np.any(
            [epochs_stacked.metadata[column_name] == i for i in items_to_select],
            axis=0
        )]
    else:
        return epochs_stacked[epochs_stacked.metadata[column_name] == items_to_select]

def train_test_split_cross(epo_stacked, epo_stackedMovie, test_condition, start_time, end_time):
    epochs_test = epo_stackedMovie[
        epo_stackedMovie.metadata['condition'] == test_condition
    ]
    y_test = epochs_test.metadata['condition'].to_numpy()
    x_test = epochs_test._data

    epochs_train = epo_stacked
    y_train = epochs_train.metadata['condition'].to_numpy()

    if specifyTime:
        mask = (epochs_train.times >= start_time) & (epochs_train.times <= end_time)
        x_train = np.mean(epochs_train._data[:, :, mask], axis=2)
    else:
        x_train = epochs_train._data

    return x_train, x_test, y_train, y_test

def run_decoding_cross(x_train, y_train, x_test):
    pipe = Pipeline([
        ('scaler', StandardScaler()),
        ('classifier', svm.SVC(kernel='linear', C=1))
    ])
    pipe.fit(x_train, y_train)
    return pipe.predict(x_test)

def find_contacting_movies_and_samples(input_number, movies):
    def normalize_frame(frame):
        return frame % 360

    def frames_contact(movie_start, input_number):
        right_frames = [(movie_start + i) % 360 for i in range(181)]
        left_frames = [normalize_frame(movie_start - i) for i in range(181)]
        return input_number in right_frames, input_number in left_frames

    def calculate_sample_time(movie_start, input_number, direction):
        if direction == "Right":
            frame_difference = (input_number - movie_start) % 360
        else:
            frame_difference = (movie_start - input_number) % 360
        return 60 if frame_difference == 0 else 60 + frame_difference * 20

    result = {}
    for movie_start in movies:
        right_contacts, left_contacts = frames_contact(movie_start, input_number)

        for direction, contact in zip(["Right", "Left"], [right_contacts, left_contacts]):
            if not contact:
                continue

            movie_name = (
                f"00{movie_start}_{direction}" if movie_start < 100
                else f"0{movie_start}_{direction}"
            )
            latency = 107
            sample_time = calculate_sample_time(movie_start, input_number, direction) + 240 + latency
            if sample_time >= 400:
                result[movie_name] = sample_time

    return result

def getAveragePrediction(decoding_dictList, ordered_conditions):
    proportionList = []
    for index, cond in enumerate(ordered_conditions):
        all_strings = [
            item for sublist in decoding_dictList[index].values() for item in sublist
        ]
        flattened = [i for arr in all_strings for i in arr]
        proportionList.append(flattened.count(cond) / len(flattened) if flattened else 0)
    return np.mean(proportionList)

# Main loop
all_subject_peaks = []

for Subject in subjects:
    print(f"\nProcessing {Subject}...")

    fn_still = f'sub-{Subject}_Still_preprocessed-epo.fif'
    fn_dynamic = f'sub-{Subject}_Dynamic_preprocessed-epo.fif'

    epochs_still = mne.read_epochs(data_path + fn_still)
    epochs_movie = mne.read_epochs(data_path + fn_dynamic)

    epochs_still.metadata['degrees_string'] = [
        k.split('/')[-1] for k in epochs_still.metadata['trial_type']
    ]
    epochs_still = epochs_still[epochs_still.metadata['degrees_string'] != 'catch']
    epochs_still.metadata['degrees'] = epochs_still.metadata['degrees_string'].astype(int)
    epochs_still.metadata.rename(columns={'run_nr': 'run'}, inplace=True)

    result_list = [find_contacting_movies_and_samples(i, movies) for i in input_numbers]
    window_width = 0.03

    masterList = []
    center_times = np.arange(-0.18, 0.58 + 0.001, 0.01)

    for center_time in center_times:
        decoding_dictList = []
        trainStart = center_time - window_width / 2
        trainEnd   = center_time + window_width / 2

        for i in result_list:
            decoding_dict = {}
            for movie, sample_time in i.items():
                x_train, x_test, y_train, _ = train_test_split_cross(
                    epochs_still, epochs_movie, movie, trainStart, trainEnd
                )
                decoding_list = Parallel(n_jobs=12, prefer="threads")(
                    delayed(run_decoding_cross)(
                        x_train, y_train, x_test[:, :, t]
                    )
                    for t in range(sample_time - 18, sample_time + 19)
                )
                decoding_dict[movie] = decoding_list
            decoding_dictList.append(decoding_dict)

        masterList.append(decoding_dictList)

    decoding_peak = [getAveragePrediction(i, ordered_conditions) for i in masterList]
    all_subject_peaks.append(decoding_peak)

    np.save(f"{output_dir}/data/slidingWindow1_peaks_{Subject}_latency.npy", decoding_peak)

    plt.figure(figsize=(6, 5))
    plt.axhline(y=1/16, linestyle='--')
    plt.plot(center_times, decoding_peak)
    plt.xlabel('Time (seconds)')
    plt.ylabel('Decoding Accuracy')
    plt.title(f"Subject {Subject}")
    plt.savefig(f"{output_dir}/plots/slidingWindow_plot_{Subject}.png")
    plt.close()

