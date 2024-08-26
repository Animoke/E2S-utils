import os, sys
import json
import ffmpeg
import glob
import shutil
import datetime
from ffprobe import FFProbe

cur_time = datetime.datetime.now()
user_path = "C:\\Users\\Lambda23\\Documents\\programming\\python\\E2S-utils"
all_files = user_path + "\\**\\*.*"
backup_path = os.path.abspath(os.path.join(user_path, os.pardir)) + "\\Backup-E2S-utils" + cur_time.strftime('%Y-%m-%d_%H-%M-%S')

#if not os.path.isdir(save_path):
#    print("save_path not found. Making directory...")
#    os.makedirs(save_path)

#shutil.copytree(user_path, backup_path)

def stereo_to_mono():
    for filename in glob.iglob(all_files, recursive=True):
        if (filename.endswith(".wav")):
            print(filename)
            media = FFProbe(filename)
            for stream in media.streams:
                if stream.is_audio():
                    if stream.__dict__["channels"] == '2':
                        out_filename = filename + "mono-e2s.wav"
                        (
                            ffmpeg
                            .input(filename)
                            .output(out_filename, ac='1') #os.system(f'ffmpeg -i {filename} -ac 1 {out_filename}')
                            .overwrite_output()
                            .run(capture_stdout=True, capture_stderr=True) #Quiet mode
                        )
                        shutil.move(out_filename, filename)
                    else:
                        print("Number of channels do not match. \'" + stream.__dict__["channels"] + "\' is not 2. File is probably mono. Skipping...")
                        continue              
        else:
            continue

def speed_doubler():
    print("Speeding up samples...")
    for filename in glob.iglob(all_files, recursive=True):
        if (filename.endswith(".wav")):
            print(filename)
            out_filename = filename + "2x-speed-e2s.wav"
            (
                ffmpeg
                .input(filename)
                .filter('atempo', 2)
                .output(out_filename) #os.system(f'ffmpeg -i {filename} -ac 1 {out_filename}')
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True) #Quiet mode
            )
            shutil.move(out_filename, filename)
        else:
            continue

def main():
    if sys.argv[1] == "--convert-mono" or sys.argv[1] == "-m":
        stereo_to_mono()
    elif sys.argv[1] == "--speed" or sys.argv[1] == "-s":
        speed_doubler()
    elif sys.argv[1] == "--all" or sys.argv[1] == "-a" or len(sys.argv) <= 1:
        stereo_to_mono()
        speed_doubler()
    else:
        print("Input error")

    #shutil.copytree(user_path, backup_path)

    #cur_time = datetime.datetime.now()
    #user_path = "C:\\Users\\Lambda23\\Documents\\programming\\python\\E2S-utils"
    #all_files = user_path + "\\**\\*.*"
    #backup_path = os.path.abspath(os.path.join(user_path, os.pardir)) + "\\Backup-E2S-utils" + cur_time.strftime('%Y-%m-%d_%H-%M-%S')

if __name__ == '__main__':
    main()