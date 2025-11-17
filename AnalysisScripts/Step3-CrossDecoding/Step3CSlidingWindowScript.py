"Applying a sliding window of training times across the static condition data to the movie"
"Looks specifically at a 30ms timewindow around when an orientation appears, and computes accuracy for predicting that corretly"
"Across all orientations and trials"

import os, mne, pickle, numpy as np, pandas as pd, time
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn import svm
from joblib import Parallel, delayed

# Parameters
bids_dir = 'Users/sm6511/Desktop/NIH_Experiment/Bids'
data_path = f'{bids_dir}/derivatives/preprocessed/'
output_dir = '/Users/sm6511/Desktop/Orientation-Imagery/Results/Figure2'
os.makedirs(output_dir, exist_ok=True)
subjects = [f"S{i:02}" for i in range(1, 21)] 
ordered_conditions = ['0001','0022', '0045','0067', '0090', '0112','0135', '0157','0180', '0202','0225','0247','0270', '0292','0315','0337']
input_numbers = [0, 22, 45, 67, 90, 112, 135, 157, 180, 202, 225, 247, 270, 292, 315, 337]
movies = [22, 67, 112, 157, 202, 247, 292, 337]

#Average across or pick time points and then test for each time point 
specifyTime = True

def select_conditions(epochs_stacked,column_name,items_to_select):
    """Select conditions to analyze from an epochs object"""
    #Select specific conditions from an epochs object
    if type(items_to_select)==list:
        selected_epochs = epochs_stacked[np.any([epochs_stacked.metadata[column_name] == i  for i in items_to_select],axis=0)]
    if type(items_to_select)==str:
        selected_epochs = epochs_stacked[epochs_stacked.metadata[column_name] == items_to_select]
    return selected_epochs

def train_test_split_cross(epo_stacked, epo_stackedMovie, test_condition, start_time, end_time):
    """Split into training and testing time, if specifyTime = true, average across a window for training"""
    #Create train and testing splits, train on a passed in window
    epochs_test=epo_stackedMovie[epo_stackedMovie.metadata['condition'] == test_condition]
    y_test = epochs_test.metadata['condition'].to_numpy()
    x_test = epochs_test._data
    #x_test = x_test[100:500:]
    x_test.shape
    epochs_train=epo_stacked
    y_train = epochs_train.metadata['condition'].to_numpy()
    mask = (epochs_train.times >= start_time) & (epochs_train.times <= end_time)


    if specifyTime == True:
        mask = (epochs_train.times >= start_time) & (epochs_train.times <= end_time)
        x_train = np.mean(epochs_train._data[:,:,mask], axis = 2)

    else:
        x_train = epochs_train._data
    return x_train, x_test, y_train, y_test

def run_decoding_cross(x_train,y_train,x_test):
    """Create and run decoding pipeline"""
    #Create pipeline
    pipe = Pipeline([('scaler', StandardScaler()), 
            ('classifier', svm.SVC(kernel='linear',C=1))])
    pipe.fit(x_train,y_train)
    predictions = pipe.predict(x_test)
    return predictions

def find_contacting_movies_and_samples(input_number, movies):
    """This function looks, for each orientation, which movies pass through it and at what time in samples they do so
#Note: This intentionally excludes instances when an orientation appears right at the beginning of a movie from its list, 
since we do not want to include decoding for the first frame to appear as this is different from the rest (still-still)"""
    def normalize_frame(frame):
        #Normalize frame to be within 0 to 359.
        return frame % 360

    def frames_contact(movie_start, input_number):
        #Check if a movie intersects the input number
        right_frames = [(movie_start + i) % 360 for i in range(181)]
        left_frames = [(movie_start - i) % 360 for i in range(181)]
        left_frames = [normalize_frame(f) for f in left_frames]

        return input_number in right_frames, input_number in left_frames

    def calculate_sample_time(movie_start, input_number, direction):
        #Calculate the sample time at which the movie passes through the input number
        if direction == "Right":
            frame_difference = (input_number - movie_start) % 360
        else:  # direction == "Left"
            frame_difference = (movie_start - input_number) % 360
        
        if frame_difference == 0:
            return 60
        else:
            return 60 + frame_difference * 20

    result = {}
    for movie_start in movies:
        right_contacts, left_contacts = frames_contact(movie_start, input_number)
        
        if right_contacts:
            if movie_start < 100: #Ensure correct naming, movies less than 100 have two zeros in front of them in condition name
                movie_name = f"00{movie_start}_Right"
            else:
                movie_name = f"0{movie_start}_Right"
            sample_time = calculate_sample_time(movie_start, input_number, "Right") + 240
            if sample_time < 400:
                continue  # skip this movie
            result[movie_name] = sample_time
        
        if left_contacts:
            if movie_start < 100:
                movie_name = f"00{movie_start}_Left"
            else:
                movie_name = f"0{movie_start}_Left"
            sample_time = calculate_sample_time(movie_start, input_number, "Left") + 240
            if sample_time < 400:
                continue
            result[movie_name] = sample_time

    return result

