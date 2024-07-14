# pylint:disable=wrong-import-position


import os
import asyncio

import httpx
from wrapworks import cwdtoenv
from dotenv import load_dotenv
from rich import print
import chompjs
from pydantic import ValidationError


cwdtoenv()
load_dotenv()


from models.genai_models import (
    ValidLLMModels,
    LLM_COST_PER_TOKEN,
    LLMMessage,
    LLMMessageLog,
    AIResponse,
    LLMRoles,
)
from models.product_models import ProductSchema, OPENAPI_SCHEMA


async def invoke_openai(
    model: ValidLLMModels | str, messages: LLMMessageLog, api_key: str
) -> AIResponse:
    """
    ### Responsibility:
        - Send a request to the OpenAI API to get a response based on the provided model and messages.

    ### Args:
        - `model`: ValidLLMModels | str
            The language model to be used, either as a string or an instance of ValidLLMModels.
        - `messages`: LLMMessageLog
            A log of messages to be sent to the OpenAI API.
        - `api_key`: str
            The API key for authenticating with OpenAI.

    ### Returns:
        - `AIResponse`: AIResponse
            The response from the OpenAI API containing the model's output.

    ### Raises:
        - `RuntimeError`:
            Raised when there is an error with the OpenAI response payload.
        - `Exception`:
            Raised for any other errors that occur during parsing or API interaction.

    ### How does the function work:
        - Convert `model` to string if it is not already a string
        - Construct the payload with model type, messages, and max tokens
        - Set the headers with content type and authorization token
        - Use httpx.AsyncClient to send a POST request to the OpenAI API
        - Handle and raise errors related to the API response
        - Return the AI response in a structured `AIResponse` object
    """

    if not isinstance(model, str):
        model = model.value

    url = "https://api.openai.com/v1/chat/completions"

    payload = {
        "model": model,
        "messages": [x.model_dump() for x in messages.messages],
        "max_tokens": 1500,
    }
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}",
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=payload, headers=headers, timeout=120)

    try:
        data = response.json()
        if data.get("error"):
            print(payload)
            raise RuntimeError(data["error"]["message"])
        return AIResponse(**data)
    except RuntimeError:
        raise
    except Exception as e:
        print(f"Error parsing {response.text}: {type(e).__name__}: {e}")
        raise


async def handler_generate_response(
    messages: LLMMessageLog, model: ValidLLMModels, api_key: str
) -> AIResponse:
    """
    ### Responsibility:
        - Generate a response from OpenAI API and calculate the cost based on the model used.

    ### Args:
        - `messages`: LLMMessageLog
            A log of messages to be sent to the OpenAI API.
        - `model`: ValidLLMModels
            The language model to be used for generating the response.
        - `api_key`: str
            The API key for authenticating with OpenAI.

    ### Returns:
        - `AIResponse`: AIResponse
            The response from the OpenAI API along with calculated cost information.

    ### How does the function work:
        - Call `invoke_openai` to get the response from the OpenAI API
        - Calculate the cost of the response based on the model and token usage
        - Return the structured `AIResponse` with the cost included
    """

    response = await invoke_openai(model, messages, api_key)
    response.calculate_cost(model.value, LLM_COST_PER_TOKEN)

    return response


def convert_response_to_schema(res: str) -> ProductSchema:
    """
    ### Responsibility:
        - Convert a JavaScript object in a string format to a `ProductSchema`.

    ### Args:
        - `res`: str
            The response string containing a JavaScript object.

    ### Returns:
        - `schemed_product`: ProductSchema
            The converted `ProductSchema` object containing structured product data.

    ### How does the function work:
        - Parse the JavaScript object from the string using `chompjs.parse_js_object`
        - Instantiate a `ProductSchema` object with the parsed data
        - Return the `ProductSchema` object
    """

    data = chompjs.parse_js_object(res)
    schemed_product = ProductSchema(**data)
    return schemed_product


async def entry_convert_to_schema(
    page: str, api_key: str
) -> tuple[AIResponse, ProductSchema]:
    """
    ### Responsibility:
        - Generate an AI response from the webpage HTML and convert it into a `ProductSchema`.

    ### Args:
        - `page`: str
            The HTML content of the webpage to be analyzed.
        - `api_key`: str
            The API key for authenticating with OpenAI.

    ### Returns:
        - `(response, parsed_product)`: tuple[AIResponse, ProductSchema]
            A tuple containing the AI response and the parsed product schema.

    ### How does the function work:
        - Create a log of messages defining the task and schema using `LLMMessageLog`
        - Append the user's HTML content to the message log
        - Initialize running cost and retry counter
        - Attempt to generate a response from the AI up to 5 times
        - On success, add the current cost to the running total
        - Convert the response text to a `ProductSchema` object using `convert_response_to_schema`
        - Update the response with the running cost
        - Return the AI response and the parsed product schema
        - Retry on validation errors and print exceptions
    """

    messages = LLMMessageLog(
        messages=[
            LLMMessage(
                role=LLMRoles.SYSTEM,
                content="""You are a webpage parser. User will provide you with the HTML of a webpage. 
                You should determine if it's a product page, and if it is fill the data in the given format. If it's not a product page, then product details are not requried
                Reply in valid JSON.
                """,
            ),
            LLMMessage(
                role=LLMRoles.SYSTEM,
                content=f"""Below is the OpenAPI JSON schema:

                {OPENAPI_SCHEMA}
                """,
            ),
        ]
    )

    messages.messages.append(LLMMessage(role=LLMRoles.USER, content=page))

    running_cost = 0
    retries = 0
    while retries < 5:
        try:
            response = await handler_generate_response(
                messages, ValidLLMModels.OPENAI_GPT4o, api_key
            )
            # add current cost to checkpoint incase validation fails
            if response:
                running_cost += response.cost

            parsed_product = convert_response_to_schema(response.text)
            response.cost = running_cost  # combine cost of failed previous runs
            return response, parsed_product
        except ValidationError:
            retries += 1
            print(f"Error extracting metadata with OpenAI. Retrying...")
        except Exception as e:
            retries += 1
            print(
                f"Error extracting metadata with OpenAI: {type(e).__name__}: {e}. Retrying..."
            )


if __name__ == "__main__":

    with open("page.md", "r", encoding="utf-8") as rf:
        page = rf.read()

    res = asyncio.run(entry_convert_to_schema(page, os.getenv("OPENAI_API_KEY")))
    print(res)
