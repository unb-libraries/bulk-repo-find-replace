#! /usr/bin/env python
# coding: utf-8
"""Iterates over Github repositories and commits prints those containing the specified file.
"""

from github import Github
from git import Repo
from optparse import OptionParser
import base64
import json
import shutil
import tempfile
import time
import os
import re

include_repo_match = ''
file_to_modify = os.path.join('build', 'composer.json')
pause_seconds = 30

parser = OptionParser()
(options, args) = parser.parse_args()
config = json.load(open(args[0]))

g = Github(config['github_auth_key'])
org_repos = g.get_organization('unb-libraries').get_repos()
num_repos = len(list(org_repos))

for repo in org_repos:
    if include_repo_match == '' or include_repo_match in repo.name:
        try:
            repo_needs_update = False
            file_contents = repo.get_file_contents(file_to_modify)
            print repo.name
        except:
            pass
