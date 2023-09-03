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
from utils import databricks_qa_chain

load_dotenv()

DATABRICKS_URL = os.environ["DATABRICKS_URL"]
DATABRICKS_TOKEN = os.environ["DATABRICKS_TOKEN"]

qa_chain = databricks_qa_chain(databricks_host=DATABRICKS_URL,
                               token=DATABRICKS_TOKEN,
                               args = 'production')

    


# qa_chain.request_llm_response("what is the limit for misfuelling cost?")

def query_transcription_endpoint(
    dataset, url=DATABRICKS_URL, databricks_token=DATABRICKS_TOKEN
):
    url = f"{url}/serving-endpoints/whisper-small/invocations"
    headers = {
        "Authorization": f"Bearer {databricks_token}",
        "Content-Type": "application/json",
    }
    ds_dict = {"dataframe_split": dataset.to_dict(orient="split")}
    data_json = json.dumps(ds_dict, allow_nan=True)
    response = requests.request(method="POST", headers=headers, url=url, data=data_json)
    if response.status_code != 200:
        raise Exception(
            f"Request failed with status {response.status_code}, {response.text}"
        )

    return response.json()["predictions"][0]


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
    time.sleep(5)
    # transcribed = query_transcription_endpoint(dataset)
    # print("transcribed")
    history +=  [("what is the cost of misfuelling?",None)]
    print(history)
    return history
    # info = qabot.get_answer(question)
    # chat_history.append((question,info['answer']))
    # return "", chat_history , info['vector_doc'], info['source']

def get_llm_response(history):

    # history[-1][1] = ""
    print(history)
    response = qa_chain.request_llm_response(history[-1][0])
    print("response:",literal_eval(response)['answer'])
    history[-1][1] = literal_eval(response)['answer']
    return history,literal_eval(response)['revelant_context']

# def clear_output(clear):



with gr.Blocks() as demo:
    with gr.Row():
        gr.Markdown(
            f"""
             # # Policy Retrieval QA using "aaaaa"
        # The current version FAISS vector store to Fetch the most relevant paragraph's to create the bot
        # """
        )
        # f"""
        # # Policy Retrieval QA using {config['model_id']}
        # The current version FAISS vector store to Fetch the most relevant paragraph's to create the bot
        # """)
    with gr.Row():
        with gr.Column():
            chatbot = gr.Chatbot(avatar_images=("image/user.jpg","image/databricks_logo.png" ))
            audio = gr.Audio(source="microphone", type="numpy", format="mp3")
            clear = gr.ClearButton([audio, chatbot])

        with gr.Column():
            raw_text = gr.Textbox(label="Document from which the answer was generated",scale=50)
            raw_source = gr.Textbox(label="Source of the Document",scale=1)
    # with gr.Row():
    #   examples = gr.Examples(examples=["what is limit of the misfueling cost covered in the policy?", "what happens if I lose my keys?","what is the duration for the policy bought by the policy holder mentioned in the policy schedule / Validation schedule","What is the maximum Age of a Vehicle the insurance covers?"],
    #                     inputs=[msg])
    # msg.submit(respond, [msg, chatbot], [msg, chatbot,raw_text,raw_source])
    # submit.click(respond, [audio, chatbot], [audio, chatbot])
    audio_submit = audio.stop_recording(transcribe_audio, [audio, chatbot], chatbot).then(
        get_llm_response, chatbot, [chatbot,raw_source]).then(lambda :None, None, audio)


if __name__ == "__main__":
    demo.queue()
    demo.launch(
        server_name="127.0.0.1",
        server_port=7000
    )
