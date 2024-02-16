import os
import sys
import re
import requests
import json
import slack_sdk as slack

from dotenv import load_dotenv
from flask import Flask, jsonify
from slackeventsapi import SlackEventAdapter

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth.aws_auth import get_aws_auth
from auth.openai_auth import get_openai_client

aws_client = get_aws_auth()

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Initialize Slack WebClient
client = slack.WebClient(token=os.environ['SLACK_BOT_TOKEN'])

# Initialize SlackEventAdapter and link it to your Flask app
slack_event_adapter = SlackEventAdapter(
    os.environ['SLACK_SIGNING_SECRET'], "/slack/events", app
)

BOT_ID = client.api_call("auth.test")['user_id']

@slack_event_adapter.on("url_verification")
def handle_challenge(event_data):
    return jsonify({"challenge": event_data["challenge"]})

@slack_event_adapter.on("message")
def handle_message(event_data):
    """
    Slack event handler for message events.
    """
    message = event_data["event"]

    # Check if the message is not from the bot itself and contains a mention
    if "bot_id" not in message and BOT_ID in message["text"]:
        # Extract the text of the message (excluding mentions)
        mentioned_text = message["text"].replace(f"<@{BOT_ID}>", "").strip()

        outputText = query(mentioned_text)

        # Respond in the same thread
        client.chat_postMessage(
            channel=message["channel"],
            text=outputText,
            thread_ts=message["ts"],  # Thread timestamp to reply in the same thread
        )

def clean_and_truncate(text):
    """
    Remove non-standard characters and truncate the text to 150 characters.
    """
    text = text.replace('\n', ' ')
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    if len(text) > 150:
        text = text[:150] + '…'
    return text

def query(text):
    """
    Query OpenAI with the input text and return the top 3 similar messages.
    Uses cosine similarity to find similar messages.
    """
    openai_client = get_openai_client()
    generated_embedding = openai_client.embeddings.create(input = [text], model="text-embedding-ada-002").data[0].embedding
  
    opensearch_endpoint_url = os.environ['AWS_OPENSEARCH_URL']
    index_name              = os.environ['AWS_OPENSEARCH_INDEX_NAME']

    aws_client = get_aws_auth()

    query = {
        "size": 3,
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
    response = requests.post(search_url, headers=headers, data=query_json, auth=aws_client)

    text_combined = 'I found some similar problems users faced in the past:' + '\n' 

    if response.status_code == 200:
        response_json = json.loads(response.content)

        hits = response_json['hits']['hits']

        for hit in hits[:3]:
            score = hit["_score"]
            text = hit["_source"]["text"]
            timestamp = hit["_source"]["ts"]
            slack_link = f"https://company.slack.com/archives/{timestamp}" # Replace with your Slack workspace name

            print(f'Score: {score}, Text: {text}, Timestamp: {timestamp}')
            text_combined += f"• <{slack_link}|{clean_and_truncate(text)}>\n\n"

        return text_combined

    else:
        print(f'Error searching index: {response.content}')
        return "Error querying message database."

if __name__ == "__main__":
    app.run(port=3000)