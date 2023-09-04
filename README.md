# speech-enabled-QA-chatbot
A Q&A chatbot with ability to recognise speech 

## Requirements

1. Create a .env file in the app folder and add the following parameters:
```
DATABRICKS_TOKEN=<your-databricks-token>
DATABRICKS_URL=<your_databricks_url>
```
You can create a token in *User settings* withing the Databricks workspace your model is served in.

2. Install the following using brew (on MacOS) or alternative on other operating systems:
```
brew install ffmpeg
```

3. Install python requirements:
```
pip install -r requirements.txt
```
## Run the app

```
python app/app.py
```
