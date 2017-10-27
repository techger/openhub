#!/usr/bin/env python
# coding=utf-8

import sys
from requests import session
from bs4 import BeautifulSoup as bs
import json

headers = {
    'Origin': 'https://github.com',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-EN,en;q=0.8,en;q=0.6',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) \
        AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Cache-Control': 'max-age=0',
    'Referer': 'https://github.com/',
    'Connection': 'keep-alive',
}


class Traffic:
    def __init__(self, username, password):
        s = session()
        login_url = "https://github.com/login"
        session_url = "https://github.com/session"
        req = s.get(login_url).content 
        html_object = bs(req, "html.parser")
        token = html_object.find("input", {"name": "authenticity_token"}).attrs['value']
        com_val = html_object.find("input", {"name": "commit"}).attrs['value']  
        login_data = {'login': username,
                    'password': password,
                    'commit' : com_val,
                    'authenticity_token' : token}    
        login_req = s.post(session_url, data = login_data, headers=headers)
        html_object = bs(login_req.content, "html.parser")
        self.login = html_object.find("meta", {"name": "octolytics-actor-login"}).attrs["content"]
        self.s = s
        self.cache = False

    def cache_repo(self, repo_name):
        clone_data_url = "https://github.com/{}/{}/graphs/clone-activity-data".format(self.login, repo_name)
        traffic_data_url = "https://github.com/{}/{}/graphs/clone-activity-data".format(self.login, repo_name)
        top_list_url = "https://github.com/{}/{}/graphs/traffic?partial=top_lists".format(self.login, repo_name)
        self.top_list_data = self.s.get(top_list_url, headers=headers).content
        headers["Referer"] = "https://github.com/binhe22/pullword/graphs/traffic"
        headers["Accept"] = "application/json"
        self.clone_data = self.s.get(clone_data_url, headers=headers)
        self.traffic_data = self.s.get(traffic_data_url, headers=headers)
        self.cache = True

    def get_reffer_sites(self):
        top_list_data = bs(self.top_list_data, "html.parser")
        reffer_sites_tr = top_list_data.find("tbody").findAll("tr")
        reffer_sites_list = []
        for i in reffer_sites_tr:
            reffer_site = []
            for j in i.findAll("td"):
                    reffer_site.append(j.getText().strip())
            reffer_sites_list.append(reffer_site)
        return reffer_sites_list

    def get_popular_content(self):
        top_list_data = bs(self.top_list_data, "html.parser")
        popular_content_tr = top_list_data.select(".top-content")[0].find("tbody").findAll("tr")
        popular_content_list = []
        for i in popular_content_tr:
            popular_content = []
            for j in i.findAll("td"):
                popular_content_list.append(j.getText().strip())
        return popular_content_list

    def get_clone_data(self):        
        return json.loads(self.clone_data.content)["counts"]

    def get_visit_data(self):
        return json.loads(self.traffic_data.content)["counts"]

    def get_all_data(self, repo_name=None):
        if repo_name:
            self.cache_repo(repo_name)
        if not self.cache:
            return None
        data_dict = {}
        data_dict["viist_data"] = self.get_visit_data()
        data_dict["clone_data"] = self.get_clone_data()
        data_dict["reffer_sites"] = self.get_reffer_sites()
        data_dict["popular_content"] = self.get_popular_content()
        return data_dict

if __name__ == "__main__":
    inputs = sys.argv    
    if len(inputs) != 4:
        print """
        args num is wrong, you can use by:
        ./repo_traffic.py username password repo_name
        for example:
        ./repo_traffic.py ***@gmail.com 12312312 repo_traffic
        """
    username = sys.argv[1]
    password = sys.argv[2]
    repo_name = sys.argv[3]
    repo_traffic = Traffic(username, password)
    repo_traffic.cache_repo(repo_name)
    print repo_traffic.get_all_data()
    print repo_traffic.get_visit_data()
    print repo_traffic.get_clone_data()
    print repo_traffic.get_reffer_sites()
    print repo_traffic.get_popular_content()
