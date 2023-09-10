import os
import fastapi
import aiohttp

from dotenv import load_dotenv

load_dotenv()
app = fastapi.FastAPI()

async def client_request(request: dict) -> dict:
    """Make a request to the target API."""

    #? Start the request
    async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(connect=5, total=500.0)) as session:
        async with session.request(
            method=request.get('method', 'POST'),
            url=request['url'],
            json=request.get('payload'),
            headers=request.get('headers', {})
        ) as response:
            response.raise_for_status()

            async for response_chunk in response.content.iter_any():
                yield response_chunk

@app.route('/v1/{path:path}', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
async def handle(request: fastapi.Request):
    path = request.url.path.replace('/v1/v1', '/v1') # fix double v1

    try: payload = await request.json()
    except: payload = {}

    request = {
        'path': path,
        'method': request.method,
        'payload': payload,
        'headers': {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + os.environ['OPENAI_API_KEY']
        },
        'url': 'https://api.openai.com' + path
    }

    return fastapi.responses.StreamingResponse(client_request(request))

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=4242)
