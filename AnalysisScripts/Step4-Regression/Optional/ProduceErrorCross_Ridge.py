

#########################
# **** cross-validated optimization of intercept for ridge regression ****
#########################
import os
import mne ,argparse
import pandas as pd 
import numpy as np 
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt 
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from joblib import Parallel, delayed
from collections import Counter
import seaborn as sns
from sklearn.linear_model import RidgeCV
from sklearn.metrics import r2_score


from sklearn.linear_model import BayesianRidge

def linear_regression_timegen(X_train, X_test, y_train_deg, t_test,t_train):
    y_train_sin = np.sin(np.deg2rad(y_train_deg))
    y_train_cos = np.cos(np.deg2rad(y_train_deg))
    
    # Average over training time window
    X_train = X_train[:, :, t_train]

    pipe_sin = Pipeline([
        ('scaler', StandardScaler()),
        ('regression', Ridge(alpha=1000))
    ])
    pipe_cos = Pipeline([
        ('scaler', StandardScaler()),
        ('regression', Ridge(alpha=1000))
    ])

    # Fit on training data
    pipe_sin.fit(X_train, y_train_sin)
    pipe_cos.fit(X_train, y_train_cos)

    # Predict on test timepoint
    y_pred_sin = pipe_sin.predict(X_test[:, :, t_test])
    y_pred_cos = pipe_cos.predict(X_test[:, :, t_test])

    # Convert back to degrees (0–360)
    y_pred_angle = np.rad2deg(np.arctan2(y_pred_sin, y_pred_cos)) % 360
    return y_pred_angle



def run_regression_cross(epochs_train, epochs_test, target_column_train, target_column_test, t_train):
    # Extract degree targets
    y_train_deg = epochs_train.metadata[target_column_train].values.astype(float)
    y_test_deg = epochs_test.metadata[target_column_test].values.astype(float)

    # Extract full data
    X_train = epochs_train._data  # shape: (n_trials, n_channels, n_times)
    X_test = epochs_test._data

    # Run time-generalized decoding
    y_predicted = Parallel(n_jobs=8)(
        delayed(linear_regression_timegen)(
            X_train, X_test, y_train_deg,
            t_test=t,
            t_train = t_train
        )
        for t in range(X_test.shape[2])
    )

    # Convert to shape: (n_trials, n_times)
    y_predicted = np.array(y_predicted).T

    return y_predicted, y_test_deg




def run_process(bids_dir,Subject,train_time):
    # Specify the custom filename from which you want to load the pickle file
    epochs_still = mne.read_epochs(
        f'{bids_dir}/derivatives/preprocessed/sub-{Subject}_Still_preprocessed-epo.fif',
        preload=True
    )
    epochs_mini = mne.read_epochs(
        f'{bids_dir}/derivatives/preprocessed/sub-{Subject}_miniEpochs_preprocessed-epo.fif',
        preload=True
    )

    # exclude catch trials from stills & add degree column
    epochs_still.metadata['degrees_string'] = [k.split('/')[-1] for k in epochs_still.metadata['trial_type']]
    epochs_still = epochs_still[epochs_still.metadata['degrees_string'] != 'catch']
    epochs_still.metadata['degrees']=[int(i) for i in epochs_still.metadata['degrees_string']]
    epochs_still.metadata.rename(columns={'run_nr': 'run'}, inplace=True)

    epochs_mini.metadata['degrees'] = epochs_mini.metadata['degrees'].astype(int)

    target_column_train = 'degrees'
    target_column_test = 'degrees'
    epochs_train = epochs_still
    epochs_test = epochs_mini


    y_pred, y_true = run_regression_cross(epochs_train,epochs_test,target_column_train,target_column_test, train_time)
    out_dir = f'{bids_dir}/derivatives/CrossDecode/{Subject}'
    os.makedirs(out_dir, exist_ok=True)
    np.save(os.path.join(out_dir, f"{Subject}_predictions_{train_time}.npy"), y_pred)
    np.save(os.path.join(out_dir, f"{Subject}_true_{train_time}.npy"), y_true)
    errors_totals = []

    for trial in range(y_pred.shape[0]):  # n_trials
        trial_errors = []
        
        sign_flip = -1 if 'Left' in epochs_mini.metadata['condition'].iloc[trial] else 1
        actual_angle = y_true[trial]

        for time in range(y_pred.shape[1]):  # n_timepoints (typically 60)
            predicted_angle = y_pred[trial, time]
            # Compute circular error in degrees, signed
            error = ((predicted_angle - actual_angle + 180) % 360) - 180
            if trial < 2:  # Only print first two trials
                print(f"Trial {trial} Predicted: {predicted_angle}, Error: {error}")

            error *= sign_flip

            trial_errors.append(error)

        errors_totals.append(trial_errors)

    # Save as numpy array
    errors_total_array = np.array(errors_totals)

    np.save(os.path.join(out_dir, f"{Subject}_errors_{train_time}.npy"), errors_total_array)

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