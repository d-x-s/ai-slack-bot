import os
from requests_aws4auth import AWS4Auth

def get_aws_auth():
    """
    Return the authenticated AWS client.
    """
    aws_access_key_id = os.environ['AWS_ACCESS_KEY_ID']
    aws_secret_access_key = os.environ['AWS_SECRET_ACCESS_KEY']
    aws_region = os.environ['AWS_REGION']

    auth = AWS4Auth(aws_access_key_id, aws_secret_access_key, aws_region, 'es')
    return auth