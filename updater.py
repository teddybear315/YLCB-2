import requests
import sys, os
import zipfile
import shutil
import hashlib

from loglib import Logger

branch = sys.argv[1]
cwd = os.path.abspath(".") + "\\"
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
            print(f"Downloaded: {total_kb}kb/{total_kb}kb         ", end="\n")
        return hashlib.sha256(open(os.path.abspath(file_path),"rb").read()).hexdigest()
    else:  # HTTP status code 4XX/5XX
        l.err(f"Download failed: status code {r.status_code}\n{r.text}")

print("This function will overwrite all current files, except for secrets.json and config.json")
if input("Type any character to exit, press enter to continue"): exit(0)

dl = f"https://github.com/teddybear315/YLCB-2/archive/refs/heads/{branch}.zip"

if os.path.exists(cwd+f"\\{branch}.zip"):
    updated_hash = download(dl)
    if "skip-check" not in sys.argv:
        curr_hash = hashlib.sha256(open(os.path.abspath(cwd+f"\\{branch}.zip"),"rb").read()).hexdigest()
        if updated_hash == curr_hash:
            l.log(f"Current ZIP hash: {curr_hash}")
            l.log(f"New ZIP hash: {updated_hash}")
            l.log("Hashes equal, exiting...")
            exit(0)
else: download(dl)

with zipfile.ZipFile(f"./{branch}.zip", 'r') as zip_ref:
    l.log("Extracting zip to temp folder")
    zip_ref.extractall(cwd)
    zip_ref.close()

master = os.path.join(cwd, f"YLCB-2-{branch}\\")
files = os.listdir(master)

l.log(f"Moving {master} to {cwd}...")
for f in files:
    if f in ["config.json", "secrets.json", master.split('\\')[-1]]:
        os.remove(os.path.join(master,f))
        continue
    if f == "updater.py":
        shutil.move(os.path.join(master,f), cwd+"_"+f)
        l.log(f"\tMoving {f}")
        continue
    try:
        shutil.move(os.path.join(master,f), cwd)
        l.log(f"\tMoving {f}")
    except shutil.Error as e:
        try:
            os.remove(os.path.join(cwd,f))
            shutil.move(os.path.join(master,f), cwd)
            l.log(f"\tMoving {f}")
        except Exception: continue
    except Exception: continue

# move src folder
source = os.path.join(cwd, f"YLCB-2-{branch}\\src\\")
dest1 = os.path.join(cwd, "src\\")
files = os.listdir(source)

l.log(f"Moving {source} to {dest1}...")
for f in files:
    try:
        shutil.move(os.path.join(source,f), dest1)
        l.log(f"\tMoving {f}")
    except shutil.Error as e:
        try:
            os.remove(os.path.join(dest1,f))
            shutil.move(os.path.join(source,f), dest1)
            l.log(f"\tMoving {f}")
        except Exception: continue
    except Exception: continue

shutil.rmtree(source)
shutil.rmtree(master)
