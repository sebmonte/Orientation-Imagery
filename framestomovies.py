import pandas as pd
from psychopy import visual, event, core, gui, data, logging, parallel
import os

testStim = '/Users/meglab/EExperiments/Sebastian/BlenderMoviePilot/'
run_file = 1
win = visual.Window(units="pix", fullscr=0, color=(-.5, -.5, -.5))
rundata=data.importConditions(testStim + f'megStimMovie{run_file}.xlsx')
rundata = pd.DataFrame(rundata)
stimWidth = 1
stimHeight = 1

filenames = []
for filename in os.listdir(testStim + '/Stimuli/'):
    if filename.startswith('frame_') and filename.endswith('.png'):
        filenames.append(filename)


def extract_number(filename):
    # Assuming the number is between 'frame_' and '.jpg'
    number_part = filename[len('frame_'):-len('.png')]
    return int(number_part)

# Sort the filenames based on the numeric value in their names
filenames.sort(key=extract_number)

print(filenames)

possibleImages = []
for filename in filenames:
    file_path = os.path.join(testStim + '/Stimuli/', filename)  
    possibleImages.append(filename)

print('length is', len(possibleImages))


def generate_image_list(start_frame, direction, win, num_frames=180):
    images = []
    if direction == 'Left':
        step = -1
    else:
        step = 1
    
    current_frame = start_frame
    for _ in range(num_frames):
        images.append(possibleImages[current_frame - 1])
        #images.append(visual.ImageStim(win, testStim + '/Stimuli/' f"frame_{current_frame:04d}.png", size=(stimHeight, stimWidth), units = 'pix', pos = (0, 20)))
        current_frame += step
        if current_frame > 360:
            current_frame = 1
        elif current_frame < 1:
            current_frame = 360
    return images


imageDict = {}
for condition in rundata['Condition'].unique():
    start_frame, direction = condition.split('_')
    start_frame = int(start_frame)
    print(start_frame)

    # Generate the list of images
    image_list = generate_image_list(start_frame, direction, win)

    imageDict[condition] = image_list

    # Print or store the image list
    print(f"Condition: {condition}")

print(len(imageDict['0157_Left']))


# Create a DataFrame
df = pd.DataFrame(imageDict)

# Specify the Excel file path
excel_file_path = 'frameTest.xlsx'

# Write DataFrame to Excel
df.to_excel(excel_file_path, index=False)
