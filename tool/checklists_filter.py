import os
import subprocess


cloned_repo_path = "/Users/Shared/cloned-repos"
checklists_path = "results/checklists-merged"
checklists_filtered_path = "results/checklists-merged-filtered"

checklists = []

# Filter out a file if its path contains "test"
for p in [p for p in os.listdir(checklists_path) if "-checklist.txt" in p]:
    owner, repo = p[p.index("-") + 1 : p.index("-checklist.txt")].split("#")
    with open(os.path.join(checklists_path, p)) as f:
        items = [eval(line) for line in f.read().strip().split("\n") if line != ""]
    checklist = sorted(list(set(item for item in items if "test" not in item[2])))
    checklists.append((owner, repo, checklist))
checklists.sort(key=lambda x: len(x[2]), reverse=True)


def is_not_typo_fix(owner, repo, item):
    _, commit_hash, _ = item
    repo_path = os.path.join(cloned_repo_path, owner, repo)
    msg = subprocess.check_output(
        ["git", "-C", repo_path, "log", "-m", "-1", "--pretty=format:%B", commit_hash]
    ).decode()
    msg_lower = msg.lower()
    return "typo" not in msg_lower and "error message" not in msg_lower

# Filter out a file if its corresponding commit message contains "typo" or "error message"
checklists = [
    (owner, repo, [item for item in checklist if is_not_typo_fix(owner, repo, item)])
    for owner, repo, checklist in checklists
]

for owner, repo, checklist in checklists:
    file_path = os.path.join(
        checklists_filtered_path,
        "%04d-%s#%s-checklist.txt" % (len(checklist), owner, repo),
    )
    with open(file_path, "w") as f:
        f.write("\n".join(repr(i) for i in checklist))
