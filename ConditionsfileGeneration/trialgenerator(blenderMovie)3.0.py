import csv
import os
import random
import pandas as pd

localTest = 1
totalSheets = 5

local_path = '/Users/montesinossl/desktop/BlenderExp/'

if localTest == 1:
    stimulus_path = '/Users/montesinossl/desktop/BlenderExp/'
else:
    stimulus_path = 'C:/Users/meglab/EExperiments/Sebastian/BlenderPilot/'
# Set your variables
num_runs =  7 # Specify the number of runs

catch_percentage = 15  # Specify the percentage of rows to duplicate
break_freq = 10 #How many trials before a break screen comes up
jitter_amount = 0  # Specify the jitter amount

# Define conditions and their unique integer codes
conditions = ['0022_Left', '0022_Right', '0067_Left', '0067_Right', '0112_Left', 
              '0112_Right', '0157_Left', '0157_Right', '0202_Left', '0202_Right',
              '0247_Left', '0247_Right', '0292_Left', '0292_Right', '0337_Left', '0337_Right']

# This creates a dictionary that maps the conditions that
#end in the same places as others start. For instance '0022_Left'
#Ends where '292_Right' starts and vice versa
grouped_conditions = {}
def find_group_key(num):
    return min(num, num - 180 if num >= 180 else num + 180)

for condition in conditions:
    number, side = condition.split('_')
    num = int(number)
    group_key = find_group_key(num)
    
    if group_key not in grouped_conditions:
        grouped_conditions[group_key] = []
    grouped_conditions[group_key].append(condition)

# This is now a list where each sublist contains the conditions
#Grouped by start and end positions being the same
grouped_list = list(grouped_conditions.values())


#This function is intended to check if a given trial is preceded by
#A trial that ended where this trial begins. We want to have this
#Not happen to avoid any effect of continuity 
#We take in a list of trials for a given run in the experiment,
#and also a list that shows what trials start and end in the same places
#Returns true if any two trials in a run start or end in the same place
#Otherwise returns false
def validate_grouping1(input_list, grouped_list):
    # Create a mapping from condition to its index in the input list
    index_map = {condition: index for index, condition in enumerate(input_list)}
    
    for group in grouped_list:
        
        # Get indices for the first two and last two elements in the group
        first_two_indices = [index_map[group[0]], index_map[group[1]]]
        last_two_indices = [index_map[group[-2]], index_map[group[-1]]]
        # Check for violations
        for first_index in first_two_indices:
            for last_index in last_two_indices:
                if abs(first_index - last_index) == 1:
                    return True
    
    return False


#This also checks whether one trial is next to another such that
#it ends where another trial begins. The difference is that this function
#only takes 2 trials, so it is used in-between runs and for catch-trial
#placement to also remove perceptual continuity there
def validate_grouping2(input_list):
    number, side = input_list[0].split('_')
    number2, side = input_list[1].split('_')

    num1 = int(number)
    num2 = int(number2)
    if abs(num2 - num1) == 180:
        return True
    
    return False



anticipated_length = int(num_runs*len(conditions) + (num_runs*len(conditions))*catch_percentage/100)
anticipated_length = int(num_runs*len(conditions))

condition_codes = {condition: idx + 1 for idx, condition in enumerate(conditions)}
conditionsOld = ['0_test']
# Create a list to store the experiment data
experiment_data = []

for sheet in range(1, totalSheets + 1):
    # Generate data for each run
    experiment_data = []
    for run in range(1, num_runs + 1):
        conditions = conditions[:]
        random.shuffle(conditions)  # Shuffle conditions for each run
        #Ensures that no trial in the run stars where a previous trial ended, and that the first trial in the run
        #Does not start where the last trial in the previous run ended
        while (validate_grouping1(conditions, grouped_list) == True) or validate_grouping2([conditionsOld[-1], conditions[0]]) == True:
            random.shuffle(conditions)
        #while conditionsOld[-1] == conditions[0]:
            #random.shuffle(conditions)
        
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
            continue
        # Insert the catch trial
        # Insert the catch trial
        duplicated_row = df.iloc[original_index].copy()
        duplicated_row['Catch'] = 1
        catchCond = random.choice(conditions)
        # Before inserting the catch trial, make sure that the previous trial and the subsequent trial
        #Do not start where this trial ends
        while validate_grouping2([catchCond, df.iloc[original_index]['Condition']]) or validate_grouping2([catchCond, df.iloc[original_index + 1]['Condition']]):
            catchCond = random.choice(conditions)
        duplicated_row['Condition'] = catchCond
        duplicated_row['Code'] = 17
        df = pd.concat([df.iloc[:original_index + 1], duplicated_row.to_frame().T, df.iloc[original_index + 1:]]).reset_index(drop=True)


    # Specify the output Excel file
    output_excel_file = os.path.join(local_path, f'megStimMovie{sheet}.xlsx')
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