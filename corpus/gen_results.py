import pandas as pd

# 加载CSV文件
df = pd.read_csv('result_summary.csv')

# 1. 为每个repo生成每种root_cause的数量
repo_root_cause_count = df.groupby(['repo', 'root_cause']).size().unstack(fill_value=0)

# 2. 生成一个总的每种symptom的数量
symptom_count = df['symptom'].value_counts()

# 3. 为每一种root cause求平均的code add和code remove
avg_code_change_by_root_cause = df.groupby('root_cause')[['code_add', 'code_remove']].mean()

# 4. 生成一个总的每种error_handling的数量
error_handling_count = df['error_handling'].value_counts()

# 5. 生成一个总的每种（propagation_chain_1, propagation_chain_2）pair的数量
propagation_chain_count = df.groupby(['propagation_chain_1', 'propagation_chain_2']).size()

# 6. 提取出所有的symptom值为'3'的字段，生成一个每种len_panic的数量
len_panic_count = df[df['symptom'] == 3]['len_panic'].value_counts()

# 保存结果到新的CSV文件
repo_root_cause_count.to_csv('repo_root_cause_count.csv')
symptom_count.to_csv('symptom_count.csv')
avg_code_change_by_root_cause.to_csv('avg_code_change_by_root_cause.csv')
error_handling_count.to_csv('error_handling_count.csv')
propagation_chain_count.to_csv('propagation_chain_count.csv')
len_panic_count.to_csv('len_panic_count.csv')