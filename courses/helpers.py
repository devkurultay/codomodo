import json
import requests

from django.conf import settings

def run_code(submitted_code, programming_language):
    msg = '{}: should not be empty'
    if not submitted_code:
        raise ValueError(msg.format('sumitted_code'))
    if not programming_language:
        raise ValueError(msg.format('programming_language'))

    if programming_language.lower() == 'python':
        url = settings.AWS_PYTHON_EXEC_LAMBDA_URL
        #TODO(murat): Append unit test code to the submission code
        payload = json.dumps({'answer': submitted_code})
        res = requests.post(url, payload)
        return res.json()
    return 'output'