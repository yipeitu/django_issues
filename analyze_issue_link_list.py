# catergorize issues
import pandas as pd
import json
import csv

# read issues which is stored by csv and fetch from github (get_issue_list.py)
df = pd.read_csv("issues.csv")
# Type django exceptions
filter_string_list = [
	"ObjectDoesNotExist",
	"EmptyResultSet",
	"FieldDoesNotExist",
	"MultipleObjectsReturned",
	"SuspiciousOperation",
	"PermissionDenied",
	"ViewDoesNotExist",
	"FieldError",
	"ValidationError",
	"NON_FIELD_ERRORS",
	"Resolver404",
	"NoReverseMatch",
	"UnreadablePostError",
	"InterfaceError",
	"DatabaseError",
	"DataError",
	"OperationalError",
	"IntegrityError",
	"InternalError",
	"ProgrammingError",
	"NotSupportedError",
	"models.ProtectedError",
	"TransactionManagementError"
]

# filter lables, title, body which contains error and newbie
def match_filter_str(message, filter_str):
	if type(message) is not str:
		return False
	message = message.lower()
	if 'docker' in message:
		return False
	elif 'Docker' in message:
		return False
	if ('django' in message or 'Django' in message) and filter_str.lower() in message:
			return True
	elif filter_str.lower() in message:
		return True
	return False


match_filter_index = []
repo_django_errors = {}
count_django_errors = {}
count_total_errors = 0
csvfile = open("django_error_count.csv", "w")
csv_writer = csv.writer(csvfile)
csv_writer.writerow(['django error', 'auth', 'repo', 'html_url'])

for filter_str in filter_string_list:
	print("----------------%s----------------"%filter_str)
	for num_index in range(len(df)):
		# read all labels
		# labels = df.loc[num_index].labels
		# if labels != '[]':
		# 	try:
		# 		labels = json.loads(labels)
		# 	except:
		# 		print("--------error--------: ", labels)
		# if type(labels) is list:
		# 	for label in labels:
		# 		name = label.get("name", "")
		# 		if len(name) == 0:
		# 			continue
				
				# check this issue has existed or not
		# 		if match_filter_str(name):
		# 			match_filter_index.append(num_index)
		# if num_index in match_filter_index:
		# 	pass
		# else:
		# 	# check title and body
		# 	if match_filter_str(df.loc[num_index].title, True) or match_filter_str(df.loc[num_index].body, True):
		# 		match_filter_index.append(num_index)
		print(num_index,"/",len(df))
		if df.loc[num_index].author == "django":
			continue
		if match_filter_str(df.loc[num_index].title, filter_str) or match_filter_str(df.loc[num_index].body, filter_str):
			key = df.loc[num_index].author+"_"+df.loc[num_index].repo
			if key in repo_django_errors:
				if filter_str in repo_django_errors[key]:
					repo_django_errors[key][filter_str] += 1
				else:
					repo_django_errors[key][filter_str] = 1
				repo_django_errors[key]['total'] += 1
			else:
				repo_django_errors[key] = {'total': 1, filter_str: 1}
			if filter_str in count_django_errors:
				count_django_errors[filter_str] += 1
			else:
				count_django_errors[filter_str] = 1
			count_total_errors += 1
			match_filter_index.append(num_index)
			csv_writer.writerow([filter_str, df.loc[num_index].author, df.loc[num_index].repo, df.loc[num_index].html_url])
csvfile.close()

# write filter csv
with open("match_filter_index.json", "w") as f:
	json.dump(match_filter_index, f)
	df.loc[match_filter_index].to_csv("match_filter.csv")
print("match:", len(match_filter_index))

mi=match_filter_index
df.loc[mi].groupby('repo').count().to_csv("issue_repo_count.csv")

with open("repo_django_errors.json", "w") as fj:
	json.dump(repo_django_errors, fj)

with open("count_django_errors.json", "w") as fj:
	json.dump(count_django_errors, fj)


for k in count_django_errors:
	print("%s & %d & %s% \\\\ \\cline{2-4}"%(k, count_django_errors[k],  "{0:.2f}".format(count_django_errors[k]/count_total_errors)*100))



