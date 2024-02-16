import sys
import os
import requests
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth.aws_auth import get_aws_auth

opensearch_endpoint_url = os.environ['AWS_OPENSEARCH_URL']
index_name              = os.environ['AWS_OPENSEARCH_INDEX_NAME']
aws_client = get_aws_auth()

def upload_data_from_file(json_file_path):
    """
    Function to upload data from a JSON file to OpenSearch.
    """
    try:
        with open(json_file_path, 'r') as file:
            embeddings_data = json.load(file)
    except FileNotFoundError:
        print(f"File not found: {json_file_path}")
        return

    # Construct the OpenSearch endpoint URL
    endpoint_url = f'{opensearch_endpoint_url}/{index_name}/_doc'
    headers = {'Content-Type': 'application/json'}

    # Loop through each embedded message and post it to the endpoint
    for data in embeddings_data:
        json_data = json.dumps(data)
        response = requests.post(endpoint_url, headers=headers, data=json_data, auth=aws_client)
        print(f'Response Status Code: {response.status_code}')

        if response.status_code != 201:
            print(f'Error posting data: {response.status_code} {data["ts"]}')
            continue
        print(f'Success posting data: {response.status_code} {data["ts"]}')

    print('Upload completed.')

# Usage: Provide the path to your JSON file as a command-line argument
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: python upload_data.py <path_to_json_file>')
    else:
        json_file_path = sys.argv[1]
        upload_data_from_file(json_file_path)
