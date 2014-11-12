#! /usr/bin/env python
"""Iterates over Github repositories and commits find-replaces.
"""

from github import Github
from git import Repo
import glob
import shutil
import tempfile
import time
import os

github_auth_key = ''
include_repo_match = 'build-profile'
files_to_modify = os.path.join('make', '*.makefile')
find_string = 'projects[views][version] = "3.7"'
replace_string = 'projects[views][version] = "3.8"'
commit_message = 'Views 3.7 -> 3.8 (BugzID : 1350)'
pause_seconds = 180

g = Github(github_auth_key)
for repo in g.get_organization("unb-libraries").get_repos():
    if include_repo_match in repo.name:
        tmp_dirpath = tempfile.mkdtemp()
        cur_repo = Repo.clone_from(repo.ssh_url, tmp_dirpath)
        for makefile_filepath in glob.glob(os.path.join(tmp_dirpath, files_to_modify)):
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
            print cur_repo.git.status()
            print cur_repo.remotes.origin.push(cur_repo.head)
            print "Sleeping for " + str(pause_seconds) + " seconds to be polite.."
            time.sleep(pause_seconds)
        shutil.rmtree(tmp_dirpath)
