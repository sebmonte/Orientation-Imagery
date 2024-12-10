#Script to display still images of faces at various orientations

#setup libraries
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
participant = 1
run_file = 4
fname = f'{participant}_{run_file}still'
ismeg = 1
isfull = 1
iseyetracking = 1
islaptop = 0
response_keys = ['1','2','3','4','q']

#setup libraries
thisDir = os.getcwd() 
# #PERSONAL COMPUTER:
if ismeg == 0:   
    testStim = '/Users/montesinossl/Desktop/BlenderExp/'
else:
    testStim = '/Users/meglab/EExperiments/Sebastian/BlenderPilot/'

output_folder = '/Users/meglab/EExperiments/Sebastian/BlenderMoviePilot/Data/eyetracking'

imDir = '/Users/montesinossl/Desktop/BlenderExp/Stimuli'
rundata=data.importConditions(testStim + f'megStim{run_file}.xlsx')
rundata = pd.DataFrame(rundata)
response_list = []
timeon_list = []
timeoff_list = []
stimList = rundata['Stimulus']


#WINDOW

win = visual.Window(units="pix", fullscr=isfull, color=(-.5, -.5, -.5))

# Wait for start key
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
        if pressed == ['q']:
            print('user quit experiment')
            #trialmat.to_csv(f"{fname_data}_quit.csv",index=False)
            #if iseyetracking:
           #     eyetracker.exit(el_tracker,et_fname,results_folder=f'{testStim}/results/')
            win.close()
            core.quit()
        else: 
            return 1
            #timeList.append(last_flip - trialmat.loc[trial,'stim_on']
    else:
        return 0

            
    
def draw_stim(win, stim, photorect_white, lines):
    stim.draw()
    photorect_white.draw()
    drawFix(lines)
    return win.flip()

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
    

#Photorect
photorect_white = visual.Rect(win=win,width = 2,height=2,fillColor='white',pos=(-win.size[0]/2,win.size[1]/2))
photorect_black = visual.Rect(win=win,width = 2,height=2,fillColor='black',pos=(-win.size[0]/2,win.size[1]/2))
localizationText = visual.TextStim(win,text = 'Localizing head position ... \n \n please remain still', units = 'norm', height = 0.07)
trigger_check_text = visual.TextStim(win, text='checking triggers... (press "c" to continue)',units = 'norm', height = 0.07)
introScreen = visual.TextStim(win, text = 'Reminder: In this experiment, you will see a fixation point followed by an image of a face. Press a button if any two face-orientations appear in a row. Press any button to begin',pos=(0.0, 0.0), units = 'norm', height = 0.07)
responseScreen = visual.TextStim(win, text='Please press any key to continue.', pos=(0, 0), units = 'norm', height = 0.07)
localizationTextEnd = visual.TextStim(win,text = 'You are done! Localizing head position ... \n \n please remain still', units = 'norm', height = 0.07)

win.mouseVisible = False

#Defining Parameters and frames
expFrame = win.getActualFrameRate()
print('framerate is', expFrame)
if expFrame != None:
    frameDur = 1.0 / round(expFrame)
else:
    frameDur = 1.0 / 60.0  # could not measure, so approximated

if islaptop:
    frameDur = 1/120

imDuration = .3 # in seconds
imFrames = imDuration/frameDur
print('imdur is', imFrames)
fixDuration = .5 # seconds of blank screen in between stim
fixationFrames = fixDuration/frameDur


scn_width = 1024 #in px
scn_height = 768 #in px
monitorwidth = 42
monitorheight = 30.5 
viewdist = 80
dva = 15 #angle

stimulus_path = testStim + '/Stimuli/frame_0001.png'  # Replace with the actual path to your image file
stimulus = Image.open(stimulus_path)
# Get the dimensions
width, height = stimulus.size
stimAspectRatio = height/width

height_degree = dva
width_degree = dva*stimAspectRatio

#stimAspectRatio = 0.75
dva_width_fixation = 0.2 #in terms of degrees of visual angle
dva_length_fixation = 0.2 # in terms of degrees of visual angle
dva_stim_height = 30

