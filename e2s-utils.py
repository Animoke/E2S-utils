import os, sys, argparse, datetime, errno, stat
import ffmpeg, taglib
import glob
import shutil, re, itertools
from ffprobe import FFProbe
from argparse import ArgumentParser
from pathvalidate.argparse import validate_filename_arg, validate_filepath_arg

cur_time = datetime.datetime.now()

def handleRemoveReadonly(func, path, exc):
  excvalue = exc[1]
  if func in (os.rmdir, os.unlink, os.remove) and excvalue.errno == errno.EACCES:
      os.chmod(path, stat.S_IRWXU| stat.S_IRWXG| stat.S_IRWXO) # 0777
      func(path)
  else:
      raise

def stereo_to_mono(all_files):
    i = 0
    fcount = 0
    print("[CONVERT_MONO] Conversion merges both stereo tracks into one.")
    filetree = glob.glob(all_files, recursive=True)
    filetree_len = len(filetree)
    for filename in glob.iglob(all_files, recursive=True):
        if (filename.endswith(".wav")):
            fcount += 1
            sys.stdout.write(f"\r[{fcount}/{filetree_len}] " + filename + " ")
            media = FFProbe(filename)
            for stream in media.streams:
                if stream.is_audio():
                    if stream.__dict__["channels"] == '2':
                        out_filename = filename + "mono-e2s.wav"
                        (
                            ffmpeg
                            .input(filename)
                            .output(out_filename, ac='1', ar='44100') #os.system(f'ffmpeg -i {filename} -ac 1 -ar 44100 {out_filename}')
                            .overwrite_output()
                            .run(capture_stdout=True, capture_stderr=True) #Quiet mode
                        )
                        shutil.move(out_filename, filename)
                        i = i + 1
                    else:
                        print("\n[INFO] Number of channels do not match. \'" + stream.__dict__["channels"] + "\' is not 2. File is probably mono. Skipping...")
                        continue              
        else:
            continue
    print("[CONVERT_MONO]", i, "files converted")

def read_speed_metadata(filename):
    metadata = taglib.File(filename)
    check = metadata.tags.get('COMMENT', None)
    if check != None:
        original_comments = str(metadata.tags['COMMENT'])
        original_speed_r = re.match(r".+\, \[E2S-UTILS\] SPEED: (\d+.\d+)", original_comments)

        if original_speed_r != None:
            original_speed = float(original_speed_r.group(1))
            return original_speed
    else:
        return None

def write_speed_metadata(filename, speed):
    metadata = taglib.File(filename)
    check = metadata.tags.get('COMMENT', None)
    original_comments = ''
    if check != None:
        original_comments = str(metadata.tags['COMMENT'])
        original_speed_r = re.match(r".+\, \[E2S-UTILS\] SPEED: (\d+.\d+)", original_comments)
        original_comments = re.sub(r"\[\'", "", original_comments)
        original_comments = re.sub(r"\'\]", "", original_comments)
        original_comments = re.sub(r", \[E2S-UTILS\] SPEED: \d+.\d+", "", original_comments)

        if original_speed_r != None:
            original_speed = float(original_speed_r.group(1))
    else:
        original_speed = 1.0
        
    new_speed = speed * original_speed
    speed = new_speed
    metadata.tags['COMMENT'] = [f'{original_comments}, [E2S-UTILS] SPEED: {speed}']
    metadata.save()
    #print(metadata.tags)
    metadata.close()
    return speed

def speed_convert(all_files, speed):
    i = 0
    fcount = 0
    print("[INFO][SPEED] File speed is set to", speed)
    filetree = glob.glob(all_files, recursive=True)
    filetree_len = len(filetree)
    for filename in glob.iglob(all_files, recursive=True):
        if (filename.endswith(".wav")):
            media = FFProbe(filename)
            media_probe = str(media.__dict__)
            sample_rate_d = re.search(r"\d{5,6}Hz", media_probe)
            sample_rate = int(re.sub(r"\D", "", sample_rate_d.group()))
            or_speed = read_speed_metadata(filename)
            new_speed = write_speed_metadata(filename, speed)
            fcount += 1
            print(f"[{fcount}/{filetree_len}] " + filename + " | Original speed:", or_speed, " | Speed mod:", speed, "| New speed", new_speed, "| Original sample rate:", sample_rate, "Hz")
            in_filename = filename + "-speed-e2s.wav"
            shutil.move(filename, in_filename)
            (
                ffmpeg
                .input(in_filename)
                .filter('asetrate', sample_rate * speed)
                .output(filename, ar='44100')
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True) #Quiet mode
            )
            i = i + 1
            os.remove(in_filename)
        else:
            continue
    print("[SPEED]", i, "files converted")

def delete_backup(user_path):

    print("/!\\ BE CAREFUL AND VERIFY YOUR FILES BEFORE PROCEEDING /!\\\nALL DIRECTORIES STARTING WITH \'Backup-E2S-utils_\' IN THE DIRECTORY ABOVE SPECIFIED PATH WILL BE DELETED\n")
    
    delete_confirm = input("Type \'i am sure\' to proceed... ")
    if (delete_confirm != "i am sure"):
        print("Cancelling...")
        return
    else:
        i = 0
        backups_path = os.path.abspath(os.path.join(user_path, os.pardir))
        for backups in os.listdir(backups_path):
            directory = backups_path + '\\' + backups
            if (backups.startswith("Backup-E2S-utils_")):
                shutil.rmtree(directory, onerror=handleRemoveReadonly)
                print(f"Deleted {backups_path}\\{backups}")
                i = i + 1
            else:
                continue
        print("Done.", i, "directories removed.")

def main():
    parser = argparse.ArgumentParser(description="Convert all files recursively in directories to mono, with adjustable speed. Made for Korg machines")
    parser.add_argument("-m", "--convert-mono", help="Convert to mono", action='store_true')
    parser.add_argument("-s", "--speed", help="Speed selection (0.5-2.0)", action='store', type=float)
    parser.add_argument("--delete-backups", help="Delete the backups for specified library directory (should be the same path)", action='store_true')
    parser.add_argument("path_to_convert", metavar="PATH", help="Path to process (default speed: 2)", type=validate_filepath_arg)
    args = parser.parse_args()
    
    user_path = args.path_to_convert
    all_files = user_path + "\\**\\*.wav"
    backup_path = os.path.abspath(os.path.join(user_path, os.pardir)) + "\\Backup-E2S-utils_" + cur_time.strftime('%Y-%m-%d_%H-%M-%S')

    if args.delete_backups:
        delete_backup(user_path)
    if args.convert_mono or args.speed or len(sys.argv) == 2:
        print("[E2S-Utils] Backing up...")
        try:
            shutil.copytree(user_path, backup_path)
        except shutil.Error as e:
            print("Something went wrong.")
            print(e.stderr, file=sys.stderr)
            sys.exit(1)
        print("[E2S-Utils] Backup successful. You can find it here: " + backup_path)

    if args.path_to_convert and len(sys.argv) == 2:
        stereo_to_mono(all_files)
        speed_convert(all_files, 2.0)
        print("All tasks done.")
    if args.convert_mono:
        stereo_to_mono(all_files)
        print("All tasks done.")
    if args.speed:
        speed_convert(all_files, args.speed)
        print("All tasks done.")

if __name__ == '__main__':
    main()