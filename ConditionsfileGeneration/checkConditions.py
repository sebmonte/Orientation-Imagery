import pandas as pd

# Define the local path and file names
local_path = '/Users/montesinossl/Desktop/BlenderExp/'
file_names = ['megStimMovie1.xlsx', 'megStimMovie2.xlsx', 'megStimMovie3.xlsx', 'megStimMovie4.xlsx', 'megStimMovie5.xlsx']

# Read the Excel files into DataFrames
dfs = [pd.read_excel(local_path + file_name, engine='openpyxl') for file_name in file_names]

# Define the sublists
sublists = [
    ['0022_Left', '0022_Right', '0202_Left', '0202_Right'],
    ['0067_Left', '0067_Right', '0247_Left', '0247_Right'],
    ['0112_Left', '0112_Right', '0292_Left', '0292_Right'],
    ['0157_Left', '0157_Right', '0337_Left', '0337_Right']
]

def check_violations(dfs, sublists):
    violations = []
    
    # Convert sublists to dictionary for quick lookup
    sublist_dict = {}
    for sublist in sublists:
        for condition in sublist[:2]:
            sublist_dict[condition] = sublist
        for condition in sublist[2:]:
            sublist_dict[condition] = sublist
    total_index = 0  # To track the row index across all DataFrames
    for idx, df in enumerate(dfs):
        if 'Condition' in df.columns:
            conditions = df['Condition'].tolist()
            for i in range(len(conditions) - 1):
                current_condition = conditions[i]
                next_condition = conditions[i + 1]
                
                # Get the corresponding sublists
                if current_condition in sublist_dict and next_condition in sublist_dict:
                    current_sublist = sublist_dict[current_condition]
                    next_sublist = sublist_dict[next_condition]
                    
                    # Check if both conditions are in the same sublist
                    if current_sublist == next_sublist:
                        current_first_two = set(current_sublist[:2])
                        current_last_two = set(current_sublist[2:])
                        
                        if (current_condition in current_first_two and next_condition in current_last_two) or \
                           (current_condition in current_last_two and next_condition in current_first_two):
                            violations.append((total_index + i, current_condition, next_condition))
    
    return violations

violations = check_violations(dfs, sublists)
print(violations)
