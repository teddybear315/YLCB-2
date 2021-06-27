import requests
import sys, os
import zipfile
import shutil

branch = sys.argv[1]
cwd = os.path.abspath(".")

def download(url: str, dest_folder: str = "."):
    print(f"Downloading {url}...")
    if not os.path.exists(dest_folder):
        print("Making directory {dest_folder}...")
        os.makedirs(dest_folder)  # create folder if it does not exist

    filename = url.split('/')[-1].replace(" ", "_")  # be careful with file names
    file_path = os.path.join(dest_folder, filename)

    r = requests.get(url, stream=True)
    if r.ok:
        print("Saving to " + os.path.abspath(file_path) + "...")
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
    else:  # HTTP status code 4XX/5XX
        print(f"Download failed: status code {r.status_code}\n{r.text}")

print("This function will overwrite all current files, except for secrets.json and config.json")
if input("Type any character to exit, press enter to continue"): exit(0)

if branch == "master":
    download("https://github.com/teddybear315/YLCB-2/archive/refs/heads/master.zip")
elif branch == "experimental":
    download("https://github.com/teddybear315/YLCB-2/archive/refs/heads/experimental.zip")
else:
    download("https://github.com/teddybear315/YLCB-2/archive/refs/heads/stable.zip")

source = os.path.join(cwd, f"YLCB-2-{branch}\\")
files = os.listdir(source)
with zipfile.ZipFile(f"./{branch}.zip", 'r') as zip_ref:
    print("Extracting zip to temp folder")
    zip_ref.extractall(cwd)
    print(f"Moving {source} to {cwd}...")
    for f in files:
        if f in ["config.json", "secrets.json", source.split('\\')[-1], "updater.py"]: continue
        print(f"\tMoving {f}")
        try:
            shutil.move(source+f, cwd)
        except Exception as e:
            os.remove(dest1+f)
            shutil.move(source+f, cwd)
    os.rmdir(source)
os.remove(f"./{branch}.zip")
