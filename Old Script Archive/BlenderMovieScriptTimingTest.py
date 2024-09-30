#This is a script for an experiment that displays videos of a face rotating on its vertical axis

#Setup Libraries
from psychopy import visual, event, core, gui, data, logging, parallel
import glob
import numpy as np
import random
import pandas as pd
import os
import sys
from psychopy.hardware import keyboard
import math
from PIL import Image

#Initial parameters
participant = 1
run_file = 1 #change every run
ismeg = 0
isfull = 0
iseyetracking = 0
islaptop = 0
response_keys = ['1','2','3','4','q']
length = 0 #if 0, 180 frame movies, if 1, 90 frame movies (twice as fast)
generationMethod = 0 #If 0, movies labeled 'right' go numerically up, 'left' goes numerically down in frames
#if 1, movies go left/right based on head position as you look intuitively

#setup libraries
thisDir = os.getcwd() 
#Set the right path to my file directory
if ismeg == 0:
    testStim = '/Users/montesinossl/Desktop/BlenderExp/'
else:
    testStim = '/Users/meglab/EExperiments/Sebastian/BlenderMoviePilot/'


#Import conditions file
rundata=data.importConditions(testStim + f'megStimMovie{run_file}.xlsx')
rundata = pd.DataFrame(rundata)

#Initalize lists to fill up with responses & timing information
response_list = []
timeon_list = []
timeoff_list = []
timing_list = []
stimList = rundata['Stimulus']


#Making the window
if iseyetracking:
    import eyetracker 
    fname = f'{participant}S{str(run_file)}'
    et_fname = eyetracker.make_filename(fname=fname)
    # mon = eyetracker.setup_monitor(monitorwidth=screen_width,viewing_distance=view_dist,widthpix=1027,heightpix=768)
    el_tracker,win = eyetracker.connect(fname=et_fname,isfullscreen=isfull, background_col=(-.5, -.5, -.5))
    eyetracker.do_setup(el_tracker)
    # eyetracker.calib(win,el_tracker,fix_size=deg_to_pix(1,win,screen_width,view_dist))
else:
    win = visual.Window(units="pix", fullscr=isfull, color=(-.5, -.5, -.5))

# Wait for start key, q to quit experiment
while True:
    if event.getKeys(keyList=['space']):
        break
    if event.getKeys(keyList='q'):
        win.close()
        core.quit()


#function to add a fixation cross
def fixation_cross(px_width_fixation, px_length_fixation, outline_color_fixation, color_fixation, opacity):
    px_outline_width_fixation = 4 
    #Outline fixation cross Parameters
    line1 = visual.Line(
        win=win,
        units="pix",
        lineColor=outline_color_fixation,
        lineWidth=px_width_fixation, opacity = opacity
    )
 
    line2 = visual.Line(
        win=win,
        units="pix",
        lineColor= outline_color_fixation,
        lineWidth= px_width_fixation, opacity = opacity
    )
    # Fixation Cross Parameters
    line3 = visual.Line(
        win=win,
        units="pix",
        lineColor= color_fixation,
        lineWidth= px_outline_width_fixation, opacity = opacity
    )
 
    line4 = visual.Line(
        win=win,
        units="pix",
        lineColor= color_fixation,
        lineWidth= px_outline_width_fixation, opacity = opacity
    )
    #Drawing the lines relative to the center (lines 1 and 2 are for the outline fixation cross while lines 3 and 4 are for the smaller fixation cross)
    half_line = px_length_fixation/2 
    half_line_small = px_length_fixation/2 - px_outline_width_fixation/2
    line1.start = [-half_line, 0]
    line1.end = [+half_line, 0]
    line2.start = [0, +half_line]
    line2.end = [0, -half_line]
    line3.start = [-half_line_small, 0]
    line3.end = [half_line_small, 0]
    line4.start = [0, +half_line_small]
    line4.end = [0, -half_line_small]
    return [line1, line2, line3, line4]


def drawFix(lines):
    for i in lines:
        i.draw()
        
        
def drawISI(win, lines):
    drawFix(lines)
    return win.flip()
    
    
