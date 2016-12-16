"""This module loads all of the jsonschemas for validating
request and response bodies.
"""

import json
import os


def _load_jsonschema(schema_name):
    filename = os.path.join(
        os.path.dirname(__file__), 'jsonschemas', '%s.json' % schema_name)
    with open(filename) as fp:
        return json.load(fp)


create_tasks_request = _load_jsonschema('create_tasks_request')

create_tasks_response = _load_jsonschema('create_tasks_response')
