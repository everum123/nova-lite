import os
import time
import fastapi # For the API

from slowapi import Limiter # For rate limiting (anti-spam)
from fastapi.middleware.cors import CORSMiddleware # For CORS

from dotenv import load_dotenv # For loading environment variables from the .env file

import handler

load_dotenv() # Loads the .env file, which makes the environment variables accessible via os.getenv() or os.environ
app = fastapi.FastAPI()

#? Makes it so that websites can directly access the API using JavaScript which runs on the client side (in the browser).
#? If this was turned off, then custom front-ends like Better ChatGPT, Chatbot UI ChatGPT Next Web etc. would not be able to access the API.
#! If you're using Cloudflare, you might also need to enable CORS there as well!
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

#? The actual core of the API. This is where the magic happens.
#? This is in a separate file to make it easier to maintain.
app.include_router(handler.router)

def get_ip_from_request(request: fastapi.Request) -> str:
    """Get the IP address of the incoming request.
    The reason this function is so complicated is because of proxies like Cloudflare that add the IP address of the user to the headers of the request.

    If you're not using any sort of reverse proxy, you can just use

    return request.client.host

    instead.
    """

    #? Some proxies (like Cloudflare) will add the IP address of the user to the headers of the request.
    xff = None
    if request.headers.get('x-forwarded-for'):
        xff, *_ = request.headers['x-forwarded-for'].split(', ')

    #? The IP address of the user can be in one of three places:
    possible_ips = [
        xff,
        request.headers.get('cf-connecting-ip'),
        request.client.host
    ]

    #? The IP address of the user is the first one that is not None.
    detected_ip = next((i for i in possible_ips if i), None)

    #? Whitelist IPs that should not be rate limited
    #* You can whitelist IPs by adding them to the NO_RATELIMIT_IPS environment variable, separated by a space.
    #* You don't even have to add your entire IP address, you can just add the first few blocks, and these will be whitelisted then.
    for whitelisted_ip in os.getenv('NO_RATELIMIT_IPS', '').split():
        if whitelisted_ip in detected_ip:
            custom_key = f'whitelisted-{time.time()}'
            return custom_key

    return detected_ip

#? Rate limiting is used to prevent spam of the API.
#? key_func tells the Limiter how to identify the user. In this case, it uses the IP address of the user.
#* If you're using Cloudflare, you probably might also want to enable rate limiting there as well!
limiter = Limiter(swallow_errors=True, key_func=get_ip_from_request, default_limits=['2/second', '20/minute', '300/hour'])

#? This is the main route of the API. Just shows some basic information about the API.
#? You could also make a simple HTML page and return that instead.
@app.get('/')
async def index():
    return {
        'hi': 'Welcome to Nova-Lite!',
        'github': 'https://github.com/NovaOSS/nova-lite'
    }

if __name__ == '__main__':
    # run testing server
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=4242)
