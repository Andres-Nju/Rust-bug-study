import os

# 设置当前目录和test目录的路径
current_dir = '.'  # 当前目录
test_dir = '../test'  # test目录

for root, dirs, files in os.walk(current_dir):
    for file in files:
        if file == 'class.txt':
            current_file_path = os.path.join(root, file)

            # 构建test目录中对应的class.txt的路径
            test_file_path = os.path.join(test_dir, os.path.relpath(current_file_path, current_dir))

            if os.path.isfile(test_file_path):
                with open(current_file_path, 'r') as current_file:
                    lines = current_file.readlines()
                
                with open(test_file_path, 'r') as test_file:
                    test_line = test_file.readline()
                
                # 获取当前目录中class.txt的第二行的数字
                num1, num2 = map(int, lines[1].split())
                # 获取test目录中class.txt的第一行的数字
                num3, num4 = map(int, test_line.split())

                # 计算新的数字并更新当前目录中的class.txt
                lines[1] = f"{num1 - num4} {num2 - num3}\n"
                with open(current_file_path, 'w') as current_file:
                    current_file.writelines(lines)