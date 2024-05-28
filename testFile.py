import pandas as pd
from psychopy import visual, event, core, gui, data, logging, parallel

testStim = '/Users/montesinossl/Desktop/BlenderExp/'
run_file = 1

rundata=data.importConditions(testStim + f'megStim{run_file}.xlsx')
rundata = pd.DataFrame(rundata)

def generate_image_list(start_frame, direction, num_frames=72):
    images = []
    if direction == 'Left':
        step = -1
    else:
        step = 1
    
    current_frame = start_frame
    for _ in range(num_frames):
        images.append(f"frame_{current_frame:04d}.jpg")
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

    # Generate the list of images
    image_list = generate_image_list(start_frame, direction)

    imageDict[condition] = image_list

    # Print or store the image list
    print(f"Condition: {condition}, Images: {image_list}")

