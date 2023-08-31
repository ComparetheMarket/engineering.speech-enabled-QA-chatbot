# Databricks notebook source
import requests
import json

def request_llamav2_13b(question):
    token = "<xxxxxx>"
    url = '<xxxxxxx>'
    
    headers = {
        "Content-Type": "application/json",
        "Authentication": f"Bearer {token}"
        }
    
    data = {
     "prompt": question
     }
    
    response = requests.post(url, headers=headers, data=json.dumps(data))
    return response.text




# COMMAND ----------

request_llamav2_13b("what is the limit for misfuelling cost?")

# COMMAND ----------

# DBTITLE 1,To hit it from within the cluster
# from langchain.llms import Databricks
# respond = Databricks(cluster_driver_port="7777")

# respond("What is Unilever's revenue for 2021?")

# COMMAND ----------


