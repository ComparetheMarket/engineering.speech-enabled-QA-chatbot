# Define the profile before calling create-llm-job e.g make profile=aws-dogfood create-llm-job
create-llm-job:
	databricks bundle deploy --profile=$(profile)

launch-llm-job:
	databricks bundle deploy --profile=$(profile)
	databricks bundle run deploy_llm  --profile=$(profile) --no-wait

launch-ui:
	cd frontend/app && python app.py