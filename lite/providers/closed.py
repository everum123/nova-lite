from . import _utils

ENDPOINT = 'https://api.openai.com'

async def patch_request(request: dict) -> dict:
    key = await _utils.random_secret_for('closed')

    request['url'] = ENDPOINT + request['path']
    request['headers']['Authorization'] = f'Bearer {key}'

    return request
