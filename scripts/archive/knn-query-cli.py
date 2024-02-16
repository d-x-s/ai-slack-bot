import requests
import json
import sys
from requests_aws4auth import AWS4Auth
from openai import OpenAI

# Check that the correct number of command-line arguments were provided
if len(sys.argv) != 2:
    print("Usage: knn_query.py <text_to_query>")
    sys.exit(1)

# Get the input string
user_text = sys.argv[1]

# embed it with OpenAI
client = OpenAI(api_key='')
generated_embedding = client.embeddings.create(input = [user_text], model="text-embedding-ada-002").data[0].embedding

# Replace with your AWS access key, secret key, and region
aws_access_key_id = ''
aws_secret_access_key = ''
aws_region = ''
opensearch_endpoint_url = ''
index_name=''

# Initialize AWS authentication
auth = AWS4Auth(aws_access_key_id, aws_secret_access_key, aws_region, 'es')

# Define the search query
query = {
 "size": 4,
 "query": {
   "script_score": {
     "query": {
       "match_all": {}
     },
     "script": {
       "source": "knn_score",
       "lang": "knn",
       "params": {
         "field": "embedding",
         "query_value": generated_embedding,
         "space_type": "cosinesimil"
       }
     }
   }
 }
}

query_json = json.dumps(query)
search_url = f'{opensearch_endpoint_url}/{index_name}/_search'
headers = {'Content-Type': 'application/json'}

# Send the POST request to the search endpoint with the query
response = requests.post(search_url, headers=headers, data=query_json, auth=auth)

text_combined = ''

if response.status_code == 200:
    response_json = json.loads(response.content)

    hits = response_json['hits']['hits']

    for hit in hits[:4]:
        print(f'Score: {hit["_score"]}, Text: {hit["_source"]["text"]}')
        text_combined += hit['_source']['text'] + ' '
else:
    print(f'Error searching index: {response.content}')