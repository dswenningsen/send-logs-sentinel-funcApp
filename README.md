# Send Logs to Sentinel Function App

An Azure Functions application that provides an HTTP endpoint for receiving log data and forwarding it to Azure Monitor using Data Collection Rules (DCR). This is commonly used for sending custom logs to Azure Sentinel for security monitoring and analysis.

## Overview

This Azure Function app exposes a REST API endpoint that:
- Accepts log data via HTTP POST requests
- Validates and processes the incoming data
- Forwards logs to Azure Monitor using Data Collection Rules
- Provides error handling and logging for troubleshooting

## Prerequisites

- Python 3.6 or higher
- Azure Functions Core Tools
- Azure CLI (for deployment)
- An Azure subscription with:
  - Log Analytics Workspace
    - Table with appropriate schema
  - Data Collection Endpoint (DCE)
  - Data Collection Rule (DCR)
  - Appropriate Azure permissions for the Function App identity

## Installation

### Local Development

1. Clone the repository:
   ```bash
   git clone https://github.com/dswenningsen/send-logs-sentinel-funcApp.git
   cd send-logs-sentinel-funcApp
   ```

2. Create and activate a Python virtual environment:
   ```bash
   python -m venv .venv
   
   # On Windows
   .venv\Scripts\activate
   
   # On Linux/Mac
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

### Environment Variables

The following environment variables must be configured:

| Variable | Description | Example |
|----------|-------------|---------|
| `DCE_INGESTION_URL` | Data Collection Endpoint ingestion URL | `https://your-dce.eastus-1.ingest.monitor.azure.com` |
| `DCR_ID` | Data Collection Rule immutable ID | `dcr-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` |
| `TABLE_NAME` | Target table name in your Log Analytics workspace | `CustomLogs_CL` |

### Local Development Configuration

Update `local.settings.json` with your configuration:

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "DCE_INGESTION_URL": "https://your-dce.eastus-1.ingest.monitor.azure.com",
    "DCR_ID": "dcr-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
    "TABLE_NAME": "CustomLogs_CL"
  }
}
```

### Azure Function App Configuration

In the Azure portal, add the environment variables as Application Settings for your Function App.

## Usage

### Running Locally

1. Start the Azure Functions runtime:
   ```bash
   func start
   ```

2. The function will be available at:
   ```
   http://localhost:7071/api/send_logs
   ```

### API Endpoint

**Endpoint:** `POST /api/send_logs`

**Content-Type:** `application/json`

#### Request Body

The endpoint accepts either a single log object or an array of log objects (Schema depends on DCR and Table):

**Single Log:**
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "INFO",
  "message": "User login successful",
  "user_id": "user123",
  "source_ip": "192.168.1.100"
}
```

**Multiple Logs:**
```json
[
  {
    "timestamp": "2024-01-15T10:30:00Z",
    "level": "INFO",
    "message": "User login successful",
    "user_id": "user123"
  },
  {
    "timestamp": "2024-01-15T10:31:00Z",
    "level": "WARNING",
    "message": "Failed login attempt",
    "user_id": "user456"
  }
]
```

#### Response

**Success (200 OK):**
```json
{
  "message": "Data successfully sent to DCR",
  "records_sent": 2
}
```

**Error (400 Bad Request):**
```json
{
  "error": "Request body is required"
}
```

**Error (500 Internal Server Error):**
```json
{
  "error": "Missing required environment variables: DCE_INGESTION_URL, DCR_ID, or TABLE_NAME"
}
```

### Example Usage with curl (Schema depends on DCR and Table)

```bash
curl -X POST http://localhost:7071/api/send_logs \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2024-01-15T10:30:00Z",
    "level": "INFO",
    "message": "Test log message",
    "application": "my-app"
  }'
```

## Deployment

### Deploy to Azure

1. Login to Azure:
   ```bash
   az login
   ```

2. Create a Function App (if not already created):
   ```bash
   az functionapp create \
     --resource-group myResourceGroup \
     --consumption-plan-location eastus \
     --runtime python \
     --runtime-version 3.9 \
     --functions-version 4 \
     --name myFunctionApp \
     --storage-account mystorageaccount
   ```

3. Deploy the function:
   ```bash
   func azure functionapp publish myFunctionApp
   ```

4. Configure the application settings:
   ```bash
   az functionapp config appsettings set \
     --name myFunctionApp \
     --resource-group myResourceGroup \
     --settings \
     DCE_INGESTION_URL="https://your-dce.eastus-1.ingest.monitor.azure.com" \
     DCR_ID="dcr-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" \
     TABLE_NAME="CustomLogs_CL"
   ```

### Authentication

The function uses `DefaultAzureCredential` for authentication with Azure Monitor. Ensure your Function App has the appropriate permissions:

1. **System-assigned Managed Identity**: Enable in the Function App settings
2. **Required Role**: `Monitoring Metrics Publisher` role on the Data Collection Rule
3. **Scope**: The specific Data Collection Rule resource

## Architecture

```
Client Application
       ↓ HTTP POST
Azure Function (send_logs)
       ↓ Azure Monitor Ingestion API  
Data Collection Rule
       ↓
Log Analytics Workspace
       ↓
Azure Sentinel
```

## Development

### Project Structure

```
├── function_app.py          # Main function code
├── requirements.txt         # Python dependencies
├── host.json               # Azure Functions host configuration
├── local.settings.json     # Local development settings
└── README.md              # This file
```

### Dependencies

- `azure-functions`: Azure Functions Python SDK
- `azure-monitor-ingestion`: Azure Monitor data ingestion client
- `azure-identity`: Azure authentication library

## Troubleshooting

### Common Issues

1. **Authentication Errors**: Ensure the Function App's managed identity has the correct permissions
2. **Missing Environment Variables**: Verify all required environment variables are set
3. **Invalid JSON**: Ensure the request body contains valid JSON
4. **DCR Configuration**: Verify the Data Collection Rule is properly configured and the table schema matches your log data

### Monitoring

- Check Function App logs in the Azure portal
- Use Application Insights for detailed telemetry
- Monitor the Log Analytics workspace for incoming data

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions:
1. Check the [Issues](https://github.com/dswenningsen/send-logs-sentinel-funcApp/issues) page
2. Create a new issue with detailed information about the problem
3. Include relevant error messages and configuration details