import os
import subprocess
import shutil


cloned_repo_path = "cloned-repos"
checklists_path = "results/checklists-merged"
corpus_path = "results/corpus"

date_after = ["2021-1-1", '2021-10-21', '2022-1-1', '2023-1-1']
date_before  = ['2021-10-20', '2021-12-31', '2022-12-31', '2023-12-31']
obj_path = ['results/corpus/2021-before-edition2021', 'results/corpus/2021-after-edition2021', 'results/corpus/2022', 'results/corpus/2023']

checklists = []
for p in [p for p in os.listdir(checklists_path) if "-checklist.txt" in p]:
    owner, repo = p[p.index("-") + 1 : p.index("-checklist.txt")].split("#")
    with open(os.path.join(checklists_path, p)) as f:
        items = [eval(line) for line in f.read().strip().split("\n") if line != ""]
    checklist = sorted(list(set(item for item in items if "test" not in item[2])))
    checklists.append((owner, repo, checklist))
checklists.sort(key=lambda x: len(x[2]), reverse=True)

def judge(repo_path, date_after_filter, date_before_filter, commit_hash):
    cur_commit = (
                subprocess.check_output(
                [
                    "git",
                    "-C",
                    repo_path,
                    "show",
                    "--date=short",
                    date_after_filter,
                    date_before_filter,
                    "--pretty=format:%H",
                    commit_hash,
                ],
                encoding="utf-8"
                ).strip()
                .split("\n")
            )
    if len(cur_commit[0]) == 0: 
        return False
    return True

for owner, repo, checklist in checklists[:40]:
    for i in range(4):
        acc = 0
        # 对于每个commit文件改动条目
        for changed_file_index, (_, commit_hash, file_path_in_repo) in enumerate(checklist):
            repo_path = os.path.join(cloned_repo_path, owner, repo)
            short_commit_hash = commit_hash[:8]
            
            
            #for kk in range(4):
                #date_after_filter = '--since=\"'+date_after[kk]+"\""
                #date_before_filter = '--until=\"'+date_before[kk]+"\""
                #print(kk, judge(repo_path, date_before_filter, date_after_filter, commit_hash))
            date_after_filter = '--since=\"'+date_after[i]+"\""
            date_before_filter = '--until=\"'+date_before[i]+"\""
            
            if judge(repo_path, date_after_filter, date_before_filter, commit_hash) == False:
                #print(commit_hash)
                continue 
            
            acc = acc + 1
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
            commit_hashes = [ch for _, ch, _ in checklist]
            file_name = "%04d-%s" % (
                changed_file_index + 1,
                os.path.splitext(os.path.split(file_path_in_repo)[-1])[0],
            )
            path = os.path.join(obj_path[i], repo, short_commit_hash, file_name)
            msg = subprocess.check_output(
                [
                    "git",
                    "-C",
                    repo_path,
                    "log",
                    "-m",
                    "-1",
                    "--pretty=format:%B",
                    commit_hash,
                ]
            ).decode()
            msg_for_matching = " " + msg.replace("\n", " ").lower()
            msg_file_path = os.path.join(path, "commit_message.txt")
            if os.path.exists(msg_file_path):
                print(f"{owner}/{repo}/{short_commit_hash}:{file_name} already exists")
                continue
            os.makedirs(path, exist_ok=True)
            print(f"{owner}/{repo}/{short_commit_hash}" + ":" + file_name)
            print("acc = ", acc)
            os.system(
                f"git -C {repo_path} show {prev_commit_hash}:{file_path_in_repo} > {os.path.join(path, file_name + '_before.rs')}"
            )
            os.system(
                f"git -C {repo_path} show      {commit_hash}:{file_path_in_repo} > {os.path.join(path, file_name + '_after.rs')}"
            )
            with open(msg_file_path, "w") as msg_file:
                msg_file.write(msg)
            files = [
                file_name + "_before.rs",
                file_name + "_after.rs",
                "commit_message.txt",
            ]
            incomplete = not all(os.path.exists(os.path.join(path, p)) for p in files)
            if (
                incomplete
            ):  # or any(os.path.getsize(os.path.join(path, p)) == 0 for p in files):
                shutil.rmtree(path)
                print(
                    f"{owner}/{repo}/{short_commit_hash}:{file_name} is incomplete and is discarded"
                )
