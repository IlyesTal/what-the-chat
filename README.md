# What The Chat

What The Chat is an open-source project that connects the OpenAI's ChatGPT API with WhatsApp, using Twilio. It allows users to interact with ChatGPT through their WhatsApp app, providing a seamless experience. Users can send text messages and audio messages to ChatGPT and receive responses directly in their WhatsApp chat.

## Features

Free and premium subscription options.
- Text and audio messaging support.
- Image generation support for premium users.
- Daily usage limit for free users.

## Getting Started

### Prerequisites

- Python 3.6 or later.
- A Twilio account with a WhatsApp enabled phone number.
- An OpenAI API key.

### Installation

- Clone the repository.

<pre><code>git clone https://github.com/your_username/what-the-chat.git</code></pre>

- Install the required dependencies.

<pre><code>pip install -r requirements.txt</code></pre>

- Set up environment variables in the .env file
- Run the Flask application.

<pre><code>python app.py</code></pre>

### Usage

- Add the Twilio WhatsApp number to your contacts.
- Start a chat with the Twilio WhatsApp number.
- Send messages or audio messages to interact with ChatGPT.
- Premium users can generate images by sending a message starting with /image.

If you want to propose your ChatGPT based model as a service on Whatsapp you can connect it to Stripe.

## Files

- app.py: The main Flask application file
- openai_request.py: Handles OpenAI API requests for chat, audio transcription, and image generation
- .env: Your Twilio and OpenAI API credentials
- requirements.txt: The required Python packages for the project

## To-Do

- Database connexion (I used PostgresSQL)
- Stripe connexion

## License
This project is open-source and available under the MIT License

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## Contact

If you have any questions or suggestions, feel free to reach out at hello@what-the-chat.com.
