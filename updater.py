import requests
import sys, os
import zipfile
import shutil
import loglib
import hashlib

branch = sys.argv[1]
cwd = os.path.abspath(".")
l = Logger(flags=0b0111)

def download(url: str, dest_folder: str = ".") -> str:
    l.log(f"Downloading {url}...")
    if not os.path.exists(dest_folder):
        l.log("Making directory {dest_folder}...")
        os.makedirs(dest_folder)  # create folder if it does not exist

    filename = url.split('/')[-1].replace(" ", "_")  # be careful with file names
    file_path = os.path.join(dest_folder, filename)

    r = requests.get(url, stream=True)
    if r.ok:
        l.log("Saving to " + os.path.abspath(file_path) + "...")
        bytes_downloaded = 0
        total_kb = round(len(r.content)/1024.0, 2)
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024 * 8):
                if chunk:
                    f.write(chunk)
                    f.flush()
                    os.fsync(f.fileno())
                    bytes_downloaded=bytes_downloaded+(1024 * 8)
                print(f"Downloaded: {bytes_downloaded/1024.0}kb/{total_kb}kb", end="\r")
            print(f"Downloaded: {total_kb}kb/{total_kb}kb", end="\n")
        return hashlib.sha256(open(os.path.abspath(file_path),"rb").read()).hexdigest()
    else:  # HTTP status code 4XX/5XX
        l.err(f"Download failed: status code {r.status_code}\n{r.text}")

print("This function will overwrite all current files, except for secrets.json and config.json")
if input("Type any character to exit, press enter to continue"): exit(0)
dl = f"https://github.com/teddybear315/YLCB-2/archive/refs/heads/{branch}.zip"
if os.path.exists(cw+f"{branch}.zip"):
    curr_hash = hashlib.sha256(open(os.path.abspath(cw+f"{branch}.zip"),"rb").read()).hexdigest()
    l.log(f"Current ZIP hash: {curr_hash}",)
updated_hash = download(dl)
l.log(f"New ZIP hash: {updated_hash}")
if updated_hash == curr_hash:
    l.log("Hashes equal, exiting...")
    return

source = os.path.join(cwd, f"YLCB-2-{branch}\\")
files = os.listdir(source)

with zipfile.ZipFile(f"./{branch}.zip", 'r') as zip_ref:
    l.log("Extracting zip to temp folder")
    zip_ref.extractall(cwd)
    l.log(f"Moving {source} to {cwd}...")
    for f in files:
        if f in ["config.json", "secrets.json", source.split('\\')[-1], "updater.py"]: continue
        l.log(f"\tMoving {f}")
        try:
            shutil.move(source+f, cwd)
        except Exception as e:
            os.remove(dest1+f)
            shutil.move(source+f, cwd)
    os.rmdir(source)
