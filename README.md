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

**class.txt:** information of the bug, detailed as following fields:  

root cause, symptom, panic propagation length (if not panic issue, set the default -1)

code added, code removed,

whether platform-specific,

whether error-handling-related,

propagation chain of safe/unsafe. (0 represents unsafe, 1 safe)

**Note:** if a class.txt contains only two 0's (i.e., 0 0), it means we filtered it.

##### scripts

**count_files.py**
**process_class.py:** process each class.txt and write a summary.
**statistic.py:** assist counting specific column in the summary. 
**gen_results.py:** generate the results for analysis from the summary.





#### tool

**repos.py:**  define candidate repos and corresponding bug-related issue/pr labels
**commit_crawler.py:**  crawl commit hashes by searching for commits with pre-defined labels
**commit_filter.py:** filter non-Rust commit hash, and generate checklists
**checklists_merge.py:** merge duplicate changes in checklists
**checklist_filter.py:** filter test code and other noise like typo fix
**generate_corpus.py:** generate the corpus and group them according to the time stamp