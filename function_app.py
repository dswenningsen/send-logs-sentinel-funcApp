import logging
import azure.functions as func
from azure.monitor.ingestion import LogsIngestionClient
from azure.identity import DefaultAzureCredential
import os

app = func.FunctionApp()


@app.timer_trigger(
    schedule="0 */5 * * * *",
    arg_name="myTimer",
    run_on_startup=False,
    use_monitor=False,
)
def timer_trigger(myTimer: func.TimerRequest) -> None:
    if myTimer.past_due:
        logging.info("The timer is past due!")

    logging.info("Python timer trigger function executed.")
    endpoint = os.getenv("DCE_INGESTION_URL")
    rule_id = os.getenv("DCR_ID")
    table_name = os.getenv("TABLE_NAME")
    credential = DefaultAzureCredential()
    client = LogsIngestionClient(endpoint, credential)
    data = [{"msg": "Hello, World!"}]
    client.upload(rule_id, table_name, data)
