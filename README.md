# MiniChat

MiniChat is a flexible and extensible chat application that supports multiple AI models and providers.

## Features

- Support for multiple AI providers:
  - OpenAI
  - Claude (Anthropic)
  - Coze
- Configurable settings for each provider
- SQLite database for storing chat history
- Flask-based API for chat interactions
- Streaming responses for real-time chat experience

## Installation

1. Clone the repository
2. Install the required dependencies:
   This project requires [rye](https://rye-up.com/getting-started/) to install dependencies.
   Or you can use pip to install manually.
3. Set up your configuration in `src/minichat/minichat.json`

## Configuration

The `minichat.exanple.json` file contains all the necessary configurations for the application. Copy it as `minichat.json` and fill in the appropriate values for your environment.

## Usage

1. Start the chat server:
   ```
   rye run guniorn -w 4 -b 0.0.0.0:5000 --timeout 120 server_run:app
   ```

2. You can access the chat interface by visiting `http://0.0.0.0:5000` in your browser.

3. Or you can use the cmd client to send message to the server:
   The client repository is here: https://github.com/26awen/mncc
