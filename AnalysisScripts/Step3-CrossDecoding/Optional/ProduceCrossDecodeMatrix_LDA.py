"""Script to produce temporal generalization of training and testing times: uses the midiepochs to produce
4 matrices, each of which represents a 1/4 chunk of the movie. Looks at what the model predicts over time
in each chunk with respect to what happens at the beginning and end of that chunk. Must run in conjunction
with a swarm file in biowulf"""


import mne ,argparse
import pandas as pd 
import numpy as np  
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn import svm
from joblib import Parallel, delayed
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis

def select_conditions(epochs_stacked,column_name,items_to_select):
    if type(items_to_select)==list:
        selected_epochs = epochs_stacked[np.any([epochs_stacked.metadata[column_name] == i  for i in items_to_select],axis=0)]
    if type(items_to_select)==str:
        selected_epochs = epochs_stacked[epochs_stacked.metadata[column_name] == items_to_select]
    return selected_epochs

def train_test_split_cross(epo_stacked, epo_stackedMovie, test_condition, chunk):
    epochs_test = epo_stackedMovie[
    (epo_stackedMovie.metadata['condition'] == test_condition) & 
    (epo_stackedMovie.metadata['chunk'] == chunk)]
    y_test = epochs_test.metadata['condition'].to_numpy()
    x_test = epochs_test._data
    #x_test = x_test[100:500:]
    x_test.shape
    epochs_train=epo_stacked[epo_stacked.metadata['block_type'] == 'Still']
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

def determineStillCond(condition, chunk):
    still_list = ['0022', '0067', '0112', '0157', '0202', '0247', '0292', '0337']
    movienumber, direction = condition.split('_')
    start_index = still_list.index(movienumber)
    step = -1 if direction == 'Left' else 1
    chunk_start_index = (start_index + chunk * step) % len(still_list)
    chunk_next_index = (chunk_start_index + step) % len(still_list)
    first_still = still_list[chunk_start_index]
    second_still = still_list[chunk_next_index]
    return first_still, second_still


def run_cross_decoding(bids_dir,Subject,train_time):
    epochs_still = mne.read_epochs(f'{bids_dir}/derivatives/preprocessed/sub-{Subject}_Still_preprocessed-epo.fif')
    epochs_midi = mne.read_epochs(f'{bids_dir}/derivatives/preprocessed/sub-{Subject}_midiEpochs_preprocessed-epo.fif')

    allmovieConditions = np.unique(epochs_midi.metadata['condition'])

    first_chunks,second_chunks,third_chunks,fourth_chunks = [],[],[],[]
    for i in allmovieConditions:
        res_per_chunk = np.zeros((len(np.unique(epochs_midi.metadata['chunk'])),len(epochs_midi.times)))
        for p in np.unique(epochs_midi.metadata['chunk']):
            first_still, second_still = determineStillCond(i, p)
            epochs_selected = select_conditions(epochs_still,column_name='condition',items_to_select=[first_still, second_still])
            x_train, x_test, y_train, y_test_orig = train_test_split_cross(epochs_selected, epochs_midi, i, p)
            # this is going to return the accuracy for predicting the first still
            # as it's a pairwise classification the accuracy for prediciting the second still is just the mirror reverse
            pipe = train_model(x_train[:,:,train_time], y_train)
            y_test = np.repeat(first_still,y_test_orig.shape[0]) 
            classification_acc = Parallel(n_jobs=32)(delayed(test_model)(pipe, x_test[:,:,t],y_test) for t in range(x_test.shape[2]))
            res_per_chunk[p,:] = classification_acc
        first_chunks.append(res_per_chunk[0,:])
        second_chunks.append(res_per_chunk[1,:])
        third_chunks.append(res_per_chunk[2,:])
        fourth_chunks.append(res_per_chunk[3,:])
    chunklist = [first_chunks, second_chunks, third_chunks, fourth_chunks]

    np.save(f"{bids_dir}/derivatives/output2/{Subject}chunks{train_time}.npy",np.array(chunklist))

    return np.array(chunklist)
    

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

    run_cross_decoding(bids_dir,Subject,train_time)