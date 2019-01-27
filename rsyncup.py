from datetime import datetime
import logging
import subprocess
import os

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

BACKUP_ROOT = "/media/pearson/ntfs-external/rsyncup"

INCLUDE = [
    "/home/pearson",
]

EXCLUDE = [
    ".local/share/Trash",
    ".ssh/share/Trash",
    ".cache",
]

DATETIME_FORMAT = "%Y-%m-%d-%H:%M:%S"

def logged_call(cmd):
    logging.info("subprocess.call {}".format(" ".join(cmd)))
    return subprocess.call(cmd)

def copy(dst, src):
    cmd = ["cp", "-al", src, dst]
    return logged_call(cmd)

def rsync(dst, src):
    cmd = ["rsync", "-ravX", "--delete", "--delete-excluded"]
    for e in EXCLUDE:
        cmd += ["--exclude", e]
    cmd += [src, dst]
    return logged_call(cmd)

# get the current time
backup_time = datetime.now()

# figure out the dst for the current backup
current_backup_dir = os.path.join(BACKUP_ROOT, "backup."+backup_time.strftime(DATETIME_FORMAT))
logging.info("backing up to {}".format(current_backup_dir))

# find most recent backup
backup_dates = []
for (dirpath, dirnames, filenames) in os.walk(BACKUP_ROOT):
    for dirname in dirnames:
        dirname = os.path.join(BACKUP_ROOT, dirname)
        _, _, backup_date_str = dirname.rpartition(".")
        backup_dates += [(datetime.strptime(backup_date_str, DATETIME_FORMAT), dirname)]
    break

if backup_dates:
    # copy the most recent backup into the current backup
    latest_backup_date, latest_backup_dir = max(backup_dates)
    logging.info("most recent backup: {}".format(latest_backup_date))
    assert 0 == copy(current_backup_dir, latest_backup_dir) # latest -> current
else:
    logging.info("no backups found in {}".format(BACKUP_ROOT))

# create a new backup now
if not os.path.isdir(current_backup_dir):
    logging.info("os.makedirs {}".format(current_backup_dir))
    os.makedirs(current_backup_dir)
assert 0 == rsync(current_backup_dir, INCLUDE[0])
