import os
import re

#####Renames MEG run files in pre-bids format so that the different types of runs (still and dynamic) are named differently######
#This is necessary because of the way make_meg_bids from nih2mne names tasks"


def rename_dynamic_trials(root_dir):
    # Regex pattern to match folders with the run number at the end
    folder_pattern = re.compile(r'(.*_OrientationImagery_)(\d{8}_)(\d+)(\.ds)')
    
    for folder in os.listdir(root_dir):
        folder_path = os.path.join(root_dir, folder)
        
        if os.path.isdir(folder_path):
            match = folder_pattern.match(folder)
            if match:
                base_name, date_part, run_number, ext = match.groups()
                run_number = int(run_number)
                
                # Check if it is an even run number (dynamic trial)
                if run_number % 2 == 0:
                    # Rename the folder by removing the underscore and adding 'Dynamic' after 'OrientationImagery'
                    new_folder_name = f"{base_name[:-1]}Dynamic_{date_part}{str(run_number).zfill(3)}{ext}"
                    new_folder_path = os.path.join(root_dir, new_folder_name)
                    os.rename(folder_path, new_folder_path)
                    print(f"Renamed folder: {folder} -> {new_folder_name}")
                    
                    # Rename files inside the folder if they contain 'OrientationImagery'
                    for file_name in os.listdir(new_folder_path):
                        if 'OrientationImagery' in file_name:
                            # Remove underscore and add 'Dynamic' directly after 'OrientationImagery'
                            new_file_name = file_name.replace('OrientationImagery_', 'OrientationImageryDynamic_')
                            os.rename(
                                os.path.join(new_folder_path, file_name),
                                os.path.join(new_folder_path, new_file_name)
                            )
                            print(f"Renamed file: {file_name} -> {new_file_name}")





# Identify root directory where pre-bids MEG data is stored, run function
#root_directory = '/System/Volumes/Data/misc/data12/sjapee/Sebastian-OrientationImagery/Data/20250211/'
root_directory = '/Users/montesinossl/Desktop/Data/20250514'
rename_dynamic_trials(root_directory)
