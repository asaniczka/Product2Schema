"""Module for the sync engine"""

import asyncio
import time

from product2schema.extract_metadata import entry_convert_to_schema
from product2schema.scrape import entry_handle_page_fetch
from product2schema.models.product_models import ProductSchema
from product2schema.models.engine_models import TransformUrlResponse


class SyncEngine:
    """
    Product2Schema is meant to be used Async. But this is an alternative to Async version
    """

    def __init__(self, openai_key: str, zyte_key: str) -> None:
        self.openai_key = openai_key
        self.zyte_key = zyte_key

    def transform_url(self, url: str) -> TransformUrlResponse:
        """
        ### Responsibility:
            - Transform a given product URL into a standardized product schema.

        ### Args:
            - `url`: str
                The product URL to be transformed.

        ### Returns:
            - `TransformUrlResponse`: TransformUrlResponse
                An object containing the original URL, cost of the AI transformation, and the product schema derived from the URL.

        ### Raises:
            - `RuntimeError`:
                Raised when the URL cannot be transformed into a schema.

        ### How does the function work:
            - Fetch the page content from the given URL using Zyte api
            - Convert the fetched page content into a product schema using OpenAI
            - Raise an error if schema transformation fails
            - Return a response object containing the URL, cost, and product schema
        """

        page = asyncio.run(entry_handle_page_fetch(url, self.zyte_key))
        schema_response = asyncio.run(entry_convert_to_schema(page, self.openai_key))
        if not schema_response:
            raise RuntimeError("Unable to transform URL to schema")

        ai_response, schemed_product = schema_response
        return TransformUrlResponse(
            url=url, cost=ai_response.cost, product_schema=schemed_product
        )


class AsyncEngine:
    """
    Main AsyncEngine
    """

    def __init__(self, openai_key: str, zyte_key: str) -> None:
        self.openai_key = openai_key
        self.zyte_key = zyte_key

    async def transform_url(self, url: str) -> TransformUrlResponse:
        """
        ### Responsibility:
            - Transform a given product URL into a standardized product schema.

        ### Args:
            - `url`: str
                The product URL to be transformed.

        ### Returns:
            - `TransformUrlResponse`: TransformUrlResponse
                An object containing the original URL, cost of the AI transformation, and the product schema derived from the URL.

        ### Raises:
            - `RuntimeError`:
                Raised when the URL cannot be transformed into a schema.

        ### How does the function work:
            - Fetch the page content from the given URL using Zyte api
            - Convert the fetched page content into a product schema using OpenAI
            - Raise an error if schema transformation fails
            - Return a response object containing the URL, cost, and product schema
        """

        start = time.perf_counter()
        page = await entry_handle_page_fetch(url, self.zyte_key)
        schema_response = await entry_convert_to_schema(page, self.openai_key)
        if not schema_response:
            raise RuntimeError("Unable to transform URL to schema")

        ai_response, schemed_product = schema_response
        end = time.perf_counter()

        # print(f"A transform request took {end-start} seconds")
        return TransformUrlResponse(
            url=url, cost=ai_response.cost, product_schema=schemed_product
        )


if __name__ == "__main__":
    pass
