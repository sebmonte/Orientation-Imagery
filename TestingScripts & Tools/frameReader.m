% Specify the folder where your videos are located
folderPath = './';  % Change this to the path of your video folder

% Get a list of all video files in the folder
videoFiles = dir(fullfile(folderPath, '*.mp4'));  % You can specify the video file format here

% Initialize a cell array to store video frame counts and video names
frameCounts = cell(length(videoFiles), 1);
videoNames = cell(length(videoFiles), 1);

% Loop through each video file and count frames
for i = 1:length(videoFiles)
    videoFileName = fullfile(folderPath, videoFiles(i).name);
    
    % Read the video and count frames
    videoObj = VideoReader(videoFileName);
    frameCounts{i} = videoObj.NumberOfFrames;
    videoNames{i} = videoFiles(i).name;
end

% Display the results
for i = 1:length(videoFiles)
    disp([videoNames{i} ' has ' num2str(frameCounts{i}) ' frames.']);
end
