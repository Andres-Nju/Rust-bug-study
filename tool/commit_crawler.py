import logging
import subprocess
import json
import os
import sys
import requests
import time
import random
import threading
from multiprocessing.pool import ThreadPool
from repos import gh_api, gh_tokens

std = ["A-collections", "A-fmt", "A-io", "A-process", "A-thread", "A-runtime"]

fmt = "%(asctime)s [%(threadName)s] [%(levelname)s] %(message)s"
logging.basicConfig(filename="./crawler.log", format=fmt, level=logging.INFO)
stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setFormatter(logging.Formatter(fmt))
logging.getLogger().addHandler(stdout_handler)

base_dir = os.getcwd()
gh_token, timestamp, mux = gh_tokens[0], time.time(), threading.Lock()
cloned_repo_path = "./Shared/cloned-repos"
bfc_li_results_path = "./results/commits-new"


def web_page(url):
    print(url)
    trials = 3
    resp = None
    while trials > 0:
        try:
            time.sleep(1.0 + random.random() * 2.0)
            resp = requests.get(url)
            if 200 <= resp.status_code < 300:
                break
            logging.warning(f"{url} status code {resp.status_code} ")
            if resp.status_code == 429:
                time.sleep(3.0 + random.random() * 4.0)
        except:
            trials -= 1
    assert resp is not None
    ##print(resp.content)
    return resp.content.decode()


def repo_closed_issues(repo_full_name, label):
    closed_issues = []
    page, links = 1, ["next"]

    def worker(args):
        page, last_page = args
        data, links = gh_api(
            f"/repos/{repo_full_name}/issues",
            params={
                "labels": f"{label}",
                "state": "closed",
                "per_page": "100",
                "page": "%d" % (page,),
            },
        )
        ##print(data)
        logging.info(f"GitHub-API page {page}/{last_page}")
        closed_issues.extend(datum["number"] for datum in data)

    _, links = gh_api(
        f"/repos/{repo_full_name}/issues",
        params={"labels": f"{label}", "state": "closed", "per_page": "100", "page": "1"},
    )
    last_page = int(links["last"]["url"].split("=")[-1]) if "last" in links else 1
    with ThreadPool(processes=32) as p:
        p.map(worker, [(page, last_page) for page in range(1, last_page + 1)])
    return closed_issues


# 加一个判断，判断不明显

def get_related_develop_issues(github_issue_number, repo_path):
    # 使用 GitHub CLI 获取指定 issue 的详细信息
    issue_info_cmd = f"gh issue view {github_issue_number} --json title,url,development --repo {repo_path}"
    issue_info_output = subprocess.check_output(issue_info_cmd, shell=True, text=True)

    # 解析 JSON 输出
    issue_info = json.loads(issue_info_output)
    print("issue_info \n\n ", issue_info)
    if 'title' not in issue_info or 'url' not in issue_info:
        print("Failed to retrieve issue information.")
        return None

    print(f"GitHub Issue #{github_issue_number}: {issue_info['title']} ({issue_info['url']})")

    # 使用 GitHub CLI 获取相关的 develop 中的 issue
    related_develop_cmd = f"gh issue list --label develop --json number,title,url --repo {repo_path}"
    related_develop_output = subprocess.check_output(related_develop_cmd, shell=True, text=True)

    # 解析 JSON 输出
    related_develop_issues = json.loads(related_develop_output)

    # 打印相关的 develop 中的 issue 信息
    print("\nRelated issues in 'develop' label:")
    for issue in related_develop_issues:
        print(f"#{issue['number']}: {issue['title']} ({issue['url']})")

    return related_develop_issues

