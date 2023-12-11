import os

safety = ["unsafe", "safe", "Interior unsafe", "unknown"]

not_general_bug_cnt = 0
un_checked_cnt = 0
checked_bug = 0
causes = ['Alg', 'Cod', 'Mem', 'Type', 'Conc', 'Priv', 'Bound', 'Doc', 'Num', 'padding', 'Unwrap', 'Mut', 'Owner', 'Attr', 'Mac', 'Ver', 'Unsound', 'Other']
symptoms = ['Behavior', 'Compile', 'Panic', 'Security', 'Crash', 'Performance']

def process_class_file(class_file_path, repo, commit, year):
    global not_general_bug_cnt
    global un_checked_cnt
    global checked_bug
    with open(class_file_path, 'r') as file:
        # print(class_file_path)
        len_panic = -1
        lines = file.readlines()
        if len(lines[0].split()) == 1:
            un_checked_cnt += 1
            return None
        if len(lines[0].split()) == 3:
            root_cause, symptom, len_panic = map(int, lines[0].split())
        else:
            root_cause, symptom = map(int, lines[0].split())
        if root_cause == 0 and symptom == 0:
            not_general_bug_cnt += 1
            return None
        checked_bug += 1
        code_add, code_remove = map(int, lines[1].split())
        platform_related = int(lines[2])
        error_handling = int(lines[3])
        propagation_chain = tuple(map(int, lines[4].split()))
        print(repo + ' ' + commit)
        return [
            year,
            repo,
            commit,
            causes[root_cause - 1],
            symptoms[symptom - 1],
            code_add,
            code_remove,
            platform_related,
            error_handling,
            safety[propagation_chain[0]],
            safety[propagation_chain[1]],
            len_panic
        ]

def process_corpus(corpus_folder, output_file):
    with open(output_file, 'w', newline='') as csv_file:
        csv_file.write("year,repo,commit,root_cause,symptom,code_add,code_remove,platform_related,error_handling,propagation_chain_1,propagation_chain_2,len_panic\n")

        for year_folder in os.listdir(corpus_folder):
            year_path = os.path.join(corpus_folder, year_folder)
            if os.path.isdir(year_path):
                for repo_folder in os.listdir(year_path):
                    repo_path = os.path.join(year_path, repo_folder)
                    if os.path.isdir(repo_path):
                        for commit_folder in os.listdir(repo_path):
                            commit_path = os.path.join(repo_path, commit_folder)
                            if os.path.isdir(commit_path):
                                repo_commit = f"{repo_folder}/{commit_folder}"
                                class_file_path = os.path.join(commit_path, 'class.txt')
                                if os.path.exists(class_file_path):
                                    class_data = process_class_file(class_file_path, repo_folder, commit_folder, year_folder)
                                    if class_data is not None:
                                        csv_file.write(','.join(map(str, class_data)) + '\n')

if __name__ == "__main__":
    corpus_folder = "."  # 替换为你的语料库文件夹路径
    output_file = "result_summary.csv"  # 输出文件名
    process_corpus(corpus_folder, output_file)
    print("unchecked count: ", un_checked_cnt)
    print("0 0 count: ", not_general_bug_cnt)
    print("checked bug: ", checked_bug)
