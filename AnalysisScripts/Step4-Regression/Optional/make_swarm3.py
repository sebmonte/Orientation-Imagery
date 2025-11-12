# Open a file to write the commands
all_subjs = ['S01', 'S02', 'S03', 'S04', 'S05', 'S06', 'S07', 'S08', 'S09', 'S10', 'S11', 'S12', 'S13', 'S14', 'S15', 'S16', 'S17', 'S18', 'S19', 'S20']

output_file = "/data/OrientationDecoding/code/swarm3.sh"

with open(output_file, "w") as f:
    for subjid in all_subjs:
        for t in range(961):
            statement = f"module load mne;python ProduceErrorCross_Ridge.py -bids_dir /data/OrientationDecoding/bids_dir/ -S {subjid} -traintime {t}\n"
            f.write(statement)


