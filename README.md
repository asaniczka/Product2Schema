# Product2Schema

**Product2Schema** is a Python library designed to convert product URLs into standardized product schemas.

This library offers both synchronous and asynchronous capabilities to fit various use cases.

The conversion process leverages the Zyte API for fetching page contents and OpenAI for generating the schema from the fetched content.

## Features

- Asynchronous and synchronous versions available.
- Converts product URLs into structured product schemas.
- Utilizes Zyte API for web scraping and OpenAI for AI transformation.
- Easy to integrate with existing Python projects.

## Installation

You can install the library from PyPI:

```sh
pip install Product2Schema
```

## Usage

### Synchronous Engine

The **SyncEngine** class provides a synchronous interface for URL transformation.

```python
from Product2Schema import SyncEngine

# Initialize the engine with your API keys
sync_engine = SyncEngine(openai_key="your_openai_key", zyte_key="your_zyte_key")

# Transform a product URL
response = sync_engine.transform_url("https://example.com/product")

# Access the response details
print(f"Original URL: {response.url}")
print(f"Cost: {response.cost}")
print(f"Product Schema: {response.product_schema}")
```

### Asynchronous Engine

The **AsyncEngine** class provides an asynchronous interface for URL transformation and is more suitable for use cases that require non-blocking operations.

```python
import asyncio
from Product2Schema import AsyncEngine

async def main():
    # Initialize the engine with your API keys
    async_engine = AsyncEngine(openai_key="your_openai_key", zyte_key="your_zyte_key")

    # Transform a product URL
    response = await async_engine.transform_url("https://example.com/product")

    # Access the response details
    print(f"Original URL: {response.url}")
    print(f"Cost: {response.cost}")
    print(f"Product Schema: {response.product_schema}")

# Run the async main function
asyncio.run(main())
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the Apache-2.0 License.
