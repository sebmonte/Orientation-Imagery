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
participant = 3
run_file = 1 #change every run
fname = f'{participant}_{run_file}movie'
ismeg = 1
isfull = 1
iseyetracking = 1
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

output_folder = '/Users/meglab/EExperiments/Sebastian/BlenderMoviePilot/Data/eyetracking'
#Import conditions file
rundata=data.importConditions(testStim + f'megStimMovie{run_file}.xlsx')
rundata = pd.DataFrame(rundata)

#Initalize lists to fill up with responses & timing information
response_list = []
timeon_list = []
timeoff_list = []
timing_list = []
stimList = rundata['Stimulus']

#WINDOW

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
        if 'q' in pressed:
            print('user quit experiment')
            #trialmat.to_csv(f"{fname_data}_quit.csv",index=False)
            #if iseyetracking:
                #eyetracker.exit(el_tracker,et_fname,results_folder=f'{testStim}/results/')
            win.close()
            core.quit()
        else: 
            return 1
            #timeList.append(last_flip - trialmat.loc[trial,'stim_on']
    else:
        return 0

            
#Draw the stimulus, fixation lines, and photorectoid  
def draw_stim(win, stim, photorect_white, lines):
    stim.draw()
    photorect_white.draw()
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

def eyetracker_exit(el_tracker,fname,output_folder):
    el_tracker.stopRecording()
    # Close the edf data file on the Host
    # Put tracker in Offline mode
    el_tracker.setOfflineMode()

    # Clear the Host PC screen and wait for 500 ms
    el_tracker.sendCommand('clear_screen 0')
    pylink.msecDelay(500)

    # Close the edf data file on the Host
    el_tracker.closeDataFile()

    # Show a file transfer message on the screen
    print('EDF data is transferring from EyeLink Host PC...')
    el_tracker.receiveDataFile(fname + '.edf', output_folder +'/' + fname +'.edf')

    # Close the link to the tracker.
    el_tracker.close()
    

#Defining text that is displayed and the photorectoid 
photorect_white = visual.Rect(win=win,width = 2,height=2,fillColor='white',pos=(-win.size[0]/2,win.size[1]/2))
photorect_black = visual.Rect(win=win,width = 2,height=2,fillColor='black',pos=(-win.size[0]/2,win.size[1]/2))
photorect_catch = visual.Rect(win=win,width = 2,height=2,fillColor=(-.5, -.5, -.5),pos=(-win.size[0]/2,win.size[1]/2))
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

startDur = .15
stimDur = .05


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

if iseyetracking:
    import pylink
    from EyeLinkCoreGraphicsPsychoPy import EyeLinkCoreGraphicsPsychoPy
    
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

if iseyetracking == 1:

    # STEP 1: Connect to the EyeLink Host PC
    pylink.closeGraphics()
    try:
        el_tracker = pylink.EyeLink("100.1.1.1")
    except RuntimeError as error:
        print('ERROR:', error)
        core.quit()
        sys.exit()

    # STEP 2: Open an EDF data file on the Host PC
    try:
        el_tracker.openDataFile(fname)
    except RuntimeError as err:
        print('ERROR:', err)
        # close the link if we have one open
        if el_tracker.isConnected():
            el_tracker.close()
        core.quit()
        sys.exit()

    # STEP 3: Configure the tracker
    el_tracker.setOfflineMode()
    
    # Get the software version:  1-EyeLink I, 2-EyeLink II, 3/4-EyeLink 1000, 5-EyeLink 1000 Plus, 6-Portable DUO
    vstr = el_tracker.getTrackerVersionString()
    eyelink_ver = int(vstr.split()[-1].split('.')[0])
    
    # print out some version info in the shell
    print('Running experiment on %s, version %d' % (vstr, eyelink_ver))

    # File and Link data control
    
    # what eye events to save in the EDF file
    file_event_flags = 'LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON,INPUT'
    
    # what eye events to make available over the link
    link_event_flags = 'LEFT,RIGHT,FIXATION,SACCADE,BLINK,BUTTON,FIXUPDATE,INPUT'
    
    # what sample data to save in the EDF data file and to make available
    if eyelink_ver > 3:
        file_sample_flags = 'LEFT,RIGHT,GAZE,HREF,RAW,AREA,HTARGET,GAZERES,BUTTON,STATUS,INPUT'
        link_sample_flags = 'LEFT,RIGHT,GAZE,GAZERES,AREA,HTARGET,STATUS,INPUT'
    else:
        file_sample_flags = 'LEFT,RIGHT,GAZE,HREF,RAW,AREA,GAZERES,BUTTON,STATUS,INPUT'
        link_sample_flags = 'LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,INPUT'
    el_tracker.sendCommand("file_event_filter = %s" % file_event_flags)
    el_tracker.sendCommand("file_sample_data = %s" % file_sample_flags)
    el_tracker.sendCommand("link_event_filter = %s" % link_event_flags)
    el_tracker.sendCommand("link_sample_data = %s" % link_sample_flags)

    # Choose a calibration type, H3, HV3, HV5, HV13 (HV = horizontal/vertical),
    el_tracker.sendCommand("calibration_type = HV5")

    
    # STEP 4: set up a graphics environment for calibration
    win_eye=visual.Window(color='Gray',colorSpace='rgb',units='pix',checkTiming=True,fullscr=1,winType='pyglet')
    scn_width, scn_height = win_eye.size

    # Pass the display pixel coordinates (left, top, right, bottom) to the tracker
    el_coords = "screen_pixel_coords = 0 0 %d %d" % (scn_width - 1, scn_height - 1)
    el_tracker.sendCommand(el_coords)

    # Write a DISPLAY_COORDS message to the EDF file
    dv_coords = "DISPLAY_COORDS  0 0 %d %d" % (scn_width - 1, scn_height - 1)
    el_tracker.sendMessage(dv_coords)

    # Change the proportion of the screen used for calibration and validation
    # default values are 0.88 0.83
    el_tracker.sendCommand("calibration_area_proportion 0.5 0.5")
    el_tracker.sendCommand("validation_area_proportion 0.5 0.5")


    # Configure a graphics environment (genv) for tracker calibration
    genv = EyeLinkCoreGraphicsPsychoPy(el_tracker, win_eye)
    print(genv)  # print out the version number of the CoreGraphics library

    # Set background and foreground colors for the calibration target
    foreground_color = (-1, -1, -1) #black
    background_color = win_eye.color
    genv.setCalibrationColors(foreground_color, background_color)

    # Request Pylink to use the PsychoPy window we opened above for calibration
    pylink.openGraphicsEx(genv)
    
    # Calibrate EyeLink
    if iseyetracking == 1:
        try:
            el_tracker.doTrackerSetup()
        except RuntimeError as err:
            print('ERROR:', err)
            el_tracker.exitCalibration()
        
        # get a reference to the currently active EyeLink connection
        el_tracker = pylink.getEYELINK()
        # put the tracker in the offline mode first
        el_tracker.setOfflineMode()
        # clear the host screen before we draw the fixation square
        el_tracker.sendCommand('clear_screen 0')
        # Start recording 
        el_tracker.startRecording(1, 1, 1, 1) 

    #close the eyetracking window so we can go back to the task
    win_eye.close()
