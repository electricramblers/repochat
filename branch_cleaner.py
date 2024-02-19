import os
import shutil
import subprocess
import tarfile
import time

# Get the current Git repository
git_dir = subprocess.check_output(["git", "rev-parse", "--git-dir"]).decode().strip()

# Get the list of all local and remote branches
local_branches = [b.strip() for b in subprocess.check_output(["git", "branch"]).decode().split("\n")]
remote_branches = [b.strip() for b in subprocess.check_output(["git", "branch", "-r"]).decode().split("\n")]

# Create a list of all branches and remove main and new
all_branches = set(local_branches + [b[7:] for b in remote_branches if b.startswith("origin/")])
protected_branches = {"main", "new"}
branches_to_delete = list(all_branches - protected_branches)

# Create a backup of the branches that will be deleted
backup_file = f"git_branches_{int(time.time())}.tar.gz"
with tarfile.open(backup_file, "w:gz") as tar:
    for branch in branches_to_delete:
        if os.path.exists(f"{git_dir}/refs/heads/{branch}"):
            tar.add(f"{git_dir}/refs/heads/{branch}", arcname=f"refs/heads/{branch}")
        if os.path.exists(f"{git_dir}/refs/remotes/origin/{branch}"):
            tar.add(f"{git_dir}/refs/remotes/origin/{branch}", arcname=f"refs/remotes/origin/{branch}")

# Delete the branches that are not main or new
for branch in branches_to_delete:
    if os.path.exists(f"{git_dir}/refs/heads/{branch}"):
        subprocess.run(["git", "branch", "-D", branch])
    if os.path.exists(f"{git_dir}/refs/remotes/origin/{branch}"):
        subprocess.run(["git", "push", "origin", f":{branch}"])

print(f"Backup saved to {backup_file}")