def check_responses(response_keys):
    pressed=event.getKeys(keyList=response_keys, modifiers=False, timeStamped=False) 
    if pressed:
        if "q" in pressed:
            print('user quit experiment')
            #trialmat.to_csv(f"{fname_data}_quit.csv",index=False)
            if iseyetracking:
                eyetracker.exit(el_tracker,et_fname,results_folder=f'{testStim}/results/')
            win.close()
            core.quit()
        else: 
            return 1
            #timeList.append(last_flip - trialmat.loc[trial,'stim_on']
    else:
        return 0

            
#Draw the stimulus, fixation lines, and photorectoid  
def draw_stim(win, stim, photorect, lines):
    stim.draw()
    photorect.draw()
    drawFix(lines)
    return win.flip()

#Draw a break screen and display how far along in the experiment one is
def draw_break(win, break_counter, break_freq, lines, fixationFrames, index, total_trials):
    way_done = int(((index + 1) / total_trials) * 100)
    break_text = responseScreen = visual.TextStim(win, text='You are ' + str(way_done) + '% done. Press any key to continue', pos=(0, 0), units = 'norm', height=0.07)
    break_text.draw()
    win.flip()
    event.waitKeys(keyList=None)
    for i in range(int(fixationFrames + np.random.randint(0,5,1)[0])):
        drawFix(lines)
        win.flip()
    
def record_response(keys_pressed):
    if len(keys_pressed) > 0:
        return 1
    else:
        return 0
        
def trigger(port,code):
    port.setData(int(code))

#This function is used to generate the list of images that will become the frames for the video
def generate_image_list(start_frame, direction, win, step, num_frames=180): 
    if generationMethod == 1:
        if direction == 'Left':
            if (start_frame > 270 or start_frame < 90):
                step = -step
            elif (start_frame >= 90 and start_frame <= 270):
                step = step
        elif direction == 'Right':
            if (start_frame < 270 and start_frame > 90):
                step = -step
            elif (start_frame <= 90 or start_frame >= 270):
                step = step
    else:
        if direction =='Left':
            step = -step
        else:
            step = step


    images = []
    current_frame = start_frame
    for _ in range(num_frames):
        images.append(possibleImages[current_frame - 1])
        current_frame += step
        if current_frame > 360:
            current_frame = 1
        elif current_frame < 1:
            current_frame = 360
    return images

def extract_number(filename):
    # Assuming the number is between 'frame_' and '.png'
    number_part = filename[len('frame_'):-len('.png')]
    return int(number_part)
    

#Defining text that is displayed and the photorectoid 
photorect_white = visual.Rect(win=win,width = 15,height=15,fillColor='white',pos=(-win.size[0]/2,win.size[1]/2))
photorect_black = visual.Rect(win=win,width = 15,height=15,fillColor='black',pos=(-win.size[0]/2,win.size[1]/2))
localizationText = visual.TextStim(win,text = 'Localizing head position ... \n \n please remain still', units = 'norm', height = 0.07)
trigger_check_text = visual.TextStim(win, text='checking triggers... (press "c" to continue)',units = 'norm', height = 0.07)
introScreen = visual.TextStim(win, text = 'Reminder: In this experiment, you will see a fixation point followed by an movie of a face. Press a button if the face begins rotating back the way it came. Press any button to begin',pos=(0.0, 0.0), units = 'norm', height = 0.07)
responseScreen = visual.TextStim(win, text='Please press any key to continue.', pos=(0, 0), units = 'norm', height = 0.07)
localizationTextEnd = visual.TextStim(win,text = 'You are done! Localizing head position ... \n \n please remain still', units = 'norm', height = 0.07)

win.mouseVisible = False

#Defining Parameters and getting the amount of frames for various experiment components
expFrame = win.getActualFrameRate()
print('framerate is', expFrame)
if expFrame != None:
    frameDur = 1.0 / round(expFrame)
else:
    frameDur = 1.0 / 60.0  # could not measure, so approximated

if islaptop:
    frameDur = 1/120

imDuration = .05 # in seconds
imFrames = imDuration/frameDur
print('imframes are', imFrames)
fixDuration = .5 # seconds of blank screen in between stim
fixationFrames = fixDuration/frameDur

