# Viral Analysis Workflow v1

## Inputs

- `video_url`: string

## HTTP Processing

1. Call video service endpoint: `POST /api/v1/video/process`
2. Request body:

```json
{
  "video_url": "{{video_url}}"
}
```

3. Expected response fields:
   - `transcript`
   - `segments`
   - `scenes`
   - `keyframes`
   - `duration_seconds`

## Prompt Assembly

- Template: `dify/prompts/viral-analysis-v1.md`
- Variables:
  - `transcript`: response transcript
  - `scenes`: response scenes JSON

## Generation

- Model provider: DeepSeek via Dify model provider settings
- Suggested model: `deepseek-chat`
- Temperature: `0.3`
- Max tokens: `4096`

## Validation

The generated output must satisfy all of the following:

1. Valid JSON object
2. Includes `structure.hook`, `structure.content`, `structure.value_add`, `structure.cta`
3. Includes `overall_analysis`
4. Includes `applicable_patterns` array with at least 2 entries

## Publishing

Publish as Workflow App, then expose via Dify Workflow API `/workflows/run`
