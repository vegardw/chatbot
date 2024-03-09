Personal LLM experimentation. Licensed under the MIT license if anyone else would like to use it for something.

# Configuration File (config.json)

The `config.json` file is used to configure the chatbot application. It contains various settings and model configurations.

## Fields

- `mistral_api_key` (string): The API key for the Mistral service. Replace `"INSERT_YOUR_MISTRAL_API_KEY"` with your actual API key.

- `anthropic_api_key` (string): The API key for the Anthropic service. Replace `"INSERT_YOUR_ANTHROPIC_API_KEY"` with your actual API key.

- `model_path` (string): The path where the local llama.cpp/GGUF models are stored.

- `default_model` (string): The default model to use for the chatbot.

- `models` (array): An array of model configurations. Each model configuration is an object with the following fields:
  - `type` (string): The type of the model. Possible values are `"HfTransformers"`, `"AnthropicClaude"`, and `"LlamaCpp"`.
  - `args` (object): Model-specific arguments. The available arguments depend on the model type.

- `system_prompts` (array): An array of system prompts. Each prompt is a string that defines the behavior or personality of the chatbot. Default value is `["You are a helpful assistant."]`.

## Model Types and Arguments

### HfTransformers
This model type uses the HuggingFace Transformers library for running local models from the HuggingFace Hub

- `models` (array): An array of model names to use with the HfTransformers model.
- `hf_repo` (string): The Hugging Face repository name for the model.
- `streaming` (boolean): Indicates whether to use streaming mode for generating responses. Optional, default value is `true`.

### AnthropicClaude
This model type uses the Antropic Claude API, you need an API key to use this option.

- `models` (array): An array of model names to use with the AnthropicClaude model.
- `streaming` (boolean): Indicates whether to use streaming mode for generating responses.  Optional, default value is `true`.

### LlamaCpp
This model type uses the llama-cpp-python library for running local models, optionally downloading them from the HF Hub.

- `models` (array): An array of model names to use with the LlamaCpp model.
- `hf_repo` (string): The Hugging Face repository name for the model. Optional, if no present, the model is loaded from the local path `model_path`
- `chat_format` (string): The chat format to use. See the llama-cpp-python document for possible vaules. Default vaule is `llama-2`
- `n_gpu_layers` (integer): The number of GPU layers to use. The value `-1` which means using all available GPU layers. Default is `0`, meaning the CPU is used for all layers
- `n_context` (integer): The number of context tokens to use. Default value is `512`.

## Example Configuration

Here's an example `config.json` file:

```json
{
  "mistral_api_key": "INSERT_YOUR_MISTRAL_API_KEY",
  "anthropic_api_key": "INSERT_YOUR_ANTHROPIC_API_KEY",
  "model_path": "./files/models",
  "default_model": "stablelm-zephyr-3b.Q5_K_S",
  "models": [
    {
      "type": "HfTransformers",
      "args": {
        "models": [
          "phi2-super"
        ],
        "hf_repo": "abacaj/phi-2-super",
        "streaming": true
      }
    },
    {
      "type": "AnthropicClaude",
      "args": {
        "models": [
          "claude-3-opus-20240229"
        ],
        "streaming": false
      }
    },
    {
      "type": "LlamaCpp",
      "args": {
        "models": [
          "stablelm-zephyr-3b.Q5_K_S"
        ],
        "hf_repo": "TheBloke/stablelm-zephyr-3b-GGUF",
        "chat_format": "zephyr",
        "n_gpu_layers": -1
      }
    },
    {
      "type": "LlamaCpp",
      "args": {
        "models": [
          "starling-lm-7b-alpha.Q5_K_S"
        ],
        "hf_repo": "TheBloke/Starling-LM-7B-alpha-GGUF",
        "chat_format": "openchat",
        "n_gpu_layers": 32,
        "n_context": 8192
      }
    }
  ],
  "system_prompts": [
    "You are a helpful assistant."
  ]
}
```

Make sure to update the `config.json` file with your actual API keys and desired configurations before running the chatbot application.
