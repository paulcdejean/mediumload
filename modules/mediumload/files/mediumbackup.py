#!/usr/bin/python
import mediumcore
import datetime
import os
import subprocess

conf = mediumcore.mediumconf()
backup_dir = conf.get("backup_dir")

today = datetime.date.today().isoformat()
today_backup = backup_dir + today + "/"
if not os.path.exists(today_backup):
    os.makedirs(today_backup)

os.chdir(today_backup)

server = mediumcore.mediumdb()
c = server.cursor()
c.execute("show databases")
for db, in c:
    with open(today_backup + db + ".sql", "w") as outfile:
        subprocess.check_call(["/usr/bin/mysqldump", "--triggers", "--routines", "--single-transaction",
                               "-h", conf.get("address"), "-u", conf.get("username"), "--password=" + conf.get("password"), db], 
                              stdout = outfile)
    print db
