import csv
import os
import random
import pandas as pd

localTest = 0
totalSheets = 6

local_path = '/Users/montesinossl/desktop/BlenderExp/'

if localTest == 1:
    stimulus_path = '/Users/montesinossl/desktop/BlenderExp/'
else:
    stimulus_path = 'C:/Users/meglab/EExperiments/Sebastian/BlenderPilot/'
# Set your variables
num_runs = 30  # Specify the number of runs

catch_percentage = 15  # Specify the percentage of rows to duplicate
break_freq = 25 #How many trials before a break screen comes up
jitter_amount = 0  # Specify the jitter amount

# Define conditions and their unique integer codes
conditions = ['frame_0001', 'frame_0045', 'frame_0090', 'frame_0135', 'frame_0180', 'frame_0225', 'frame_0270', 'frame_0315']
anticipated_length = int(num_runs*len(conditions) + (num_runs*len(conditions))*catch_percentage/100)
anticipated_length = int(num_runs*len(conditions))

condition_codes = {condition: idx + 1 for idx, condition in enumerate(conditions)}
conditionsOld = ['tst']
# Create a list to store the experiment data
experiment_data = []

for sheet in range(1, totalSheets + 1):
    # Generate data for each run
    experiment_data = []
    for run in range(1, num_runs + 1):
        conditions = conditions[:]
        random.shuffle(conditions)  # Shuffle conditions for each run
        #Ensures that the condition at the end of run is not the condition at the start of the next run
        #This would be a catch trial, but I want to determine all catch trials later
        while conditionsOld[-1] == conditions[0]:
            random.shuffle(conditions)
        
        #Loop to create the section in the dataframe for each run
        for i, condition in enumerate(conditions):
            code = condition_codes[condition]
            stimulus_filename = f'{condition}.png'
            stimulus_full_path = os.path.join(stimulus_path, f'Stimuli/{stimulus_filename}')
            currLength = ((run - 1) * len(conditions) + i + 1)

            # Append data for each trial
            #Break screens are calculated to appear based on break_freq, and to not appear within
            #the last 3 trials in a run
            experiment_data.append({'Run': run, 'Stimulus': stimulus_full_path, 
                                    'Condition': condition, 'Code': code, 'Catch': 0,
                                    'Break': 1 if currLength % break_freq == 0 and currLength < anticipated_length - 3 else 0})
        conditionsOld = conditions
    # Create a pandas DataFrame from the experiment_data list
        
    df = pd.DataFrame(experiment_data)
    #Determine how many rows to duplicate based on the percentage of catch trials
    num_rows_to_duplicate = int(len(experiment_data) * catch_percentage / 100)

    #Duplicate rows to create catch trials, add them after the original trial
    for i in range(num_rows_to_duplicate):
        random_jitter = random.randint(-jitter_amount, jitter_amount)
        # Calculate the index for the catch trial based on the current length of the dataframe
        original_index = int(len(df) * (i + 1) / (num_rows_to_duplicate + 1)) + random_jitter
        # Ensure the index stays within the bounds of the dataframe
        original_index = min(max(original_index, 0), len(df))
        #Make sure that no trial with a break screen is duplicated
        if df.iloc[original_index]['Break'] == 1:
            print('found it')
            continue
        # Insert the catch trial
        duplicated_row = df.iloc[original_index].copy()
        duplicated_row['Catch'] = 1
        duplicated_row['Code'] = 9
        df = pd.concat([df.iloc[:original_index + 1], duplicated_row.to_frame().T, df.iloc[original_index + 1:]]).reset_index(drop=True)



    # Specify the output Excel file
    output_excel_file = os.path.join(local_path, f'megStim{sheet}.xlsx')
    print(output_excel_file)
    # Write data to Excel file
    df.to_excel(output_excel_file, index=False)

print(f"Excel file '{output_excel_file}' generated successfully.")



'''
    for i in range(num_rows_to_duplicate):
        original_index = i % len(df)
        duplicated_row = df.iloc[original_index].copy()
        duplicated_row['Catch'] = 1
        df = pd.concat([df.iloc[:original_index], duplicated_row.to_frame().T, df.iloc[original_index+1:]]).reset_index(drop=True)
        '''