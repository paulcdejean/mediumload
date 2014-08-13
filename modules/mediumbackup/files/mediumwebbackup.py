#!/usr/bin/python
import mediumcore
import datetime
import subprocess

conf = mediumcore.mediumconf()
domain = conf.get("domain_name")

today = datetime.date.today().isoformat()
backup_name = domain + "_" + today

subprocess.check_call(["/usr/local/bin/tarsnap", "-c", "-C", "/usr/local/htdocs/", "-f", backup_name, "."])
