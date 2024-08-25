import os
import json
import ffmpeg
import glob
from ffprobe import FFProbe

user_path = "C:\\Users\\Lambda23\\Documents\\programming\\python\\strtomon"
all_files = user_path + "\\**\\*.*"
save_path = os.path.abspath(os.path.join(user_path, os.pardir)) + "\\E2S-Utils"
print(save_path)

if save_path

for filename in glob.iglob(all_files, recursive=True):
    if (filename.endswith(".wav")):
        print(filename)
        media = FFProbe(filename)
        for stream in media.streams:
            if stream.is_audio():
                if stream.__dict__["channels"] == '2':
                    out_filename = filename.strip(".wav") + "-mono.wav"
                    (
                        ffmpeg
                        .input(filename)
                        .output(out_filename, ac='1') #os.system(f'ffmpeg -i {filename} -ac 1 {out_filename}')
                        .overwrite_output()
                        .run(capture_stdout=True, capture_stderr=True)
                    )
                else:
                    print("Number of channels do not match. \'" + stream.__dict__["channels"] + "\' is not 2. Skipping...")
                    continue
        
    else:
        continue
