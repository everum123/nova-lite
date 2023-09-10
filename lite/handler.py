import aiohttp
import fastapi

from providers import closed

router = fastapi.APIRouter()

async def client_request(request: dict) -> dict:
    """Make a request to the target API."""

    #? Start the request
    async with aiohttp.ClientSession() as session:
        async with session.request(
            method=request.get('method', 'POST'),
            url=request['url'],
            data=request.get('data'),
            json=request.get('payload'),
            headers=request.get('headers', {}),
            cookies=request.get('cookies'),
            timeout=aiohttp.ClientTimeout(connect=5, total=500.0)
        ) as response:
            #? Raise an exception if the response has an error
            response.raise_for_status()

            #? Send the response back to the client
            async for response_chunk in response.content.iter_any():
                yield response_chunk

@router.route('/v1/{path:path}', methods=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS'])
async def handle(request: fastapi.Request):
    """Handle a request to the proxy."""

    path = request.url.path.replace('/v1/v1', '/v1') # fix double v1

    #? Try to parse the payload as JSON
    try:
        payload = await request.json()
    except:
        payload = {}

    #? Build the request
    request = {
        'path': path,
        'method': request.method,
        'payload': payload,
        'headers': {
            'Content-Type': 'application/json'
        }
    }

    #? Apply the proxy provider by patching the request
    request = await closed.patch_request(request)

    #? Send the request to the target API
    return fastapi.responses.StreamingResponse(client_request(request))
