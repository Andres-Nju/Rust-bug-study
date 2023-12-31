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
                print(row[1] + ' ' + row[2])
    return count

# 
file_path = './result_summary.csv'  
target_value = 'Owner'
print(count_occurrences(file_path, target_value, 3))
