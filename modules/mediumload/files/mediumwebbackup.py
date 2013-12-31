#!/usr/bin/python
import mediumcore
import datetime
import os
import subprocess

conf = mediumcore.mediumconf()
backup_dir = conf.get("backup_dir") + "web/"

today = datetime.date.today().isoformat()
today_backup = backup_dir + today + "/"
if not os.path.exists(today_backup):
    os.makedirs(today_backup)

os.chdir(today_backup)

subprocess.check_call(["tar", "-zcvf", today_backup+"web"+today+".tar.gz", "/usr/local/htdocs/"])
