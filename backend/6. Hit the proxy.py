# Databricks notebook source
import requests
import json

def request_llamav2_13b(question):
    token = "dapi718b65c1eb708cef36f9b09ee552f9bf"
    url = 'https://adb-984752964297111.11.azuredatabricks.net/driver-proxy-api/o/0/0728-153932-k08t5wf6/7777'
    
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

request_llamav2_13b("What initiatives did Unilever take to reduce its environmental impact in 2020 according to the 2020 Annual Report")

# COMMAND ----------

# DBTITLE 1,To hit it from within the cluster
# from langchain.llms import Databricks
# respond = Databricks(cluster_driver_port="7777")

# respond("What is Unilever's revenue for 2021?")

# COMMAND ----------


