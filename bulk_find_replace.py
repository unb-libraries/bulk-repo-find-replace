#! /usr/bin/env python
# coding: utf-8
"""Iterates over Github repositories and commits find-replaces.
"""

from github import Github
from git import Repo
import glob
import shutil
import tempfile
import time
import os

updates_needed = [
    {
        'project_name': 'search_api',
        'old_version': '1.17',
        'new_version': '1.18',
        'commit_comments': 'search_api 1.17->1.18 (SA-CONTRIB-2016-022) :boom:'
    },
    {
        'project_name': 'features',
        'old_version': '2.9',
        'new_version': '2.10',
        'commit_comments': 'features 2.9->2.10 (Feature Update) :boom:'
    },
]

github_auth_key = ''
include_repo_match = 'build-profile'
files_to_modify = os.path.join('make', '*.makefile')
pause_seconds = 30

g = Github(github_auth_key)
for repo in g.get_organization("unb-libraries").get_repos():
    if include_repo_match in repo.name:
        tmp_dirpath = tempfile.mkdtemp()
        cur_repo = Repo.clone_from(repo.ssh_url, tmp_dirpath)

        for makefile_filepath in glob.glob(os.path.join(tmp_dirpath, files_to_modify)):
            makefile_has_commits = False

            for update in updates_needed:
                find_string = 'projects[' + update['project_name'] + '][version] = "' + update['old_version'] + '"'
                replace_string = 'projects[' + update['project_name'] + '][version] = "' + update['new_version'] + '"'
                commit_message = update['project_name'] + ' ' + update['old_version'] + ' -> ' + update['new_version'] + ' ' + update['commit_comments']

                with open(makefile_filepath, 'r+b') as editfile_pointer:
                    editfile_content = editfile_pointer.read()
                    if find_string in editfile_content:
                        editfile_content_updated = editfile_content.replace(find_string, replace_string)
                        editfile_pointer.seek(0)
                        editfile_pointer.write(editfile_content_updated)
                        editfile_pointer.truncate()
                        editfile_pointer.close()
                    if cur_repo.is_dirty():
                        print cur_repo.git.diff()
                        print cur_repo.git.add(files_to_modify)
                        print cur_repo.git.commit(m=commit_message)
                        makefile_has_commits = True
                        print cur_repo.git.status()

            if makefile_has_commits:
                print cur_repo.remotes.origin.push(cur_repo.head)
                print "Sleeping for " + str(pause_seconds) + " seconds to be polite.."
                time.sleep(pause_seconds)

        shutil.rmtree(tmp_dirpath)