#Info about the monitor
scn_width = 1024 #in px
scn_height = 768 #in px
monitorwidth = 42
monitorheight = 30.5 
viewdist = 80
dva = 15 #angle

#Define the aspect ratio and desired image size based on the image file
stimulus_path = testStim + '/Stimuli/frame_0001.png'  
stimulus = Image.open(stimulus_path)
width, height = stimulus.size
stimAspectRatio = height/width

height_degree = dva
width_degree = dva*stimAspectRatio

#stimAspectRatio = 0.75
dva_width_fixation = 0.2 #in terms of degrees of visual angle
dva_length_fixation = 0.2 # in terms of degrees of visual angle

#Function to convert degrees of visual angle to pixels on the screen
def deg_to_pix(dva=1,view_dist=78.5,screen_width=42, win_size = [1024, 768]):
    size_cm = view_dist*np.tan(np.deg2rad(dva/2))*2
    pix_per_cm = win_size[0]/screen_width
    size_pix = size_cm*pix_per_cm
    return int(np.round(size_pix))
    

px_width_fixation = deg_to_pix(dva_width_fixation,viewdist,monitorwidth) #for fixation
px_length_fixation = deg_to_pix(dva_length_fixation,viewdist,monitorwidth) #for fixation

#Make fixation cross
outline_color_fixation = 'black'
color_fixation = 'white'
opacity = .5
lines = fixation_cross(px_width_fixation, px_length_fixation, outline_color_fixation, color_fixation, opacity)


#calculate stim height using function above
stimHeight = deg_to_pix(height_degree,viewdist,monitorwidth) #531
stimWidth = deg_to_pix(width_degree,viewdist,monitorwidth) #531
#calculate stim width from stim height
#stimWidth = int(np.round(stimHeight * stimAspectRatio)) #398



#Calculating how often there should be a break screen
break_prop = .1
break_freq = int(len(rundata['Stimulus'])*break_prop)
total_trials = int(len(rundata['Stimulus']))
break_counter = 0
all_trials_completed = False


######################################
########LOADING IN IMAGE FILES########
######################################

#PCreate a sorted list of all the image frame files
filenames = []
if ismeg == 1:
    stimuliPath = testStim + 'Stimuli/'
else:
    stimuliPath = testStim + 'Stimuli/resized/'

for filename in os.listdir(stimuliPath):
    if filename.startswith('frame_') and filename.endswith('.png'):
        filenames.append(filename)
filenames.sort(key=extract_number)


#Create a list of ordered psychopy imagestim files
possibleImages = []
for filename in filenames:
    file_path = os.path.join(stimuliPath, filename)  
    possibleImages.append(visual.ImageStim(win, file_path, units = 'pix', pos = (0, 20)))

if length == 0:
    movieLength = [180, 179, 139]
    step = 1
    frames = 180
else:
    movieLength = [90, 89, 69]
    step = 2
    frames = 90
#Now I need a dictionary where each entry is a condition and the list of the image frames I want to display for that condition
imageDict = {}
for condition in rundata['Condition'].unique():
    start_frame, direction = condition.split('_')
    start_frame = int(start_frame)

    #Function to generate the frames I want for each image condition based on the starting frame & direction of movie
    image_list = generate_image_list(start_frame, direction, win, step, frames)

    imageDict[condition] = image_list

    # Check that all the conditions were made
    print(f"Condition: {condition}")
 

######################################
########EXPERIMENT####################
######################################



#Function to test MEG triggers and photorect channel
if ismeg == 1:
    p_port = parallel.ParallelPort(address='0x0378')
if ismeg == 1:
        while 1:
            win.callOnFlip(trigger,port = p_port,code=255)
            pressed = event.getKeys(keyList = ['c'])
            photorect_white.draw()
            trigger_check_text.draw()
            win.flip()
            core.wait(0.1)
            win.callOnFlip(trigger,port = p_port,code=0)
            trigger_check_text.draw()
            win.flip()
            core.wait(0.1)
            if pressed:
                break
if ismeg:
        while 1:
            localizationText.draw()
            win.flip()
            pressed = event.getKeys(keyList = ['a'])
            if pressed:
                break

