#Script to test the output of squares with various specified degrees of visual angle,
#and then save out pixel values. I used this to determine the size I need to make my images in pixels 


from PIL import Image
from psychopy import visual, event, core, gui, data, logging, parallel
import numpy as np

scn_width = 1024 #in px
scn_height = 768 #in px
monitorwidth = 42
monitorheight = 30.5 
viewdist = 80
dva = 5 #angle
ismeg = 0
isFull = 0

if ismeg == 0:   
    testStim = '/Users/montesinossl/Desktop/BlenderExp/'
else:
    testStim = '/Users/meglab/EExperiments/Sebastian/BlenderPilot/'

#Define the aspect ratio and desired image size based on the image file
stimulus_path = testStim + '/Stimuli/frame_0001.jpg'  
stimulus = Image.open(stimulus_path)
width, height = stimulus.size
stimAspectRatio = height/width

dva_height = dva
dva_width = dva*stimAspectRatio


#Function to convert degrees of visual angle to pixels on the screen
def deg_to_pix(dva=1,view_dist=78.5,screen_width=42, win_size = [1024, 768]):
    size_cm = view_dist*np.tan(np.deg2rad(dva/2))*2
    pix_per_cm = win_size[0]/screen_width
    size_pix = size_cm*pix_per_cm
    return int(np.round(size_pix))

    

width = deg_to_pix(dva_width,viewdist,monitorwidth) #for fixation
height = deg_to_pix(dva_height,viewdist,monitorwidth) #for fixation
print(width)
print(height)


win = visual.Window(units="pix", fullscr=isFull, color=(.5, .5, .5))
testSquare = visual.Rect(win, height = height, width = width, units = 'pix', fillColor=(-1, -1, -1))

testSquare.draw()
win.flip()
event.waitKeys()
win.close()
