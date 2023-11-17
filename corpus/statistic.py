import csv

def count_occurrences(file_path, target_value, column_index):
    count = 0
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            if row[column_index] == target_value:
                count += 1
    return count

# 使用示例
file_path = './result_summary.csv'  # 替换为你的CSV文件路径
target_value = '3'
print(count_occurrences(file_path, target_value, 2))