core.wait(.5)

#Intro and Instructions Screen
introScreen.draw()
win.flip()
introResp = event.waitKeys(keyList = None,timeStamped=True)


#Draw fixation cross before image comes on the screen
for i in range(int(fixationFrames + np.random.randint(0,5,1)[0])):
    drawFix(lines)
    photorect_black.draw()
    last_flip = win.flip()


'''Look at each movie to test the display if needed
testList = rundata['Condition'].unique()
# Function to extract the numerical part and convert it to an integer
def extract_frame_number(frame):
    return int(frame.split('_')[0])

# Sort the list using the extract_frame_number function as the key
sorted_frames = sorted(testList, key=extract_frame_number)

for i in sorted_frames:
    for p in range(movieLength[0]):
        draw_stim(win, imageDict[i][p], photorect_white, lines)
    event.waitKeys()
'''

#Trial loop for experiment
keys_pressed = 0
for index, row in rundata.iterrows():
    print(row['Condition'])
    #Send triggers if in MEG
    if ismeg:
        #win.callOnFlip(trigger, port = p_port, code=code)
        win.callOnFlip(p_port.setData, int(row['Code']))
        if iseyetracking:
            eyetracker.send_message(el_tracker,row['Code'])
    #draw stimulus for 1 frame, get time image is first drawn
    keys_pressed = 0
    stim_on = draw_stim(win, imageDict[row['Condition']][0], photorect_white, lines)
    timeon_list.append(stim_on) #ask lina
    #Draw the stimulus and check for responses
    for i in range(int(imFrames)):
        if i%2 == 0:
            print('here')
            draw_stim(win, imageDict[row['Condition']][0], photorect_white, lines)
        else:
            print('there')
            draw_stim(win, imageDict[row['Condition']][0], photorect_black, lines)
    for i in range(1, movieLength[0]):
        if i%2 == 0:
            print('here')
            draw_stim(win, imageDict[row['Condition']][i], photorect_white, lines)
        else:
            print('there')
            draw_stim(win, imageDict[row['Condition']][i], photorect_black, lines)
    for i in range(int(imFrames)):
        if i%2 == 0:
            print('here')
            draw_stim(win, imageDict[row['Condition']][movieLength[1]], photorect_white, lines)
        else:
            print('there')
            last_flip = draw_stim(win, imageDict[row['Condition']][movieLength[1]], photorect_black, lines)
    timing_list.append(last_flip - stim_on)
    #Should i flip again to get image off screen?
    #If we are in a catch trial, start playing the movie backwards at the end
    if row['Catch'] == 1:
        for i in range(movieLength[1], movieLength[2], -1):
            draw_stim(win, imageDict[row['Condition']][i], photorect_white, lines)
        if keys_pressed==0:
            keys_pressed = check_responses(response_keys)
    print(last_flip - stim_on)
    #Turn off trigger once stimulus is off the screen
    if ismeg:
        win.callOnFlip(p_port.setData, int(0))
    #ISI, check for responses here too
    for i in range(int(fixationFrames + np.random.randint(0,5,1)[0])):
        last_flip = drawISI(win, lines)
        if keys_pressed==0:
            keys_pressed = check_responses(response_keys)
    #Record if they hit any buttons
    response_list.append(keys_pressed)
    if ismeg:
        trigger(port=p_port, code = 0)
    # Draw break screen if '1' in trialmatrix
    if row['Break']:
        draw_break(win, break_counter, break_freq, lines, fixationFrames, index, total_trials)
        break_counter += 1

    #add time1 and time2 into trial output
    print(response_list)


#Localize head-text before ending
while 1:
    localizationTextEnd.draw()
    win.flip()
    pressed = event.getKeys(keyList = ['a'])
    if pressed:
        break

#Record the data and save it in a csv
rundata['Responses'] = response_list
rundata['Timing'] = timing_list
df = pd.DataFrame(response_list, timing_list)
rundata.to_csv(f'extracted_dataMovie{participant}{run_file}.csv', index=False)

#exit the eyetracking
if iseyetracking:
    eyetracker.exit(el_tracker,et_fname,results_folder=f'{testStim}/results/')


