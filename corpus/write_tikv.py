import os

# 替换为您的.txt文件的路径
txt_file_path = 'review.txt'

# 可能的some_year选项
years = ['2021-before-edition2021', '2021-after-edition2021', '2022', '2023']

with open(txt_file_path, 'r') as file:
    for line in file:
        parts = line.split()

        # 确保行格式正确
        if len(parts) == 3:
            string1, string2, number = parts

            # 遍历年份目录
            for year in years:
                class_file_path = os.path.join('.', year, string1, string2, 'class.txt')
                # print(class_file_path)
                # 检查文件是否存在
                if os.path.isfile(class_file_path):
                    # 读取文件内容
                    with open(class_file_path, 'r') as class_file:
                        lines = class_file.readlines()

                    # 检查文件是否为空
                    if lines:
                        # 更新第一行的第三列
                        class_file_lines = lines[0].split()
                        if len(class_file_lines) < 3:
                            class_file_lines.append(number)
                            lines[0] = ' '.join(class_file_lines) + '\n'

                            # 将更新后的内容写回文件
                            with open(class_file_path, 'w') as class_file:
                                class_file.writelines(lines)

                    # 找到正确的文件后停止遍历年份
                    break
