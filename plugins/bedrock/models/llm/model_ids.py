"""
Bedrock model IDs configuration file.
This file maintains the mapping between model names and their corresponding Bedrock model IDs.
Based on AWS documentation: 
- https://docs.aws.amazon.com/bedrock/latest/userguide/models-supported.html
- https://docs.aws.amazon.com/bedrock/latest/userguide/models-regions.html
"""

BEDROCK_MODEL_IDS = {
    'anthropic claude': {
        'US Claude 3.7 Sonnet': 'us.anthropic.claude-3-7-sonnet-20250219-v1:0',
        'EU Claude 3.7 Sonnet': 'eu.anthropic.claude-3-7-sonnet-20250219-v1:0',
        'Claude 3.5 Sonnet': 'anthropic.claude-3-5-sonnet-20240620-v1:0',
        'Claude 3.5 Sonnet V2': 'anthropic.claude-3-5-sonnet-20241022-v2:0',
        'US Claude 3.5 Sonnet': 'us.anthropic.claude-3-5-sonnet-20240620-v1:0',
        'US Claude 3.5 Sonnet V2': 'us.anthropic.claude-3-5-sonnet-20241022-v2:0',
        'EU Claude 3.5 Sonnet': 'eu.anthropic.claude-3-5-sonnet-20240620-v1:0',
        'Claude 3.5 Haiku': 'anthropic.claude-3-5-haiku-20241022-v1:0',
        'US Claude 3.5 Haiku': 'us.anthropic.claude-3-5-haiku-20241022-v1:0',
        'Claude 3 Sonnet': 'anthropic.claude-3-sonnet-20240229-v1:0',
        'US Claude 3 Sonnet': 'us.anthropic.claude-3-sonnet-20240229-v1:0',
        'Claude 3 Haiku': 'anthropic.claude-3-haiku-20240307-v1:0',
        'US Claude 3 Haiku': 'us.anthropic.claude-3-haiku-20240307-v1:0',
        'Claude 3 Opus': 'anthropic.claude-3-opus-20240229-v1:0',
        'US Claude 3 Opus': 'us.anthropic.claude-3-opus-20240229-v1:0',
    },
    'amazon nova': {
        'Nova Pro': 'amazon.nova-pro-v1:0',
        'US Nova Pro': 'us.amazon.nova-pro-v1:0',
        'EU Nova Pro': 'eu.amazon.nova-pro-v1:0',
        'Nova Lite': 'amazon.nova-lite-v1:0',
        'US Nova Lite': 'us.amazon.nova-lite-v1:0',
        'EU Nova Lite': 'eu.amazon.nova-lite-v1:0',
        'Nova Micro': 'amazon.nova-micro-v1:0',
        'US Nova Micro': 'us.amazon.nova-micro-v1:0',
        'EU Nova Micro': 'eu.amazon.nova-micro-v1:0'
    },
    'meta': {
        'Llama 3 8B Instruct': 'meta.llama3-8b-instruct-v1:0',
        'Llama 3 70B Instruct': 'meta.llama3-70b-instruct-v1:0',
        'Llama 3.1 8B Instruct': 'meta.llama3-1-8b-instruct-v1:0',
        'US Llama 3.1 8B Instruct': 'us.meta.llama3-1-8b-instruct-v1:0',
        'Llama 3.1 70B Instruct': 'meta.llama3-1-70b-instruct-v1:0',
        'US Llama 3.1 70B Instruct': 'us.meta.llama3-1-70b-instruct-v1:0',
        'Llama 3.1 405B Instruct': 'meta.llama3-1-405b-instruct-v1:0',
        'US Llama 3.1 405B Instruct': 'us.meta.llama3-1-405b-instruct-v1:0',
        'US Llama 3.2 11B Instruct': 'us.meta.llama3-2-11b-instruct-v1:0',
        'US Llama 3.2 90B Instruct': 'us.meta.llama3-2-90b-instruct-v1:0'
    },
    'mistral': {
        'Mistral 7B Instruct': 'mistral.mistral-7b-instruct-v0:2',
        'Mistral Large': 'mistral.mistral-large-2402-v1:0',
        'Mistral Small': 'mistral.mistral-small-2402-v1:0',
        'Mixtral 8x7B Instruct': 'mistral.mixtral-8x7b-instruct-v0:1'
    },
    'ai21': {
        'Jamba 1.5 Mini': 'ai21.jamba-1-5-mini-v1:0',
        'Jamba 1.5 Large': 'ai21.jamba-1-5-large-v1:0'
    },
    'deepseek': {
        'DeepSeek-R1': 'us.deepseek.r1-v1:0'
    }
}

def get_model_id(model_type, model_name):
    """
    Get the Bedrock model ID for the specified model type and name.
    
    Args:
        model_type (str): The type of model (e.g., 'claude', 'amazon nova')
        model_name (str): The name of the model (e.g., 'Claude 3 Opus')
        
    Returns:
        str: The corresponding Bedrock model ID, or None if not found
    """
    return BEDROCK_MODEL_IDS.get(model_type, {}).get(model_name)

def get_first_model(model_type):
    """
    Get the Bedrock model ID for the specified model type and name.
    
    Args:
        model_type (str): The type of model (e.g., 'claude', 'amazon nova')
        model_name (str): The name of the model (e.g., 'Claude 3 Opus')
        
    Returns:
        str: The corresponding Bedrock model ID, or None if not found
    """
    models = BEDROCK_MODEL_IDS.get(model_type, {})
    return next(iter(models.values()))
