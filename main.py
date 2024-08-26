import os, sys, argparse, datetime
import ffmpeg
import glob
import shutil, re
from ffprobe import FFProbe

# Modify path here
user_path = "C:\\Users\\Path\\To\\E2S_SD\\Sample"

cur_time = datetime.datetime.now()
all_files = user_path + "\\**\\*.*"
backup_path = os.path.abspath(os.path.join(user_path, os.pardir)) + "\\Backup-E2S-utils_" + cur_time.strftime('%Y-%m-%d_%H-%M-%S')

def stereo_to_mono():
    i = 0
    print("[CONVERT_MONO] Conversion merges both stereo tracks into one.")
    for filename in glob.iglob(all_files, recursive=True):
        if (filename.endswith(".wav")):
            print("[CONVERT_MONO] " + filename)
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
                        i = i + 1
                    else:
                        print("[INFO] Number of channels do not match. \'" + stream.__dict__["channels"] + "\' is not 2. File is probably mono. Skipping...")
                        continue              
        else:
            continue
    print("[CONVERT_MONO]", i, "files converted")

def speed_convert(speed):
    i = 0
    print("[INFO][SPEED] File speed set to", speed)
    for filename in glob.iglob(all_files, recursive=True):
        if (filename.endswith(".wav")):
            media = FFProbe(filename)
            media_probe = str(media.__dict__)
            sample_rate_d = re.search(r"\d{5,6}Hz", media_probe)
            sample_rate = int(re.sub(r"\D", "", sample_rate_d.group()))
            print("[SPEED] " + filename + " | Speed:", speed, "| Sample Rate:", sample_rate, "Hz")
            out_filename = filename + "-speed-e2s.wav"
            (
                ffmpeg
                .input(filename)
                .filter('asetrate', sample_rate * speed)
                .output(out_filename, ar='44100')
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True) #Quiet mode
            )
            shutil.move(out_filename, filename)
            i = i + 1
        else:
            continue
    print("[SPEED]", i, "files converted")

def main():
    parser = argparse.ArgumentParser(description="Convert all files in sub-directories to mono, with adjustable speed. Made for Korg machines")
    parser.add_argument("-m", "--convert-mono", help="Convert to mono", action='store_true')
    parser.add_argument("-s", "--speed", help="Speed selection (0.5-2.0)", action='store', type=float, default=2)
    parser.add_argument("-a", "--all", help="Do everything (default speed: 2) [DEFAULT]", action='store_true')
    args = parser.parse_args()

    print("[E2S-Utils] Backing up...")
    try:
        shutil.copytree(user_path, backup_path)
    except shutil.Error as e:
        print("Something went wrong.")
        print(e.stderr, file=sys.stderr)
        sys.exit(1)
    print("[E2S-Utils] Backup successful. You can find it here: " + backup_path)

    if args.all or len(sys.argv) <= 1:
        stereo_to_mono()
        speed_convert(2.0)
        print("All tasks done.")
    elif args.convert_mono:
        stereo_to_mono()
        print("All tasks done.")
    elif args.speed:
        speed_convert(args.speed)
        print("All tasks done.")

if __name__ == '__main__':
    main()