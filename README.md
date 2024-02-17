# Embeddings-powered Slack Bot
This is a MVP slack bot I built in the context of a support channel (like IT or client hotfixes) that utilizes embeddings and a vector database for efficient semantic search. As bugs tend to resurface over time, or appear en masse when loose in production, similar or duplicate issues should exist in threads in the channel history. The bot searches and returns these similar threads when mentioned in a new message in the channel. These threads are rich in context and function as an easy way for developers and users to quickly establish a baseline for the problem they are solving, which means great efficiency gains. This repo contains the utility scripts to extract data from Slack messages dumps and store them into a vector database (AWS OpenSearch), as well as the actual Slack bot itself.

# TL;DR
TL;DR: A Slack bot that uses semantic search to find and share similar past bug reports from Slack history, helping give context into new issues. Includes data extraction scripts and integration with OpenAI and AWS OpenSearch.

# Why not just use CTRL + F?
Slack's CTRL + F functionality is great, but its only practical from a keyword searching perspective. [Semantic search](https://www.elastic.co/what-is/vector-search) is a far more powerful way of finding relevant messages, and can match entire documents at once. Plus, this bot saves the few minutes spent searching by providing the links directly in a reply to the thread.

# Usage
1) With workspace admin privileges, download your Slack workspace data in JSON form, and extract the channel that you would want to place the bot in

2) Setup your AWS OpenSearch clusters, or other vector database

3) Paste AWS/OpenAI keys into an .env file

4) Use the utility scripts to extract the relevant information from the raw data, put an index into OpenSearch, and finally upload all embedded messages

5) Serve the Slack bot from a virtual Python environment (for testing purposes, use ngrok to create a secure tunnel to your locally hosted instance)

6) Connect the Slack bot to your workspace (use the bot token) and ensure that the URL verification challenge is complete

7) Start querying the bot using '@<Bot Name>' to mention your bot! Congrats, you now have a fully functioning channel assistant that is trained on the context of your entire channel history!