#! /usr/bin/env python
# coding: utf-8
"""Iterates over Github repositories and commits find-replaces.
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
file_to_modify = os.path.join('Dockerfile')
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

for repo in org_repos:
    if include_repo_match == '' or include_repo_match in repo.name:
        try:
            repo_needs_update = False
            file_contents = repo.get_file_contents(file_to_modify)

            assert file_contents.encoding == "base64", "unsupported encoding: %s" % file_contents.encoding
            file_data = base64.b64decode(file_contents.content)

            for update in config['updates']:
                if update['old'] in file_data:
                    repo_needs_update = True
                    break

            if repo_needs_update:
                tmp_dirpath = tempfile.mkdtemp()
                cur_repo = Repo.clone_from(repo.ssh_url, tmp_dirpath)

                file_to_edit = os.path.join(tmp_dirpath, file_to_modify)
                print file_to_edit
                with open(file_to_edit, 'r+') as f:
                    file_data = f.read()

                for update in config['updates']:
                    if update['old'] in file_data:
                        file_data = file_data.replace(update['old'], update['new'])
                        with open(file_to_edit, 'w') as f:
                            f.write(file_data)
                            f.truncate()

                        commit_message = update['comments']

                        print cur_repo.git.add(file_to_modify)
                        print cur_repo.git.commit(m=commit_message)

                if options.print_only:
                    print "[DEBUG] Dry-run only. Not pushing to GitHub."
                else:
                    print cur_repo.remotes.origin.push(cur_repo.head)

                shutil.rmtree(tmp_dirpath)

                print "Sleeping for " + str(pause_seconds) + " seconds to be polite.."
                time.sleep(pause_seconds)

        except:
            if options.print_only:
                print '[DEBUG] Skipping ' + repo.name
