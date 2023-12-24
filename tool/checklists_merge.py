import os


src_paths = ["results/checklists"]
dst_path = "results/checklists-merged"

files = [
    [i.split("-", 1) for i in os.listdir(path) if len(i) > 0 and i[0] != "."]
    for path in src_paths
]
common_files = []
for i in files[0]:
    for j in files[1:]:
        if i[1] not in [l[1] for l in j]:
            break
    else:
        common_files.append(i[1])

for j in common_files:
    checklist = set()
    for src_path, i in zip(src_paths, files):
        for k in i:
            if k[1] == j:
                f = os.path.join(src_path, "-".join(k))
                with open(f) as checklist_file:
                    lines = checklist_file.read().strip().split("\n")
                    checklist.update(lines)
    checklist = list(checklist)
    merged_checklist_path = os.path.join(dst_path, "%04d-%s" % (len(checklist), j))
    with open(merged_checklist_path, "w") as merged_checklist:
        merged_checklist.write("\n".join(checklist))
