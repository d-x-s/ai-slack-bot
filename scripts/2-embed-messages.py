import sys
import os
import json
import argparse
from tqdm import tqdm

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from auth.openai_auth import get_openai_client

openai_client = get_openai_client()

def load_json_objects(file_path):
    """
    Parse individual JSON objects from a file and return them as a list.
    """
    with open(file_path, 'r') as file:
        return json.load(file)

def get_embeddings(client, textArray, model="text-embedding-ada-002"):
    """
    Get embeddings for the given text array using the specified model.
    """
    try:
        return client.embeddings.create(input = textArray, model=model).data
    except Exception as e:
        print("Error occurred while getting embeddings:", e)
        return None

def process_in_batches(data, batch_size):
    """
    Process the data in batches of the specified size.
    """
    for i in range(0, len(data), batch_size):
        yield data[i:i + batch_size]

def embed(input_file_path, output_file_path):
    """
    Embed the messages in the input file and save the augmented data to the output file.
    """
    data = load_json_objects(input_file_path)
    batch_size = 64

    for batch in tqdm(process_in_batches(data, batch_size), desc="Processing batches"):
        texts = [item['text'] for item in batch]

        embeddingsList = get_embeddings(openai_client, texts)

        if len(embeddingsList) != batch_size:
            print("some embeddings failed?")

        if embeddingsList:
            for i, item in enumerate(batch):
                item['embedding'] = embeddingsList[i].embedding

    with open(output_file_path, 'w') as outfile:
        json.dump(data, outfile, indent=4)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: script.py <input_file_path> <output_file_path>")
        sys.exit(1)
    
    input_file_path = sys.argv[1]
    output_file_path = sys.argv[2]

    embed(input_file_path, output_file_path)