import os

def create_class_file(commit_folder):
    class_file_path = os.path.join(commit_folder, 'class.txt')
    with open(class_file_path, 'w') as class_file:
        class_file.write(os.path.basename(commit_folder))

def process_commits(repo_folder):
    for commit_folder in os.listdir(repo_folder):
        commit_path = os.path.join(repo_folder, commit_folder)
        if os.path.isdir(commit_path):
            create_class_file(commit_path)

def process_repos(year_folder):
    for repo_folder in os.listdir(year_folder):
        repo_path = os.path.join(year_folder, repo_folder)
        if os.path.isdir(repo_path):
            process_commits(repo_path)

def process_years(corpus_folder):
    for year_folder in os.listdir(corpus_folder):
        year_path = os.path.join(corpus_folder, year_folder)
        if os.path.isdir(year_path):
            process_repos(year_path)

if __name__ == "__main__":
    corpus_folder = "."  # 替换为你的语料库文件夹路径
    process_years(corpus_folder)
