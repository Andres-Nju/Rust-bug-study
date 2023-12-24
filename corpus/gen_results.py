import pandas as pd


if __name__ == '__main__':
    # load csv
    df = pd.read_csv('result_summary.csv')

    # 1. root causes of each repo
    repo_root_cause_count = df.groupby(['repo', 'root_cause']).size().unstack(fill_value=0)

    # 2. count for each symptom
    symptom_count = df['symptom'].value_counts()

    # 3. average code add和code remove for each root cause
    avg_code_change_by_root_cause = df.groupby('root_cause')[['code_add', 'code_remove']].mean()

    # 4. count for each error_handling
    error_handling_count = df['error_handling'].value_counts()

    # 5. count for each (propagation_chain_1, propagation_chain_2)
    propagation_chain_count = df.groupby(['propagation_chain_1', 'propagation_chain_2']).size()

    # 6. count for each propagation length of panic
    len_panic_count = df[df['symptom'] == 'Panic']['len_panic'].value_counts()

    # 7. review coexistence of different causes and panic
    cause_panic_count = df[df['symptom'] == 'Panic']['root_cause'].value_counts()

    # 8. count for each root cause of each symptom
    symptom_root_cause_count = df.groupby(['symptom', 'root_cause']).size().unstack(fill_value=0)


    # 9.find the most modification of each root cause
    def max_sum_code_change(group):
        sum_col = group['code_add'] + group['code_remove']
        max_idx = sum_col.idxmax()
        return group.loc[max_idx, ['code_add', 'code_remove']]

    max_code_change_by_root_cause = df.groupby('root_cause').apply(max_sum_code_change)

    # 10. propagation length of unwrap
    unwrap_len = df[df['root_cause'] == 11]['len_panic'].value_counts()

    # 11. platform-specific issue with root cause
    root_cause_arch_count = df[df['platform_related'] == 1]['root_cause'].value_counts()

    # 12. count for symptoms of each repo
    repo_symptom_count = df.groupby(['repo', 'symptom']).size().unstack(fill_value=0)

    # 13. root cause counting of each year
    year_root_cause_count = df.groupby(['year', 'root_cause']).size().unstack(fill_value=0)

    # 14. average code add code remove of each symptom
    avg_code_change_by_symptom = df.groupby('symptom')[['code_add', 'code_remove']].mean()
    
    # 15. count for root causes of each safe/unsafe chain
    chain_root_cause_count = df.groupby(['propagation_chain_1', 'propagation_chain_2', 'root_cause']).size().unstack(fill_value=0)

    # 16. count for symptoms of each safe/unsafe chain
    chain_symptom_count = df.groupby(['propagation_chain_1', 'propagation_chain_2', 'symptom']).size().unstack(fill_value=0)

    # save the results
    chain_symptom_count.to_csv('chain_symptom_count.csv')
    chain_root_cause_count.to_csv('chain_root_cause_count.csv')
    avg_code_change_by_symptom.to_csv('avg_code_change_by_symptom.csv')
    year_root_cause_count.to_csv('year_root_cause_count.csv')
    root_cause_arch_count.to_csv('root_cause_arch_count.csv')
    repo_symptom_count.to_csv('repo_symptom_count.csv')
    unwrap_len.to_csv('unwrap_len.csv')
    repo_root_cause_count.to_csv('repo_root_cause_count.csv')
    symptom_count.to_csv('symptom_count.csv')
    avg_code_change_by_root_cause.to_csv('avg_code_change_by_root_cause.csv')
    error_handling_count.to_csv('error_handling_count.csv')
    propagation_chain_count.to_csv('propagation_chain_count.csv')
    len_panic_count.to_csv('len_panic_count.csv')
    cause_panic_count.to_csv('cause_panic_count.csv')
    symptom_root_cause_count.to_csv('symptom_root_cause_count.csv')
    max_code_change_by_root_cause.to_csv('max_code_change_by_root_cause.csv')
