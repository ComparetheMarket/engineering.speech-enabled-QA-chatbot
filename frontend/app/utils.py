from databricks.sdk import WorkspaceClient
from databricks.sdk.service import jobs,compute
import yaml
import requests
import json
from time import time



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

        run_name = job_details['resources']['jobs']['deploy_llm']['name'].replace("${bundle.environment}",self.args)
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