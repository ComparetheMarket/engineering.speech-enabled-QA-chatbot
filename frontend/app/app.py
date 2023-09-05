import gradio as gr
import numpy as np
import pandas as pd
import time
import os
import yaml
import json
import requests
import librosa
from ast import literal_eval


from dotenv import load_dotenv
from utils import databricks_qa_chain, query_transcription_endpoint

load_dotenv()

DATABRICKS_URL = os.environ["DATABRICKS_URL"]
DATABRICKS_TOKEN = os.environ["DATABRICKS_TOKEN"]
TRANSCIPTION_MODEL = os.environ["TRANSCRIPTION_MODEL_NAME"]

qa_chain = databricks_qa_chain(
    databricks_host=DATABRICKS_URL, token=DATABRICKS_TOKEN, args="production"
)


def transcribe_audio(audio, history):
    sampling_rate = audio[0]
    if sampling_rate != 16000:
        audio_resampled = (
            librosa.resample(
                audio[1].astype(np.float32), orig_sr=sampling_rate, target_sr=16000
            )
            / 2**15
        ).astype(int)
    dataset = pd.DataFrame({"audio": audio_resampled, "sampling_rate": 16000})
    transcribed = query_transcription_endpoint(
        dataset=dataset,
        url=DATABRICKS_URL,
        databricks_token=DATABRICKS_TOKEN,
        transciption_model=TRANSCIPTION_MODEL,
    )
    print("transcribed:", transcribed)
    history += [(transcribed, None)]
    print(history)
    return history


def get_llm_response(history):
    # history[-1][1] = ""
    print(history)
    response = qa_chain.request_llm_response(history[-1][0])
    print("response:", response)
    print("response:", literal_eval(response)["answer"])
    history[-1][1] = literal_eval(response)["answer"]
    return history, literal_eval(response)["revelant_context"]


with gr.Blocks() as demo:
    with gr.Row():
        gr.Markdown(
            f"""
             # Ask me anything about your Car Insurance Policy. 
             ### I am powered by Llama2 and Whisper.
            """
        )
    with gr.Row():
        with gr.Column():
            chatbot = gr.Chatbot(
                avatar_images=("image/user.jpg", "image/databricks_logo.png")
            )
            audio = gr.Audio(source="microphone", type="numpy", format="mp3")
            clear = gr.ClearButton([audio, chatbot])

        with gr.Column():
            raw_text = gr.Textbox(
                label="Document from which the answer was generated", scale=50
            )

    audio_submit = (
        audio.stop_recording(transcribe_audio, [audio, chatbot], chatbot)
        .then(get_llm_response, chatbot, [chatbot, raw_text])
        .then(lambda: None, None, audio)
    )


if __name__ == "__main__":
    demo.queue()
    demo.launch(server_name="127.0.0.1", server_port=7000)
