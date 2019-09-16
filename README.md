# django_issues
a crawler to fetch Django projects Github closed issues. a script to filter Django related issues

# Fetch closed issues
1. Use get_issue_list.py to get Django proejcts Github closed issues.
2. The Django proejcts repositories are listed in repos.json
3. The fetched results are in issues.csv, issues.txt.
4. Errors are logged in error.txt

# Django errors analysis
1. Use analyze_issue_link_list.py to filter the wanted Djnago errors
2. The output files are
    * django_error_count.csv: the fitlered django errors
    * match_filter_index.json: the matched django error row index in dataframe (issues.csv)
    * repo_django_errors.json: how many django errors are in each project
    * count_django_errors.json: the number of each django errors