import csv

def count_occurrences(file_path, target_value, column_index):
    count = 0
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        rows = 0
        for row in reader:
            rows += 1
            if row[column_index] == target_value:
                count += 1
                print(row[0])
    return count

# 使用示例
file_path = './result_summary.csv'  # 替换为你的CSV文件路径
target_value = '13'
print(count_occurrences(file_path, target_value,1))
