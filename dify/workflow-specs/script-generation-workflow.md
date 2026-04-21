# Script Generation Workflow v1

## Inputs

- `product_name`: string
- `special_instructions`: string | optional
- `viral_reference`: string | optional

## Retrieval

1. Query product dataset by `product_name`
2. Query historical scripts dataset by semantic similarity to `product_name`
3. Optionally load viral analysis JSON when `viral_reference` is present

## Prompt Assembly

- Template: `dify/prompts/script-generation-v1.md`
- Variables:
  - `context`: retrieved historical scripts
  - `product_info`: retrieved product metadata
  - `viral_reference`: optional viral analysis JSON
  - `special_instructions`: optional user instruction

## Generation

- Model provider: DeepSeek via Dify model provider settings
- Suggested model: `deepseek-chat`
- Temperature: `0.7`
- Max tokens: `4096`

## Validation

The generated output must satisfy all of the following:

1. Exactly four sections
2. Each section contains both `[画面]` and `[口播]`
3. No unsupported product facts
4. Target duration between 30 and 60 seconds

## Publishing

Publish as Workflow App, then expose via Dify Workflow API `/workflows/run`
