import requests
import sys, os
import zipfile
import shutil
import hashlib

from loglib import Logger

class Updater:
    def __init__(self, user, repo, branch, install_folder=os.path.abspath(".") + "\\", skip_same_version_check=False, no_update_override=False):
        self.user = user
        self.repo = repo
        self.branch = branch
        self.install_folder = install_folder
        self.l = Logger(flags=0b0101)
        self.skip_same_version_check = skip_same_version_check
        self.no_update_override = no_update_override

    def download(self, url) -> str:
        # Returns hash of downloaded file
        self.l.log(f"Downloading {url}...")
        if not os.path.exists(self.install_folder):
            self.l.log("Making directory {self.install_folder}...")
            os.makedirs(self.install_folder)  # create folder if it does not exist

        filename = url.split('/')[-1].replace(" ", "_")  # be careful with file names
        file_path = os.path.join(self.install_folder, filename)

        r = requests.get(url, stream=True)
        if r.ok:
            self.l.log("Saving to " + os.path.abspath(file_path) + "...")
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

    def update_available(self, user, repo, branch, old_zip) -> bool:
        old_hash = hashlib.md5()
        new_hash = hashlib.md5(requests.get(f"https://github.com/{user}/{repo}/archive/refs/heads/{branch}.zip").content).hexdigest()
        with open(os.path.abspath(self.install_folder+f"{old_zip}.zip"), "rb") as f:
            while True:
                data = f.read(65536)
                if not data:
                    break
                old_hash.update(data)
        old_hash = old_hash.hexdigest()
        self.l.log(f"Old ZIP hash: {old_hash}")
        self.l.log(f"New ZIP hash: {new_hash}")
        self.l.log(f"Update available? {not (old_hash == new_hash)}")
        if old_hash == new_hash: return False
        return True

    def check_and_dl(self, user, repo, branch):
        print("This function will overwrite all current files, except for secrets.json and config.json") # user warning
        if input("Type any character to exit, press enter to continue"): exit(0)

        dl = f"https://github.com/{user}/{repo}/archive/refs/heads/{branch}.zip" # download link
        downloaded = os.path.exists(self.install_folder+f"\\{branch}.zip")
        skipping_check = "skip-check" in sys.argv or self.skip_same_version_check
        if downloaded and not skipping_check and self.update_available(user, repo, branch, branch): exit(0) # exit
        self.download(dl) # download file

    def extract_zip(self, path, to):
        with zipfile.ZipFile(f"./{path}.zip", 'r') as zip_ref: # open downloaded zip
            self.l.log(f"Extracting {path}.zip to {to} folder")
            zip_ref.extractall(to) # extract zipfile
            zip_ref.close() #close zipfile

    def move_folder(self, dir, to):
        files = os.listdir(dir)

        self.l.log(f"Moving {dir} to {to}...")
        for f in files:
            if (f in ["config.json", "secrets.json", dir.split('\\')[-1]]) or (f in ["update.bat", "update.sh", "updater.py"] and ("nuo" in sys.argv or self.no_update_override)):
                os.remove(os.path.join(dir,f))
                self.l.log(f"\tSkipping {f}, restricted from overwrite")
                continue
            if f == "updater.py":
                shutil.move(os.path.join(dir,f), to+"_"+f)
                self.l.log(f"\tMoving {f}")
                continue
            try:
                shutil.move(os.path.join(dir,f), to)
                self.l.log(f"\tMoving {f}")
            except shutil.Error as e:
                try:
                    os.remove(os.path.join(to,f))
                    shutil.move(os.path.join(dir,f), to)
                    self.l.log(f"\tMoving {f}")
                except Exception: self.move_folder(dir+f+"\\", to+f+"\\")
            except Exception as e: l.err(e)
        shutil.rmtree(dir)

    def update(self):
        #if self.check(): # includes skip check, just add 'skip-check' to the command args
        self.check_and_dl(self.user, self.repo, self.branch) # includes skip check, just add 'skip-check' to the command args
        self.extract_zip(self.branch, self.install_folder)
        self.move_folder(os.path.join(self.install_folder, f"{self.repo}-{self.branch}\\"), self.install_folder)

if __name__ == "__main__":
    branch = sys.argv[1]
    updater = Updater("teddybear315", "YLCB-2", branch)
    updater.check_and_dl(updater.user, updater.repo, branch, branch)
