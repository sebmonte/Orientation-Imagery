import mne ,argparse
import pandas as pd 
import numpy as np  
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn import svm
from joblib import Parallel, delayed
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
import os

def select_conditions(epochs_stacked,column_name,items_to_select):
    if type(items_to_select)==list:
        selected_epochs = epochs_stacked[np.any([epochs_stacked.metadata[column_name] == i  for i in items_to_select],axis=0)]
    if type(items_to_select)==str:
        selected_epochs = epochs_stacked[epochs_stacked.metadata[column_name] == items_to_select]
    return selected_epochs

def train_test_split(epo_stacked, test_run):
    epochs_test = epo_stacked[f'run_nr == {test_run}']
    y_test = epochs_test.metadata['condition'].to_numpy()
    x_test = epochs_test._data

    epochs_train = epo_stacked[f'run_nr != {test_run}']
    y_train = epochs_train.metadata['condition'].to_numpy()
    x_train = epochs_train._data

    return x_train, x_test, y_train, y_test

def train_model(x_train,y_train):
    pipe = Pipeline([('scaler', StandardScaler()), 
            ('classifier', LinearDiscriminantAnalysis(solver='eigen', shrinkage=0.01))])
    pipe.fit(x_train,y_train)
    return pipe

def test_model(pipe, x_test, y_test):    
    # pipe.fit(x_train,y_train)
    acc = pipe.score(x_test,y_test)
    return acc

def run_decoding(x_train_tp, y_train, x_test_tp, y_test):
    pipe = train_model(x_train_tp, y_train)
    acc = pipe.score(x_test_tp, y_test)
    return acc


def run_process(bids_dir, Subject, train_time):
    epochs = mne.read_epochs(
        f'{bids_dir}/derivatives/preprocessed/sub-{Subject}_Still_preprocessed-epo.fif',
        preload=True
    )
    conditions_of_interest = ['0001', '0022', '0045', '0067', '0090', '0112', 
                              '0135', '0157', '0180', '0202', '0225', '0247',
                              '0270', '0292', '0315', '0337']
    epochs = select_conditions(epochs, 'condition', conditions_of_interest)

    times = epochs.times
    n_times = len(times)
    results_all = []

    run_numbers = np.unique(epochs.metadata['run_nr'])

    for test_run in run_numbers:
        x_train, x_test, y_train, y_test = train_test_split(epochs, test_run)
        x_train_tp = x_train[:, :, train_time]

        results = []
        for test_time in range(n_times):
            x_test_tp = x_test[:, :, test_time]
            acc = run_decoding(x_train_tp, y_train, x_test_tp, y_test)
            results.append(acc)
        results_all.append(results)

    # Average across cross-validation folds
    results_mean = np.mean(results_all, axis=0)

    out_dir = f'{bids_dir}/derivatives/WithinStill/{Subject}'
    os.makedirs(out_dir, exist_ok=True)
    out_file = f'{out_dir}/trainTime_{train_time:03d}.npy'
    np.save(out_file, results_mean)

    #print(f"Saved CV decoding results for {Subject} at train_time {train_time} to {out_file}")

    

##### Command-line inputs ######
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-S",
        required=True,
        help='subject identifier, e.g., "S01"',
    )
    parser.add_argument(
        "-traintime",
        required=True,
        help='training time ie. 1"',
    )

    parser.add_argument(
        "-bids_dir",
        required = True,
        help = 'supply a path to where the bids data is located'
    )

    args = parser.parse_args()
    Subject = args.S
    train_time = int(args.traintime)
    bids_dir = args.bids_dir

    run_process(bids_dir,Subject,train_time)