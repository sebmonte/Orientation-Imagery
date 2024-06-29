# Orientation-Imagery
Scripts for an MEG project testing generalization from static to dynamic faces &amp; videos

***ConditionsFileGeneration***
Folder that contains scripts that generate the conditions files used in the experiment

***Stimuli & Trialsheets***
Contains the stimuli for the experiments and the logfiles for each subject

***Testing Scripts***
Scripts for handling and testing various components of the experiment

BlenderMovieScriptTimingTest.py
	Variant of the script that turns the photodiode on and off for every new frame of the movie. Doing this to test the timing and hopefully fix issues with it

compressImages.py
	Takes large png files and makes them smaller so the stimulus computer can load them in more quickly.

framestomovies.py
	Testing script to make sure I am creating the list of frames that comprise movie presentations in BlenderScriptMovie.py correctly

VisualAngleConversion&Testing
	Script to test the size of images in visual angle on the screen, used to determine what size I want for the faces in terms of degree of visual angle.
