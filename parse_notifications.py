#! /usr/bin/env python
# coding: utf-8
"""Parses notifications of updates and generates json for config.json
"""
import json

updates = {}

columns_validate = 8
type_column = 2

type_filter = ['DrupalDocker']
project_omit_filter = []
version_strip_filter = '8.x-'

# The stop character.
sentinel = ''

for line in iter(raw_input, sentinel):
    if '|' in line:
        fields = line.split('|')
        if len(fields) == columns_validate:
            if fields[type_column].strip() in type_filter:
                [project, type] = fields[6].split('(')
                project = project.strip()
                if project == 'drupal':
                    project = 'core'
                type_string = type
                type = type.replace(')', '').strip()
                update_entry = {
                    'project': project.strip(),
                    'old': fields[4].replace(version_strip_filter, '').strip(),
                    'new': fields[5].replace(version_strip_filter, '').strip(),
                    'comments': type.strip()
                }
                updates[type_string] = update_entry

if len(updates) != 0:
    print json.dumps(updates.values(), indent=4)