if iseyetracking:
    import pylink
    from EyeLinkCoreGraphicsPsychoPy import EyeLinkCoreGraphicsPsychoPy

def deg_to_pix(dva=1,view_dist=80,screen_width=42, win_size = [1024, 768]):
    size_cm = view_dist*np.tan(np.deg2rad(dva/2))*2
    pix_per_cm = win_size[0]/screen_width
    size_pix = size_cm*pix_per_cm
    return int(np.round(size_pix))
    
px_width_fixation = deg_to_pix(dva_width_fixation,viewdist,monitorwidth) #for fixation
px_length_fixation = deg_to_pix(dva_length_fixation,viewdist,monitorwidth) #for fixation
outline_color_fixation = 'black'
color_fixation = 'white'
opacity = .5
lines = fixation_cross(px_width_fixation, px_length_fixation, outline_color_fixation, color_fixation, opacity)


#calculate stim height using function above
stimHeight = deg_to_pix(height_degree,viewdist,monitorwidth) #531
stimWidth = deg_to_pix(width_degree,viewdist,monitorwidth) #531
#calculate stim width from stim height
#stimWidth = int(np.round(stimHeight * stimAspectRatio)) #398


#############################################################################
####Experiment #####
imOnset = []
fixOnset = []
break_prop = .1
break_freq = int(len(rundata['Stimulus'])*break_prop)
total_trials = int(len(rundata['Stimulus']))
break_counter = 0
all_trials_completed = False


 
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



for i in range(int(fixationFrames + np.random.randint(0,5,1)[0])):
    drawFix(lines)
    photorect_black.draw()
    last_flip = win.flip()

imageList = []
for i in range(len(rundata['Code'].unique())):
    imageList.append(visual.ImageStim(win, rundata.loc[rundata['Code']==i+1,'Stimulus'].to_list()[0], size=(stimHeight, stimWidth), units = 'pix', pos = (0, 20)))


#Gclock = core.MonotonicClock()
keys_pressed = 0
for index, row in rundata.iterrows():
    #Send triggers if in MEG, draw stimulus for 1 frame
    if ismeg:
        #win.callOnFlip(trigger, port = p_port, code=code)
        win.callOnFlip(p_port.setData, int(row['Code']))
        if iseyetracking:
            trial = row['Code']
            el_tracker.sendMessage('TRIALID %d' % trial)
            status_msg = 'TRIAL number %d' % trial
            el_tracker.sendCommand("record_status_message '%s'" % status_msg)
    stim_on = draw_stim(win, imageList[row['Code'] - 1], photorect_white, lines)
    timeon_list.append(stim_on) #ask lina
    #Draw the stimulus and check for responses
    keys_pressed = 0
    for i in range(int(imFrames) - 1):
        last_flip = draw_stim(win, imageList[row['Code'] - 1], photorect_white, lines)
        if keys_pressed==0:
            keys_pressed = check_responses(response_keys)
    #print(last_flip - stim_on)
    #Turn off trigger once stimulus is off the screen
    if ismeg:
        win.callOnFlip(p_port.setData, int(0))
    #ISI, check for responses here too
    for i in range(int(fixationFrames + np.random.randint(0,5,1)[0])):
        last_flip = drawISI(win, lines)
        if keys_pressed==0:
            keys_pressed = check_responses(response_keys)
    response_list.append(keys_pressed)
    if ismeg:
        trigger(port=p_port, code = 0)
       # Draw break screen if '1' in trialmatrix
    if row['Break']:
        draw_break(win, break_counter, break_freq, lines, fixationFrames, index, total_trials)
        break_counter += 1

    #print(response_list)
    #add time1 and time2 into trial output

while 1:
    localizationTextEnd.draw()
    win.flip()
    pressed = event.getKeys(keyList = ['a'])
    if pressed:
        break

rundata['Responses'] = response_list
df = pd.DataFrame(response_list)
rundata.to_csv(f'extracted_dataStill{participant}{run_file}.csv', index=False)


if iseyetracking == 1:
    try:
        eyetracker_exit(el_tracker,fname,output_folder)
    except RuntimeError as error:
        print('exiting eyetracker did not work...')



