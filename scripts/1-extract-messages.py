import json
import sys
import os

def extract(input_directory, output_file):
    """
    Extract messages from the JSON files in the input directory and write them to the output file.
    """
    messages = []

    # Process each file in the input directory
    for filename in os.listdir(input_directory):
        print("processing " + filename)
        if filename.endswith('.json'):
            file_path = os.path.join(input_directory, filename)

            # Open and read the JSON file with UTF-8 encoding
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Extract the messages with "type": "message"
            for item in data:
                if 'subtype' in item or 'type' not in item or item['type'] != 'message':
                    continue

                if len(item['text']) < 30:
                    continue

                message = {
                    'ts': item['ts'],
                    'text': item['text']
                }

                if 'client_msg_id' in item:
                    message['client_msg_id'] = item['client_msg_id']

                messages.append(message)

    # Write the combined messages to a singular output file
    if messages:
        with open(output_file, 'w') as f:
            json_string = json.dumps(messages, indent=4)
            f.write(json_string)
            print(f"Finished writing {len(messages)} messages to {output_file}")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: extract_messages.py <input_directory> <output_file>")
        sys.exit(1)

    input_directory = sys.argv[1]
    output_file = sys.argv[2]

    extract(input_directory, output_file)