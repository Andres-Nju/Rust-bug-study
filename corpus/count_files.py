import os

def count_directories_at_level(root_path, desired_level):
    count = 0

    def recurse(current_path, current_level):
        nonlocal count
        if current_level == desired_level:
            count += 1
            return  # Stop further recursion at this level

        for entry in os.listdir(current_path):
            full_path = os.path.join(current_path, entry)
            if os.path.isdir(full_path):
                recurse(full_path, current_level + 1)

    recurse(root_path, 0)
    return count

def count_repo_commits(root_path):
    count = {}
    for year in os.listdir(root_path):
        year_path = os.path.join(root_path, year)
        if os.path.isdir(year):
            for repo in os.listdir(year_path):
                if repo not in count.keys():
                    count[repo] = 0
                repo_path = os.path.join(year_path, repo)
                count[repo] += len(os.listdir(repo_path))
                # print("repo: " + repo + " cnt: " + str(len(os.listdir(repo_path))))
    return count


# usage
root_directory = '.'  # replace this to your root direct
level = 3  # depth in which you want to search

print(count_directories_at_level(root_directory, level))

print(count_repo_commits(root_directory))