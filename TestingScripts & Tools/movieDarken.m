% Choose multiple mp4 files

[files, path] = uigetfile('*.mp4', 'Select the movies', 'MultiSelect', 'on');



if ~iscell(files)

    if isequal(files, 0)

        disp('User selected Cancel');

        return;

    else

        files = {files};

    end

end



% Factor by which to darken each frame (e.g., 0.7 to retain 70% brightness)

darkeningFactor = 0.7;



for fileIdx = 1:length(files)

    % Create video reader and writer objects

    videoFile = fullfile(path, files{fileIdx});

    inputVideo = VideoReader(videoFile);

    [~,name,~] = fileparts(videoFile);

    outputVideoFile = fullfile(path, [name '_darkened.mp4']);

    outputVideo = VideoWriter(outputVideoFile, 'MPEG-4');

    open(outputVideo);



    % Loop through each frame

    while hasFrame(inputVideo)

        % Read frame

        frame = readFrame(inputVideo);



        % Darken the frame

        darkenedFrame = uint8(double(frame) * darkeningFactor);



        % Write darkened frame to the new video

        writeVideo(outputVideo, darkenedFrame);

    end



    % Close the output video file

    close(outputVideo);



    fprintf('Processed %s and saved as %s\n', files{fileIdx}, [name '_darkened.mp4']);

end