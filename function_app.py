"""
Function App to receive HTTP requests and send logs to Azure Monitor Data
Collection Rules (DCR)
"""

import os
import json
import logging
import azure.functions as func
from azure.monitor.ingestion import LogsIngestionClient
from azure.identity import DefaultAzureCredential

app = func.FunctionApp()


@app.route(route="send_logs", methods=["POST"])
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    try:
        # Get the request body
        req_body = req.get_json()

        if not req_body:
            return func.HttpResponse(
                "Request body is required", status_code=400
            )

        # Ensure data is in array format for DCR
        if isinstance(req_body, list):
            data = req_body
        else:
            data = [req_body]

        # Get DCR configuration from environment variables
        endpoint = os.getenv("DCE_INGESTION_URL")
        rule_id = os.getenv("DCR_ID")
        table_name = os.getenv("TABLE_NAME")

        if not all([endpoint, rule_id, table_name]):
            return func.HttpResponse(
                "Missing required environment variables: DCE_INGESTION_URL, DCR_ID, or TABLE_NAME",
                status_code=500,
            )

        # Send data to DCR
        credential = DefaultAzureCredential()
        client = LogsIngestionClient(endpoint, credential)
        client.upload(rule_id, table_name, data)

        logging.info(f"Successfully sent {len(data)} records to DCR")

        return func.HttpResponse(
            json.dumps(
                {
                    "message": "Data successfully sent to DCR",
                    "records_sent": len(data),
                }
            ),
            status_code=200,
            mimetype="application/json",
        )

    except ValueError as e:
        logging.error(f"Invalid JSON in request body: {e}")
        return func.HttpResponse(
            "Invalid JSON in request body", status_code=400
        )
    except Exception as e:
        logging.error(f"Error sending data to DCR: {e}")
        return func.HttpResponse(
            f"Error sending data to DCR: {str(e)}", status_code=500
        )
