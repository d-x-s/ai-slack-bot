import sys
import os
import requests
from requests_aws4auth import AWS4Auth

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth.aws_auth import get_aws_auth

def create_index(opensearch_endpoint_url, index_name, aws_client):
    """
    Put the index to OpenSearch.
    """
    mapping_properties = {
        "ts": {"type": "text"},
        "text": {"type": "text"},
        "embedding": {
            "type": "knn_vector",
            "dimension": 1536,
            "method": {
                "name": "hnsw",
                "space_type": "cosinesimil",
                "engine": "nmslib"
            }
        }
    }

    index_settings = {
        'settings': {
            'index.knn': True
        },
        'mappings': {
            'properties': mapping_properties
        }
    }

    index_url = f'{opensearch_endpoint_url}/{index_name}'
    response = requests.put(index_url, headers={"Content-Type": "application/json"}, auth=aws_client, json=index_settings)

    if response.status_code == 200:
        print(f'Index "{index_name}" successfully created.')
    else:
        print(f'Error creating index: {response.content}')
        sys.exit(1)

def put_index():
    opensearch_endpoint_url = os.environ['AWS_OPENSEARCH_URL']
    index_name = os.environ['AWS_OPENSEARCH_INDEX_NAME']
    aws_client = get_aws_auth()
    create_index(opensearch_endpoint_url, index_name, aws_client)

if __name__ == "__main__":
    put_index()