def getAveragePrediction(decoding_dictList, ordered_conditions):
    """The decoding loop returns a list of dictionaries, where each entry corresponds to a given still orientation.
    In each dictionary, a given movie is mapped to predictions of specific conditions. To convert this to accuracy score,
    we need to convert this to proportions based on which orientation the movie was actually presenting. This function aims to do
    that, the key logic being that the length of decoding_dictList must match the length of ordered_conditions, and the contents of each
    must line up. For instance, if the first entry in ordered_conditions is '0001', this should mean that the first entry in decoding_dictList
    contains dictionaries with predictions for different movies where the correct answer was '0001'. Using this we can compute accuracy"""
    proportionList = []
    for index, cond in enumerate(ordered_conditions):
        all_strings = [item for sublist in decoding_dictList[index].values() for item in sublist]
        flattened_list = [item for array in all_strings for item in array]
        center_count = flattened_list.count(cond)
        total_entries = len(flattened_list)
        proportion = center_count / total_entries if total_entries > 0 else 0
        proportionList.append(proportion)
    return np.mean(proportionList)

all_subject_peaks = []

#Loop to process sliding window script
for Subject in subjects:
    print(f"Processing {Subject}...")

    fn_still = f'sub-{Subject}_Still_preprocessed-epo.fif'
    fn_dynamic = f'sub-{Subject}_Dynamic_preprocessed-epo.fif'
    print(data_path + fn_still)
    epochs_still = mne.read_epochs(data_path + fn_still)
    epochs_movie = mne.read_epochs(data_path + fn_dynamic)
    #Clean up metadata
    epochs_still.metadata['degrees_string'] = [k.split('/')[-1] for k in epochs_still.metadata['trial_type']]
    epochs_still = epochs_still[epochs_still.metadata['degrees_string'] != 'catch']
    epochs_still.metadata['degrees'] = [int(i) for i in epochs_still.metadata['degrees_string']]
    epochs_still.metadata.rename(columns={'run_nr': 'run'}, inplace=True)
    #Get list of conditions to test decoding on
    result_list = [find_contacting_movies_and_samples(i, movies) for i in input_numbers]
    #Set width of window for decoding
    window_width = 0.03  # 30 ms window 
    masterList = []
    '''
    while trainEnd < 0.6:
        decoding_dictList = []
        for i in result_list:
            decoding_dict = {}
            for movie, sample_time in i.items():
                x_train, x_test, y_train, y_test = train_test_split_cross(epochs_still, epochs_movie, movie, trainStart, trainEnd)
                startTime = sample_time - 10
                endTime = sample_time + 10
                decoding_list = Parallel(n_jobs=12, prefer="threads")(delayed(run_decoding_cross)(x_train, y_train, x_test[:,:,t]) for t in range(startTime, endTime))
                decoding_dict[movie] = decoding_list
            decoding_dictList.append(decoding_dict)
        masterList.append(decoding_dictList)
        trainStart += increment
        trainEnd += increment
    '''

    center_times = np.arange(-0.18, 0.58 + 0.001, 0.01)  
    for center_time in center_times:
        decoding_dictList = []
        trainStart = center_time - window_width / 2
        trainEnd = center_time + window_width / 2

        for i in result_list:
            decoding_dict = {}
            for movie, sample_time in i.items():
                x_train, x_test, y_train, y_test = train_test_split_cross(
                    epochs_still, epochs_movie, movie, trainStart, trainEnd
                )
                #30 second testing window
                startTime = sample_time - 18
                endTime = sample_time + 19
                decoding_list = Parallel(n_jobs=12, prefer="threads")(
                    delayed(run_decoding_cross)(x_train, y_train, x_test[:,:,t])
                    for t in range(startTime, endTime)
                )
                decoding_dict[movie] = decoding_list
            decoding_dictList.append(decoding_dict)
        
        masterList.append(decoding_dictList)
    decoding_peak = [getAveragePrediction(i, ordered_conditions) for i in masterList]
    all_subject_peaks.append(decoding_peak)
    np.save(f"{output_dir}/data/slidingWindow1_peaks_{Subject}.npy", decoding_peak)

    time_values = np.arange(-0.18, 0.58 + 0.01, 0.01)
    plt.figure(figsize=(6, 5))
    plt.axhline(y=1/16, color='grey', linestyle='--', label='chance')
    plt.plot(time_values, decoding_peak, color='#6495ED')
    plt.xlabel('Time (seconds)')
    plt.ylabel('Decoding Accuracy')
    plt.title(f"Subject {Subject}")
    plt.savefig(f"{output_dir}/plots/slidingWindow_plot_{Subject}.png")
    plt.close()

# Final average plot across processed subjects
avg_peak = np.mean(all_subject_peaks, axis=0)
np.save(f"{output_dir}/data/decoding_peaks_avg1.npy", avg_peak)
plt.figure(figsize=(6, 5))
plt.axhline(y=1/16, color='grey', linestyle='--', label='chance')
plt.plot(time_values, avg_peak, color='black')
plt.xlabel('Time (seconds)')
plt.ylabel('Average Decoding Accuracy')
plt.title("Average Across Subjects")
plt.savefig(f"{output_dir}/plots/slidingWindow_average.png")
plt.close()


