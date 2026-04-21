curl -X POST "http://localhost:5001/v1/workflows/run" \
  -H "Authorization: Bearer YOUR_DIFY_APP_API_KEY" \
  -H "Content-Type: application/json" \
  -d @workflow-api-example.json
