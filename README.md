

# Gemini Telegram Bot

Gemini Telegram Bot is a versatile and intelligent Telegram bot built to provide context-aware responses, handle web searches, process images, and retrieve system information. Developed with a focus on natural language understanding, Gemini Telegram Bot leverages Google's Gemini AI model and integrates various libraries for comprehensive functionality.

## Features

- **Asynchronous Communication:** Utilizes `telebot` and `asyncio` for efficient, non-blocking message handling.
- **AI Response Generation:** Integrates with Google's Gemini AI model to generate accurate and intelligent responses.
- **Web Search:** Employs DuckDuckGo Search to provide relevant web search results.
- **Image Processing:** Capable of processing and describing images sent by users.
- **System Information Retrieval:** Provides detailed system information including CPU, RAM, and disk usage.
- **Spam Prevention:** Implements basic spam prevention mechanisms to ensure fair usage.

## Requirements

This project requires the following Python libraries:

- `telebot`
- `asyncio`
- `google-generativeai`
- `pillow`
- `psutil`
- `aiohttp`
- `duckduckgo-search`
- `qrcode`

These dependencies are listed in the `requirements.txt` file.

## Installation

### Step 1: Clone the Repository

First, clone the repository to your local machine using Git:

```bash
git clone https://github.com/yourusername/Gemini_Telegram_Bot.git
cd Gemini_Telegram_Bot
```

### Step 2: Install Dependencies

You can install the required Python libraries using `pip`. It's recommended to use a virtual environment to avoid conflicts with other projects.

#### On Ubuntu:

1. **Update and Install Python3 and pip:**

    ```bash
    sudo apt update
    sudo apt install python3 python3-pip python3-venv
    ```

2. **Create a Virtual Environment:**

    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. **Install the Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

### Step 3: Configure API Keys

Ensure you have your API keys for Telegram and Google. Update the `BOT_TOKEN` and `GOOGLE_API_KEYS` variables in `bot.py` with your keys.

```python
BOT_TOKEN = 'your-telegram-bot-token'
GOOGLE_API_KEYS = [
    'your-google-api-key-1',
    'your-google-api-key-2',
    ...
]
```

### Step 4: Run the Bot

Start the bot using the following command:

```bash
python bot.py
```

The bot will begin polling for messages and respond accordingly.

## Usage

### Bot Commands

- **/start:** Start the bot and receive a welcome message.
- **/ask [question]:** Ask a question to the bot.
- **/clear:** Clear the chat history.
- **/info:** Get system information.
- **/switch:** Switch the AI model.

### Example Usage

1. **Start the Bot:**

    Send `/start` to initiate the bot and receive a greeting.

2. **Ask a Question:**

    Send `/ask What is the weather like today?` to get a response from the bot.

3. **Clear Chat History:**

    Send `/clear` to reset the conversation history.

4. **Get System Information:**

    Send `/info` to retrieve detailed system information.

5. **Switch AI Model:**

    Send `/switch` and select a model from the options provided.

## Files

- **bot.py:** The main bot script containing all the functionality.
- **requirements.txt:** Lists all the required Python libraries.
- **Dockerfile:** Docker configuration for containerizing the application.
- **Procfile:** Configuration for deploying to Heroku.
- **vercel.json:** Configuration for deploying to Vercel.
- **LICENSE:** License information.
- **README.md:** This README file.

## Running on Google Colab

You can also run the bot on Google Colab. Use the following command to set up and run the bot:

```python
!apt-get update && git clone https://github.com/yourusername/Gemini_Telegram_Bot.git && cd Gemini_Telegram_Bot && pip install -r requirements.txt && python bot.py
```

## Docker Setup

To run the bot using Docker:

1. **Build the Docker Image:**

    ```bash
    docker build -t gemini-telegram-bot .
    ```

2. **Run the Docker Container:**

    ```bash
    docker run -d --name gemini-bot gemini-telegram-bot
    ```

## Deployment

### Heroku

1. **Login to Heroku:**

    ```bash
    heroku login
    ```

2. **Create a New Heroku App:**

    ```bash
    heroku create your-app-name
    ```

3. **Deploy the Code:**

    ```bash
    git push heroku main
    ```

4. **Set Environment Variables:**

    ```bash
    heroku config:set BOT_TOKEN=your-telegram-bot-token
    heroku config:set GOOGLE_API_KEYS=your-google-api-key-1,your-google-api-key-2
    ```

[![Deploy on Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

### Railway

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new)

### Vercel

1. **Login to Vercel:**

    ```bash
    vercel login
    ```

2. **Deploy the Project:**

    ```bash
    vercel --prod
    ```

### Koyeb

[![Deploy on Koyeb](https://www.koyeb.com/static/images/deploy/button.svg)](https://app.koyeb.com/deploy)

## Contributing

We welcome contributions! Please fork the repository and submit pull requests.

### Steps to Contribute:

1. **Fork the Repository**

    Click the "Fork" button at the top-right corner of this repository's page.

2. **Clone Your Fork**

    ```bash
    git clone https://github.com/yourusername/Gemini_Telegram_Bot.git
    cd Gemini_Telegram_Bot
    ```

3. **Create a Branch**

    ```bash
    git checkout -b feature-branch
    ```

4. **Make Your Changes**

5. **Commit and Push**

    ```bash
    git add .
    git commit -m "Add some feature"
    git push origin feature-branch
    ```

6. **Submit a Pull Request**

    Go to the original repository and create a pull request from your fork.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Contact

For any questions or suggestions, please open an issue or contact the repository owner.

---

Thank you for using Gemini Telegram Bot! 😊
