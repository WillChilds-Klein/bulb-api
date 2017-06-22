# import re


AWS_REGION = 'us-east-1'

CORS_CFG = {
    # 'origins': [
        # re.compile('^(dev|api|)\.{0,1}buttaface\.space$'),
        # re.compile('localhost:[0-9]{1,4}'),
    # ],
    'supports_credentials': True,
    'max_age': 600,    # while firefox allows 1d, chrome only allows 10m
}

DATETIME_FMT = '%Y-%m-%dT%H:%M:%SZ'

# use a set for O(1) lookup
HIDDEN_ATTRIBUTES = {
    'password',
    'password_hash',
}

AUTH_PORT = 9090

PASSWORD_HASH_METHOD = 'pbkdf2:sha256'  # TODO: this isn't explicitly used
PASSWORD_SALT_LENGTH = 8                # TODO: this isn't explicitly used

TOKEN_SIGNING_ALGORITHM = 'HS256'   # TODO: this isn't explicitly used
TOKEN_SECRET_KEY = 'yourmom'        # should auto-regenerate this periodically
TOKEN_LIFESPAN_SECONDS = 60*60      # 1 hr (in sec.), for now
