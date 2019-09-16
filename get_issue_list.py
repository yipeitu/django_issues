import requests
import json
import csv
import time
import re
import base64
import traceback

TOKEN = 'GITHUB_TOKEN'

class DjangoIssue(object):
	def __init__(self, author, repo, issue):
		self.author = author
		self.repo = repo
		if type(issue) != dict:
			issue = dict()
		self.state = issue.get('state', '')
		self.number = issue.get('number', '')
		self.title = re.sub(u"(\u2018|\u2019)", "'", issue.get('title', ''))
		self.body = re.sub(u"(\u2018|\u2019)", "'", issue.get('body', ''))
		self.labels = re.sub(u"(\u2018|\u2019)", "'", json.dumps(issue.get('labels', [])))
		self.comments_num = int(issue.get('comments', 0))
		self.html_url = issue.get('html_url')
		self.comments_url = issue.get('comments_url', '')
		self.comments = []

	def output(self):
		print('state:', self.state)
		print('title: ', self.title)
		print('body: ', self.body)
		print('labels: ', self.labels)

	def get_comments(self):
		if len(self.comments_url) == 0:
			return
		r = requests.get(self.comments_url, params={'sort':'creates', 'sort':'asc'}, headers={'Authorization': 'token %s' % TOKEN})
		data = r.json()
		num = 1
		for d in data:
			self.body += ('[comment'+str(num)+'] '+d.get('body', '')+'\n')
			num += 1

	def write_to_csv(self, csv_writer, page_num):
		try:
			csv_writer.writerow([
				self.author,
				self.repo,
				page_num,
				self.state,
				self.number,
				self.comments_num,
				self.comments_url,
				self.html_url,
				self.labels.encode('utf-8'),
				self.title.encode('utf-8'),
				self.body.encode('utf-8')
			])
		except:
			csv_writer.writerow([
				self.author,
				self.repo,
				page_num,
				self.state,
				self.number,
				self.comments_num,
				self.comments_url,
				self.html_url,
				base64.b64encode(self.labels.encode('utf-8')),
				base64.b64encode(self.title.encode('utf-8')),
				base64.b64encode(self.body.encode('utf-8'))
			])

	def write_to_txt(self, txt_writer, page_num):
		txt_writer.write("----------------------------------------")
		txt_writer.write(self.author)
		txt_writer.write(self.repo)
		txt_writer.write(str(page_num))
		txt_writer.write(self.state)
		txt_writer.write(str(self.number))
		txt_writer.write(str(self.comments_num))
		txt_writer.write(self.comments_url)
		txt_writer.write(self.html_url)
		txt_writer.write(self.labels)
		txt_writer.write(self.title)
		txt_writer.write(self.body)
		txt_writer.write("----------------------------------------")


url = "https://api.github.com/repos/%s/issues?page=%d&per_page=100"
repos = json.load(open("repos.json"))
csvfile = open("issues.csv", "a")
csv_writer = csv.writer(csvfile)
csv_writer.writerow(['author', 'repo', 'page_num', 'state', 'issue.number', 'comments_num', 'comments_url', 'html_url', 'labels', 'title', 'body'])
txtfile = open("issues.txt", "a")
errorfile = open("error.txt", "a")

for repo in repos:
	page_num = 1
	while True:
		r = requests.get(url%(repo, page_num), params={'state': 'closed'}, headers={'Authorization': 'token %s' % TOKEN})
		issues = r.json()
		print(len(issues))
		page_num += 1
		
		if type(issues) == dict:
			r_remain = requests.get("https://api.github.com/rate_limit")
			d_remain = r_remain.json()
			w_time = d_remain.get('resources', {}).get('integration_manifest', {}).get('reset', time.time()+3600)
			print("wait until: ", time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(w_time)))
			csvfile.close()
			txtfile.close()
			## sleep
			time.sleep(w_time-time.time())
			csvfile = open("issues.csv", "a")
			csv_writer = csv.writer(csvfile)
			txtfile = open("issues.txt", "a")
		elif len(issues) == 0:
			print(issues)
			break
		issue_num = 0
		for issue in issues:
			try:
				d_issue = DjangoIssue(repo.split("/")[0], repo.split("/")[1], issue)
				d_issue.write_to_csv(csv_writer, page_num)
				d_issue.write_to_txt(txtfile, page_num)
				issue_num += 1
				print("repo: ", repo, "page: ", page_num, " issue: ", issue_num)
			except Exception as e:
				print("error:", traceback.format_exc())
				errorfile.write(issue['html_url'])
				errorfile.write(traceback.format_exc())

csvfile.close()
txtfile.close()
errorfile.close()
