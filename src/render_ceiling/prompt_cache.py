import copy

MODEL_PRICING = {
    'claude-sonnet-5-5': {'input': 2.0, 'output': 10.0, 'write_5m': 2.5, 'read': 0.1, 'minimum_tokens': 512},
    'claude-opus-5-5': {'input': 4.0, 'output': 20.0, 'write_5m': 5.0, 'read': 0.2, 'minimum_tokens': 512},
    'claude-fable-5-1': {'input': 10.0, 'output': 50.0, 'write_5m': 12.5, 'read': 0.25, 'minimum_tokens': 512},
}


def with_cache(payload, input_tokens, remaining_repeats):
    result = copy.deepcopy(payload)
    enabled = input_tokens >= MODEL_PRICING[payload['model']]['minimum_tokens'] and remaining_repeats >= 2
    if enabled:
        result['messages'][-1]['content'][-1]['cache_control'] = {'type': 'ephemeral', 'ttl': '5m'}
    return result, enabled


def token_cost(model, usage):
    rates = MODEL_PRICING[model]
    return (usage.get('input_tokens', 0)*rates['input'] + usage.get('output_tokens', 0)*rates['output'] + usage.get('cache_creation_input_tokens', 0)*rates['write_5m'] + usage.get('cache_read_input_tokens', 0)*rates['read'])/1e6
