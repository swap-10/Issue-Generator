import requests
import json
import csv
import os
from dotenv import load_dotenv

load_dotenv()

class APIError(Exception):
    """An API Error Exception"""

    def __init__(self, status):
        self.status = status

    def __str__(self):
        return "APIError: status={}".format(self.status)


class GitHub(object):
    def __init__(self, **config_options):
        self.__dict__.update(**config_options)
        self.calls = 500
        self.session = requests.Session()
        if hasattr(self, 'api_token'):
           self.session.headers['Authorization'] = 'token %s' % self.api_token
        elif hasattr(self, 'username') and hasattr(self, 'password'):
           self.session.auth = (self.username, self.password)

    def call_to_the_api(self, url):
        # do stuff with args
        self.calls += 1
        if self.calls % 100 == 0:
            print(f'Calls: {self.calls}')
        return self.session.get(url)

def get_repos(username, repo_file):
    page = 1
    resp = github.call_to_the_api(f'https://api.github.com/users/{username}/repos?type=all&per_page=100&page={page}')
    if resp.status_code != 200:
        raise APIError(resp.status_code)
    else:
        while (len(resp.json())>0):
            with open(repo_file, 'a', encoding='utf-8') as f:
                for item in resp.json():
                    f.write(item['full_name'] + '\n')
            page += 1
            resp = github.call_to_the_api(f'https://api.github.com/users/{username}/repos?type=all&per_page=100&page={page}')
            if resp.status_code != 200:
                raise APIError(resp.status_code)

def get_issues(reponame, issues_file):
    page = 1
    resp = github.call_to_the_api(f'https://api.github.com/repos/{reponame}/issues?state=all&per_page=100&page={page}')
    if resp.status_code != 200:
        raise APIError(resp.status_code)
    else:
        while (len(resp.json())>0):
            with open(issues_file, 'a', encoding='utf-8') as f:
                for item in resp.json():
                    f.write(item['title'] + '\n')
            page += 1
            resp = github.call_to_the_api(f'https://api.github.com/repos/{reponame}/issues?state=all&per_page=100&page={page}')
            if resp.status_code != 200:
                raise APIError(resp.status_code)


def get_all_repos(users_file, repo_file):
    with open(users_file, 'r', encoding='utf-8') as users, open(repo_file, 'a', encoding='utf-8') as repos:
        reader = csv.reader(users)
        for row in reader:
            get_repos(row[0], repo_file)
        


def get_all_issues(repo_file, issues_file):
    with open(repo_file, 'r', encoding='utf-8') as repos, open(issues_file, 'a', encoding='utf-8') as issues:
        reader = csv.reader(repos)
        repos_done = 0
        for row in reader:
            get_issues(row[0], issues_file)
            repos_done += 1
            if repos_done % 10 == 0:
                print(repos_done)


API_TOKEN = os.environ.get("API_TOKEN")
github = GitHub(api_token=API_TOKEN)

get_all_repos('users.csv', 'repos.csv')
get_all_issues('repos.csv', 'issues.csv')

print("End")