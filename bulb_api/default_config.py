import re


AWS_REGION = 'us-east-1'

CORS_CFG = {
    # 'origins': [
        # re.compile('^(dev|api|)\.{0,1}buttaface\.space$'),
        # re.compile('localhost:[0-9]{1,4}'),
    # ],
    'supports_credentials': True,
    'max_age': 600,    # while firefox allows 1d, chrome only allows 10m
}