core.wait(.5)

if ismeg:
        while 1:
            localizationText.draw()
            win.flip()
            pressed = event.getKeys(keyList = ['a'])
            if pressed:
                break

#Intro and Instructions Screen
introScreen.draw()
win.flip()
introResp = event.waitKeys(keyList = None,timeStamped=True)


#Draw fixation cross before image comes on the screen
for i in range(int(fixationFrames + np.random.randint(0,5,1)[0])):
    drawFix(lines)
    #photorect_black.draw()
    last_flip = win.flip()

'''
#Look at each movie to test the display if needed
testList = rundata['Condition'].unique()
# Function to extract the numerical part and convert it to an integer
def extract_frame_number(frame):
    return int(frame.split('_')[0])

# Sort the list using the extract_frame_number function as the key
sorted_frames = sorted(testList, key=extract_frame_number)

for i in sorted_frames:
    for p in range(movieLength[0]):
        print(i)
        draw_stim(win, imageDict[i][p], photorect_white, lines)
    event.waitKeys()
'''

#Trial loop for experiment
keys_pressed = 0
index = 0
frameTolerance = .001
#for index, row in rundata.iterrows()

for index, row in rundata.iterrows():
    print(index)
    print(row['Condition'])
    #Send triggers if in MEG
    if ismeg:
        #win.callOnFlip(trigger, port = p_port, code=code)
        win.callOnFlip(p_port.setData, int(row['Code']))
        if iseyetracking:
            trial = row['Code']
            el_tracker.sendMessage('TRIALID %d' % trial)
            status_msg = 'TRIAL number %d' % trial
            el_tracker.sendCommand("record_status_message '%s'" % status_msg)
    keys_pressed = 0

    orientationList = imageDict[row['Condition']][::3]

    trialClock = core.Clock()
    movie_loop = win.getFutureFlipTime(clock = trialClock)
    for i in range(len(orientationList)):
        last_flip = draw_stim(win, orientationList[i], photorect_white, lines)
        while trialClock.getTime()<= movie_loop + stimDur*(i+1) - frameTolerance:
            if keys_pressed==0:
                keys_pressed = check_responses(response_keys)
    trialTime = trialClock.getTime() - movie_loop
    if row['Catch'] == 1:
        for i in range(len(orientationList) - 1, 50, -1):
            catchClock = core.Clock()
            draw_stim(win, orientationList[i], photorect_catch, lines)
            while catchClock.getTime()<= stimDur:
                if keys_pressed==0:
                    keys_pressed = check_responses(response_keys)
    print(trialTime)
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
    timing_list.append(trialTime)
    if ismeg:
        trigger(port=p_port, code = 0)
    # Draw break screen if '1' in trialmatrix
    if row['Break']:
        draw_break(win, break_counter, break_freq, lines, fixationFrames, index, total_trials)
        break_counter += 1

    #add time1 and time2 into trial output
    index += 1



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
print(rundata)

#Exit eyetracking
if iseyetracking == 1:
    try:
        eyetracker_exit(el_tracker,fname,output_folder)
    except RuntimeError as error:
        print('exiting eyetracker did not work...')


