import pandas as pd


if __name__ == '__main__':
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

    # 7. review coexistence of different causes and panic
    cause_panic_count = df[df['symptom'] == 3]['root_cause'].value_counts()

    # 8. 为每个symptom生成每种root_cause的数量
    symptom_root_cause_count = df.groupby(['symptom', 'root_cause']).size().unstack(fill_value=0)


    # 9. 为每一种root cause找到code add 和 code remove之和最大的行
    def max_sum_code_change(group):
        sum_col = group['code_add'] + group['code_remove']
        max_idx = sum_col.idxmax()
        return group.loc[max_idx, ['code_add', 'code_remove']]

    max_code_change_by_root_cause = df.groupby('root_cause').apply(max_sum_code_change)

    # 10. 查看每个unwrap问题的传播链
    unwrap_len = df[df['root_cause'] == 11]['len_panic'].value_counts()

    # 11. 查看平台/架构特定的issue和root cause的关系
    root_cause_arch_count = df[df['platform_related'] == 1]['root_cause'].value_counts()

    # 12. 为每个repo生成每种symptom的数量
    repo_symptom_count = df.groupby(['repo', 'symptom']).size().unstack(fill_value=0)

    # 13. 按照年份统计不同的root cause数量
    year_root_cause_count = df.groupby(['year', 'root_cause']).size().unstack(fill_value=0)

    # 3. 为每一种symptom求平均的code add和code remove
    avg_code_change_by_symptom = df.groupby('symptom')[['code_add', 'code_remove']].mean()
    # 保存结果到新的CSV文件
    avg_code_change_by_symptom.to_csv('avg_code_change_by_symptom.csv')
    # year_root_cause_count.to_csv('year_root_cause_count.csv')
    # root_cause_arch_count.to_csv('root_cause_arch_count.csv')
    # repo_symptom_count.to_csv('repo_symptom_count.csv')
    # unwrap_len.to_csv('unwrao_len.csv')
    # repo_root_cause_count.to_csv('repo_root_cause_count.csv')
    # symptom_count.to_csv('symptom_count.csv')
    # avg_code_change_by_root_cause.to_csv('avg_code_change_by_root_cause.csv')
    # error_handling_count.to_csv('error_handling_count.csv')
    # propagation_chain_count.to_csv('propagation_chain_count.csv')
    # len_panic_count.to_csv('len_panic_count.csv')
    # cause_panic_count.to_csv('cause_panic_count.csv')
    # symptom_root_cause_count.to_csv('symptom_root_cause_count.csv')

    # max_code_change_by_root_cause.to_csv('max_code_change_by_root_cause.csv')
