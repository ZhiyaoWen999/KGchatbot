# KGchatbot

KGchatbot is a knowledge graph-based chatbot built using Neo4j and Python. It leverages the power of graph databases to provide informative responses based on a predefined knowledge graph structure. This project is ideal for educational purposes or as a foundation for more complex chatbot systems that require an understanding of relationships and properties within a dataset.

## Features

- Integration with Neo4j for graph database management.
- Use of OpenAI's GPT models for natural language understanding.
- Customizable queries for fetching and displaying data from Neo4j.
- Simple RESTful API setup for interaction with the chatbot.

## Prerequisites

Before you begin, ensure you have met the following requirements:
- Python 3.8 or higher
- Neo4j Database
- OpenAI API key 

## Installation

Follow these steps to get your development environment running:

1.Clone the repository:

```bash
git clone https://github.com/ZhiyaoWen999/KGchatbot.git
```

2.Navigate to the project directory:

```bash
cd KGchatbot
```

3.Install the required Python packages:

```bash
pip install -r requirements.txt
```

4.Set up environment variables for sensitive data such as the OpenAI API key:

```bash
openai.api_key ='your_api_key_here'
```

## Usage

To start the server and interact with the chatbot, run:

python chatbot.py

## Contributing
Contributions to KGchatbot are welcome. If you have suggestions for improving KGchatbot, please fork the repo and create a pull request, or open an issue with the tag "enhancement".


## License
This project is licensed under the MIT License - see the LICENSE file for details.

This README provides a complete guide to setting up and using the KGchatbot, making it easy for users to understand the project's purpose, setup, and usage. Ensure you replace placeholders like `"your-openai-api-key"` with actual working values before deployment.
