#NPH, December 12, 2023

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
run_file = 1
ismeg = 1
isfull = 1
response_keys = ['1','2','3','4','q']

#setup libraries
thisDir = os.getcwd() 
# #PERSONAL COMPUTER:
if ismeg == 0:   
    testStim = '/Users/montesinossl/Desktop/BlenderExp/'
else:
    testStim = '/Users/meglab/EExperiments/Sebastian/BlenderPilot/'

imDir = '/Users/montesinossl/Desktop/BlenderExp/Stimuli'
rundata=data.importConditions(testStim + f'megStim{run_file}.xlsx')
rundata = pd.DataFrame(rundata)
response_list = []
time_list = []
stimList = rundata['Stimulus']


#WINDOW
win = visual.Window(units="pix", fullscr=isfull, color=(-.3, -.3, -.3))


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
        
        
def drawISI(win, lines, photorect_black):
    photorect_black.draw()
    drawFix(lines)
    return win.flip()
    
    
def check_responses(response_keys):
    pressed=event.getKeys(keyList=response_keys, modifiers=False, timeStamped=False) 
    if pressed:
        if pressed == ['q']:
            print('user quit experiment')
            #trialmat.to_csv(f"{fname_data}_quit.csv",index=False)
            #if iseyetracking:
                #eyetracker.exit(el_tracker,et_fname,results_folder=f'{curr_path}/results/')
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

def draw_break(win, break_text):
    break_text.draw()
    win.flip()
    event.waitKeys(keyList=None)
    
def record_response(keys_pressed):
    if len(keys_pressed) > 0:
        return 1
    else:
        return 0
        
def trigger(port,code):
    port.setData(int(code))
    

#Photorect
photorect_white = visual.Rect(win=win,width = 2,height=2,fillColor='white',pos=(-win.size[0]/2,win.size[1]/2))
photorect_black = visual.Rect(win=win,width = 2,height=2,fillColor='black',pos=(-win.size[0]/2,win.size[1]/2))
localizationText = visual.TextStim(win,text = 'Localizing head position ... \n \n please remain still', units = 'norm', height = 0.07)
trigger_check_text = visual.TextStim(win, text='checking triggers... (press "c" to continue)',units = 'norm', height = 0.07)
introScreen = visual.TextStim(win, text = 'Reminder: In this experiment, you will see a fixation point followed by an image of a face. Press a button if any two face-orientations appear in a row.Press any button to begin',pos=(0.0, 0.0), height=50)
responseScreen = visual.TextStim(win, text='Please press any key to continue.', pos=(0, 0), height=50)
break_text = responseScreen = visual.TextStim(win, text='xx', pos=(0, 0), height=50)



 
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
            if pressed:
                break
if ismeg:
        while 1:
            localizationText.draw()
            win.flip()
            pressed = event.getKeys(keyList = ['a'])
            if pressed:
                break

win.mouseVisible = False
#Intro and Instructions Screen
introScreen.draw()
win.flip()
introResp = event.waitKeys(keyList = None,timeStamped=True)

response_text = ("Please press any key to continue.")

responseScreen = visual.TextStim(win, text=response_text, pos=(0, 0), height=50)
responseScreen.draw()
win.flip()
SubResp = event.waitKeys(keyList=None, timeStamped=True)

#Defining Parameters and frames
expFrame = win.getActualFrameRate()
if expFrame != None:
    frameDur = 1.0 / round(expFrame)
else:
    frameDur = 1.0 / 60.0  # could not measure, so approximated

imDuration = .8 # in seconds
imFrames = imDuration/frameDur
fixDuration = 1 # seconds of blank screen in between stim
fixationFrames = fixDuration/frameDur



scn_width = 1024 #in px
scn_height = 768 #in px
monitorwidth = 42
monitorheight = 30.5 
viewdist = 80
dva = 15 #angle
jitter = 0.5
stimAspectRatio = 0.75
dva_width_fixation = 0.2 #in terms of degrees of visual angle
dva_length_fixation = .2 # in terms of degrees of visual angle
dva_stim_height = 30
#Converts visual angle to image height in pixels
def deg_to_pix(dva,viewdist,scn_height,monitorheight):
    size_cm = viewdist*np.tan(np.deg2rad(dva/2))*2
    pix_per_cm = scn_height/monitorheight
    size_pix = size_cm*pix_per_cm
    return int(np.round(size_pix))

def deg_to_pix(dva=1,view_dist=80,screen_width=42, win_size = [1024, 768]):
    size_cm = view_dist*np.tan(np.deg2rad(dva/2))*2
    pix_per_cm = win_size[0]/screen_width
    size_pix = size_cm*pix_per_cm
    return int(np.round(size_pix))
    
px_width_fixation = deg_to_pix(dva_width_fixation,viewdist,monitorwidth) #for fixations
px_length_fixation = deg_to_pix(dva_length_fixation,viewdist,monitorwidth) #for fixations
outline_color_fixation = 'black'
color_fixation = 'white'
opacity = .5
lines = fixation_cross(px_width_fixation, px_length_fixation, outline_color_fixation, color_fixation, opacity)


