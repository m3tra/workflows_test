"""OpenAI Generic LLM caller interface"""

import time

from loguru import logger
from openai import AsyncAzureOpenAI
from openai.types.chat import ChatCompletionMessageParam


async def call_chat_completions(
    llm_client: AsyncAzureOpenAI, llm_model: str, text: str, prompt: list[ChatCompletionMessageParam], process_name: str
) -> str | None:
    try:
        logger.info(f"{process_name} starting...")
        class_start = time.time()
        completion = await llm_client.chat.completions.create(
            model=llm_model,
            messages=prompt,
            temperature=0,
            top_p=1,
            seed=42,
            response_format={"type": "json_object"},
        )
        completion = completion.choices[0].message.content

        logger.info(f"{process_name} collected in {time.time()-class_start}")
    except Exception as e:
        logger.info(
            f"""Error while running {process_name} 
            DOC_LEN: {len(text)} 
            prompt : {prompt}
            model_name: {llm_model}
            \n{e}"""
        )
        completion = None

    return completion
