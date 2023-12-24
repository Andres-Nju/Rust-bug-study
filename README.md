## Repository structure

```shell
corpus
  ├── @year
  |    ├── @repository
  |         ├── @bug-fix commit/issue
  |             └── class.txt
  ├── count_files.py
  ├── process_class.py
  ├── statistic.py
  ├── gen_results.py
tool
  ├── repos.py
  ├── checklists_filter.py
  ├── checklists_merge.py
  ├── commit_crawler.py
  ├── commit_filter.py
  ├── generate_corpus.py
```

#### corpus

##### dataset

**@year:** the year which the issue is solved. In this study, commits are divided into 4 groups:

2021-after-edition2021, 2021-before-edition2021, 2022, 2023

@repository: 7 repos: egui, meilisearch, rust, rust-analyzer, snarkOS, tikv, tokio

**@bug-fix commit/issue:** the hash of bug-fix commit or the corresponding issue

**class.txt:** information of the bug, detailed as:

root cause, symptom, panic propagation length (if not panic issue, set the default -1)

code added, code removed,

whether platform-specific,

whether error-handling-related,

propagation chain of safe/unsafe. (0 represents unsafe, 1 safe)



##### scripts

**count_files.py**
**process_class.py:** process each class.txt and write a summary.
**statistic.py:** assist counting specific column in the summary. 
**gen_results.py:** generate the results for analysis from the summary.





#### tool