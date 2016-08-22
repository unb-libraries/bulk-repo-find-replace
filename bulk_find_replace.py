#! /usr/bin/env python
# coding: utf-8
"""Iterates over Github repositories and commits find-replaces.
"""

from github import Github
from git import Repo
from optparse import OptionParser
import json
import shutil
import tempfile
import time
import os
import re

include_repo_match = ''
file_to_modify = os.path.join('build', 'make.yml')
pause_seconds = 30

parser = OptionParser()
parser.add_option(
    '-p',
    '--print',
    dest='print_only',
    help='Just print the results, do not update the repo',
    default=False,
    action='store_true'
)
(options, args) = parser.parse_args()
config = json.load(open(args[0]))

g = Github(config['github_auth_key'])
org_repos = g.get_organization('unb-libraries').get_repos()
num_repos = len(list(org_repos))
cur_repo_count = 0
for repo in org_repos:
    if include_repo_match == '' or include_repo_match in repo.name:
        cur_repo_count += 1
        print '[' + str(cur_repo_count) + '/' + str(num_repos) + '] Checking ' + repo.name + "\n"
        try:
            repo.get_file_contents(file_to_modify)

            if options.print_only:
                print '[DEBUG] Searching inside ' + repo.name

            tmp_dirpath = tempfile.mkdtemp()
            cur_repo = Repo.clone_from(repo.ssh_url, tmp_dirpath)

            makefile_has_commits = False

            for update in config['updates']:
                find_string = update['project'] + ":\n    version: '" + update['old']
                replace_string = update['project'] + ":\n    version: '" + update['new']
                commit_message = update['project'] + ' ' + update['old'] + ' -> ' + update['new']
                if 'comments' in update:
                    commit_message += ' ' + update['comments']
                file_to_edit = os.path.join(tmp_dirpath, file_to_modify)

                with open(file_to_edit, 'r+b') as editfile_pointer:
                    editfile_content = editfile_pointer.read()
                    if find_string in editfile_content:
                        editfile_content_updated = editfile_content.replace(find_string, replace_string)
                        editfile_pointer.seek(0)
                        editfile_pointer.write(editfile_content_updated)
                        editfile_pointer.truncate()
                        editfile_pointer.close()
                    if cur_repo.is_dirty():
                        print cur_repo.git.diff()
                        print cur_repo.git.add(file_to_modify)
                        print cur_repo.git.commit(m=commit_message)
                        makefile_has_commits = True
                        print cur_repo.git.status()

                if makefile_has_commits:
                    if options.print_only:
                        print "[DEBUG] Dry-run only. Not pushing to GitHub."
                    else:
                        print cur_repo.remotes.origin.push(cur_repo.head)

                    print "Sleeping for " + str(pause_seconds) + " seconds to be polite.."
                    time.sleep(pause_seconds)

            shutil.rmtree(tmp_dirpath)

        except:
            if options.print_only:
                print '[DEBUG] Skipping ' + repo.name