def issue_fixed_by(repo_full_name, issue):
    pr = web_page(f"https://github.com/{repo_full_name}/issues/{issue}")
    
    if "· Fixed by" not in pr:
        
        return None
    pr = pr[pr.index("· Fixed by") :]
    
    marker = "github.com"
    pr = pr[pr.index(marker) + len(marker) + 1 :]
    pr = pr[: pr.index('"')].split("/")
    pr_repo_full_name, pr = pr[0] + "/" + pr[1], pr[-1]
    if pr_repo_full_name != repo_full_name:
        return None
    print(f"pr is :: {pr}")
    get_related_develop_issues(issue, repo_full_name)
    return pr


def pr_commit_hash(repo_full_name, pr):
    data, links = gh_api(f"/repos/{repo_full_name}/pulls/{pr}", params={})
    return data.get("merge_commit_sha")

# 根据bug_label 找出bug_fix相关的commit
def bug_fixing_commits_by_issue_labels(repo_full_name, labels):
    closed_issues = set()
    for label in labels:
        issues = repo_closed_issues(repo_full_name, label)
        closed_issues.update(issues)
        ##print(issues)
    logging.info(f"{len(closed_issues)} closed issues are found in '{repo_full_name}'")
    prs = []
    worked, total, mux = 0, len(closed_issues), threading.Lock()

    def worker1(issue):
        nonlocal worked
        pr = issue_fixed_by(repo_full_name, issue)
        logging.info(
            f"({worked + 1}/{total}) Issue#{issue} of '{repo_full_name}' is closed "
            + (f"by PR#{pr}" if pr is not None else "without a PR")
        )
        if pr is not None:
            prs.append((issue, pr))
        mux.acquire()
        worked += 1
        mux.release()

    with ThreadPool(processes=32) as p:
        p.map(worker1, closed_issues)
    ##for i in closed_issues:
    ##    worker1(i)
    prs = set(prs)
    logging.info(f"{len(prs)} PRs are collected from '{repo_full_name}'")
    bug_fixing_commits = []
    worked, total = 0, len(prs)

    def worker2(args):
        nonlocal worked
        issue, pr = args
        commit_hash = pr_commit_hash(repo_full_name, pr)
        logging.info(
            f"({worked + 1}/{total}) PR#{pr} of '{repo_full_name}' has a commit hash of {commit_hash[:8]}"
        )
        bug_fixing_commits.append((issue, pr, commit_hash))
        mux.acquire()
        worked += 1
        mux.release()

    with ThreadPool(processes=32) as p:
        p.map(worker2, prs)
    #for i in prs:
     #   worker2(i)
    
    bug_fixing_commits = set(bug_fixing_commits)
    logging.info(
        f"{len(bug_fixing_commits)} bug-fixing commits (by issue labels) are found in '{repo_full_name}'"
    )
    return list(bug_fixing_commits)

# bug-fixing commits by issue labels
def work_bfc_il(repo):
    repo_full_name, labels = repo
    path = os.path.join(bfc_li_results_path, repo_full_name.replace("/", "#") + ".txt")
    if os.path.exists(path):
        with open(path) as f:
            bfcs_str = f.read().strip()
        bfcs = [] if len(bfcs_str) == 0 else [eval(i) for i in bfcs_str.split("\n")]
        logging.info(
            f"{len(bfcs)} bug-fixing commit hashes (by issue labels) of '{repo_full_name}' are retrieved from '{path}'"
        )
    else:
        bfcs = bug_fixing_commits_by_issue_labels(repo_full_name, labels)
        bfcs = [tuple(str(j) for j in i) for i in bfcs]
        with open(path, "w") as f:
            f.write("\n".join(repr(i) for i in bfcs))
        logging.info(
            f"{len(bfcs)} bug-fixing commit hashes (by issue labels) of '{repo_full_name}' are saved into '{path}'"
        )
    return (repo_full_name, bfcs)


if __name__ == "__main__":
    from repos import repos

    logging.info(
        f"Collecting bug-fixing commits by *issue labels* from {len(repos)} repos in total..."
    )

    for repo in repos:
        work_bfc_il(repo)