#calculate stim height using function above

stimHeight = deg_to_pix(dva,viewdist,monitorwidth) #531
#calculate stim width from stim height
stimWidth = int(np.round(stimHeight * stimAspectRatio)) #398


#calculate jitter distance
jitterDist = deg_to_pix(jitter,viewdist,scn_height,monitorheight)
jitterDistX = jitterDist * math.cos(math.pi/4)
jitterDistY = jitterDist * math.sin(math.pi/4)

posOptions = [(0,0),(0,jitterDist),(0,-jitterDist),(jitterDist,0),(-jitterDist,0),(jitterDistX,jitterDistY),(jitterDistX,-jitterDistY),(-jitterDistX,jitterDistY),(-jitterDistX,-jitterDistY)]

#############################################################################
####Experiment #####
imOnset = []
fixOnset = []
data = []
keys_pressed = []
break_prop = .1
break_freq = int(len(rundata['Stimulus'])*break_prop)
break_counter = 0
all_trials_completed = False

for i in range(int(fixationFrames + np.random.randint(0,5,1)[0])):
    drawFix(lines)
    photorect_black.draw()
    last_flip = win.flip()

for index, row in rundata.iterrows():
    stim_filename = row['Stimulus']
    code = row['code']
    imageStimulus = visual.ImageStim(win, stim_filename, size=(stimHeight, stimWidth), units = 'pix')
    #imageStimulus.draw()
    #win.flip()
    #event.waitKeys(keyList=None)
    keys_pressed = []
    # Present the image frames
    #if break_counter < break_freq:
        #draw_break(win, break_text)
    if ismeg:
        #win.callOnFlip(trigger, port = p_port, code=code)
        win.callOnFlip(p_port.setData, int(code))
        last_flip = draw_stim(win, imageStimulus, photorect_white, lines)
        win.flip()
    keys_pressed = 0
    for i in range(int(imFrames) - 1):
        #imageStimulus.draw()
        #photorect_white.draw()
        last_flip = draw_stim(win, imageStimulus, photorect_white, lines)
        if keys_pressed==0:
            keys_pressed = check_responses(response_keys)
    if ismeg:
        win.callOnFlip(p_port.setData, int(0))
    for i in range(int(fixationFrames + np.random.randint(0,5,1)[0])):
        last_flip = drawISI(win, lines, photorect_black)
        #check_responses(response_keys)
    response_list.append(keys_pressed)
    if ismeg:
        trigger(port=p_port, code = 0)


rundata['Responses'] = response_list
df = pd.DataFrame(response_list)
rundata.to_csv(f'extracted_data{run_file}.csv', index=False)





# End of the experiment


#first fixation

#for index, row in rundata.iterrows():
#    quitExperiment(win)
#    stim_filename = row['Stimulus']
#    videoStimulus = visual.MovieStim(win, stim_filename, size=(1.5*stimHeight, 1.5*stimWidth))
#    for i in range(int(fixationFrames)):
#        fix.draw()
#        win.flip()
#    for i in range(int(movieFrames)):
#        videoStimulus.draw()
#        win.flip()
    #win.flip()

'''
# Dialog box
while True:
    inputDict = {'subjID': 'test', 'runfile' : '1', 'run number': '1'}
    inputDialog = gui.DlgFromDict(inputDict, title="Enter subject info", order=['subjID', 'runfile', 'run number'])

    if inputDialog.OK:
        print('User pressed OK')
        break 
    else:
        print('User cancelled')
        core.quit()
        sys.exit()

# Store the information from dialog box
subjID = inputDialog.dictionary['subjID']
run = inputDialog.dictionary['run number']
fname = subjID + run
'''
'''
#Fixation
fixCol = [0,0,0] #black
fixRadius = 400 #in pixels
fix = visual.TextStim(win, text = '+', pos = (0, 0), height=50)
'''
'''
    for i in range(int(fixationFrames)):
        fix.draw()
        win.flip()

    for i in range(int(movDuration)):
        videoStimulus.draw()
        win.flip()
    #####  output file
    trial_info = {
    'Subject': subjID,
    'Task': 'Emotion',  # Assuming it's the same for all trials
    'RunNum': run,
    'TrialNum': index + 1,  # Assuming index starts from 0
    'Filename': stim_filename,
    # Add other relevant trial information here based on your experiment logic
    # Example: 'ActorCode': ..., 'EmotionType': ..., etc.
    }

    outputData.append(trial_info) 
    print(outputData)

    # Check if all trials are completed
    if index == len(rundata) - 1:
        all_trials_completed = True

# After the loop ends, exit the experiment
if all_trials_completed:
    print("All trials completed. Exiting the experiment.")

# After all trials are done, write the data to a file (example using Pandas):
output_df = pd.DataFrame(outputData)
output_df.to_csv('Desktop/Natalia_Shruti_FaMo/Data/' + subjID + '_' + run + '_' + fname +'_results.csv', index=False)
'''