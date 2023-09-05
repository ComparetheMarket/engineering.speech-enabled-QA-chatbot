from databricks.sdk import WorkspaceClient
from databricks.sdk.service import jobs,compute
import yaml
import requests
import json
from time import time


def query_transcription_endpoint(
    dataset,
    url,
    databricks_token,
    transciption_model
    ):
    url = f"{url}/serving-endpoints/{transciption_model}/invocations"

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

class databricks_qa_chain:
    def __init__(self,token,databricks_host,args):
        self.token = token
        self.databricks_host = databricks_host
        self.args = args
        self.cluster_id = self.get_cluster_id()
        self.url = self.create_proxy_url()

    def request_llm_response(self,
                            question):
        
        headers = {
            "Content-Type": "application/json",
            "Authentication": f"Bearer {self.token}"
            }
        
        data = {
        "prompt": question
        }
        
        response = requests.post(self.url, headers=headers, data=json.dumps(data))
        return response.text

    def get_cluster_id(self):
        '''
        Get the cluster ID of the running jobs
        '''

        w = WorkspaceClient(host =self.databricks_host,
                            token = self.token )

        job_list = w.jobs.list_runs(active_only=True)


        with open("../../backend/databricks_resources/llm-model-workflow.yml", "r") as stream:
            try:
                job_details  = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        run_name = job_details['resources']['jobs']['deploy_llm']['name'].replace("${bundle.environment}",
                                                                                  self.args).\
                                                        replace("${workspace.current_user.userName}",
                                                                w.current_user.me().user_name)
        print(run_name)
        for job in job_list:
            if job.run_name == run_name:
                break
        print(job)
        cluster_name  = "job-" + str(job.job_id)+"-run-"+ \
                        str(job.run_id)+ "-" + \
                        w.jobs.get(job.job_id).settings.job_clusters[0].job_cluster_key
        all = w.clusters.list(can_use_client ='JOBS')
        for cluster in all:
            if cluster.cluster_name == cluster_name:
                break
        return cluster.cluster_id
    
    def create_proxy_url(self):
        return f"{self.databricks_host}/driver-proxy-api/o/0/{self.cluster_id}/7777"