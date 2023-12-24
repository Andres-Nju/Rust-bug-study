import os
import subprocess
import threading
from multiprocessing.pool import ThreadPool


cloned_repo_path = "cloned-repos"
checklists_path = "results/checklists-new"
bfc_li_results_path = "results/commits-new"


# Update cloned repo, clone if it is not already cloned
def update_repo(repo_full_name):
    owner, repo = repo_full_name.split("/")
    repo_path = os.path.join(cloned_repo_path, owner, repo)
    if os.path.exists(repo_path):
        os.system(f"git -C {repo_path} fetch --all && git -C {repo_path} reset --hard")
    else:
        os.system(f"git clone git@github.com:{repo_full_name}.git {repo_path}")


# Provide a list of paths of files changed by the given commit
def commit_changed_files(repo_full_name, commit_hash):
    owner, repo = repo_full_name.split("/")
    repo_path = os.path.join(cloned_repo_path, owner, repo)
    try:
        files = (
            subprocess.check_output(
                [
                    "git",
                    "-C",
                    repo_path,
                    "log",
                    "-m",
                    "-1",
                    "--name-only",
                    "--pretty=",
                    commit_hash,
                ]
            )
            .decode()
            .strip()
            .split("\n")
        )
    except:
        # This commit does not belong to any branch on this repository
        # It may belong to a fork outside the repository
        return []
    return list(set(files))


# Calculate the number of changed lines in a file by the given commit
def file_changed_line_count(repo_full_name, commit_hash, file_path):
    owner, repo = repo_full_name.split("/")
    repo_path = os.path.join(cloned_repo_path, owner, repo)
    prev_commit_hash = (
        subprocess.check_output(
            [
                "git",
                "-C",
                repo_path,
                "log",
                "-m",
                "-2",
                "--pretty=format:%H",
                commit_hash,
            ]
        )
        .decode()
        .strip()
        .split("\n")[1]
    )
    diff = subprocess.Popen(
        [
            "git",
            "-C",
            repo_path,
            "diff",
            commit_hash,
            prev_commit_hash,
            "--",
            file_path,
        ],
        stdout=subprocess.PIPE,
    )
    stat = (
        subprocess.check_output(["diffstat", "-s"], stdin=diff.stdout).decode().strip()
    )
    if stat == "0 files changed" or "test" in file_path or "issue" in file_path:
        return 0
    if stat.count(",") not in (1, 2):
        print(
            " ".join(
                [
                    "git",
                    "-C",
                    repo_path,
                    "diff",
                    commit_hash,
                    prev_commit_hash,
                    "--",
                    file_path,
                ]
            )
        )
        return 10000
    changed_line_count = sum(
        [int(s.strip().split(" ")[0]) for s in stat.split(",")][1:]
    )
    return changed_line_count


# Provide a list of paths of files changed by the given commit that is both
# 1. a Rust source file (*.rs) and
# 2. has less than or equal to 8 lines changed
def commit_slightly_changed_rs_files(repo_full_name, commit_hash):
    files = commit_changed_files(repo_full_name, commit_hash)
    files = [
        (f, file_changed_line_count(repo_full_name, commit_hash, f))
        for f in files
        if os.path.splitext(f)[1] == ".rs"
    ]
    files = [
        (f, changed_line_count)
        for f, changed_line_count in files
        if changed_line_count > 0
    ]
    if len(files) == 0:
        return []
    files, counts = zip(*files)
    files = list(files) if sum(counts) > 0 else []
    return files


for p in [p for p in os.listdir(bfc_li_results_path) if p[0] != "."]:
    owner, repo = os.path.splitext(p)[0].split("#")
    if (owner + "#" + repo + "-checklist") in "".join(os.listdir(checklists_path)):
        print(f"'{owner}/{repo}' is already filtered")
        continue
    file_code_checklist = []
    update_repo(owner + "/" + repo)
    with open(os.path.join(bfc_li_results_path, p)) as f:
        content = f.read().strip()
    if len(content) == 0:
        issue_pr_commit_hashes = []
    issue_pr_commit_hashes = [] if len(content) == 0 else content.split("\n")
    if len(issue_pr_commit_hashes[0]) > 0 and issue_pr_commit_hashes[0][0] == "(":
        issue_pr_commit_hashes = [eval(i)[2] for i in issue_pr_commit_hashes]
    active_workers, worked, total, mux1, mux2 = (
        0,
        0,
        len(issue_pr_commit_hashes),
        threading.Lock(),
        threading.Lock(),
    )

    def worker(commit_hash):
        global active_workers, worked

        mux1.acquire()
        active_workers += 1
        mux1.release()
        mux2.acquire()
        print(f"({worked + 1}/{total})\tActive workers = {active_workers}")
        mux2.release()
        for file_path in commit_slightly_changed_rs_files(
            owner + "/" + repo, commit_hash
        ):
            file_code_checklist.append(repr((repo, commit_hash, file_path)))
            mux2.acquire()
            print((repo, commit_hash, file_path))
            mux2.release()
        mux1.acquire()
        active_workers -= 1
        worked += 1
        mux1.release()

    with ThreadPool(processes=10) as p:
        p.map(worker, issue_pr_commit_hashes)
    filename = "%04d-%s#%s-checklist.txt" % (len(file_code_checklist), owner, repo)
    with open(os.path.join(checklists_path, filename), "w") as f:
        f.write("\n".join(file_code_checklist))
    print(f"'{owner}/{repo}' has finished filtering")
