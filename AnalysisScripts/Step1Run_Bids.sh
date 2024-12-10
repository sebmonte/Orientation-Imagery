set raw_path = '/System/Volumes/Data/misc/data12/sjapee/Sebastian-OrientationImagery/Data/20240930'
set participant = S01
set meg_hash = ETWNABKX


#This worked with set raw path = '/System/Volumes/Data/misc/data12/sjapee/Sebastian-OrientationImagery/Data/20240911/'
#Set participant = P1 and set meg_hash = MEG
#Can add a variable that says which runs are dynamic, can loop over the folders that contain them and change the name

make_meg_bids.py -meg_input_dir $raw_path -bids_id $participant -subjid_input $meg_hash -ignore_mri_checks -ignore_eroom -mri_bsight $raw_path/$participant.anat.nii 

#get rid of ignore mri checks flag, add electrodes file

make_meg_bids.py -meg_input_dir $raw_path -bids_id $participant -subjid_input $meg_hash -ignore_eroom -mri_bsight $raw_path/$participant.anat.nii -mri_bsight_elec $raw_path/"${participant}_electrodes.txt"

