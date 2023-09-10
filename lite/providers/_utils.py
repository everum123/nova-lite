import random
import aiofiles

GPT_3 = [
    'gpt-3.5-turbo',
    'gpt-3.5-turbo-16k',
    'gpt-3.5-turbo-0613',
    'gpt-3.5-turbo-0301',
    'gpt-3.5-turbo-16k-0613',
]

GPT_4 = GPT_3 + [
    'gpt-4',
    'gpt-4-0314',
    'gpt-4-0613',
]

GPT_4_32K = GPT_4 + [
    'gpt-4-32k',
    'gpt-4-32k-0314',
    'gpt-4-32k-0613',
]

async def conversation_to_prompt(conversation: list) -> str:
    text = ''

    for message in conversation:
        text += f'<|{message["role"]}|>: {message["content"]}\n'

    text += '<|assistant|>:'

    return text

async def random_secret_for(name: str) -> str:
    async with aiofiles.open(f'secrets/{name}.txt', encoding='utf8') as f:
        lines = await f.readlines()

    lines = [line.strip() for line in lines if line.strip()]

    try:
        return random.choice(lines)
    except IndexError as exc:
        raise ValueError(f'Keys missing for "{name}" NO_AUTH') from exc
