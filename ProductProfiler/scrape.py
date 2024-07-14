"""Module to fetch pages"""

import asyncio
import httpx
from bs4 import BeautifulSoup
import html2text


def parse_page(page: str) -> str:
    """
    ### Responsibility:
        - Clean the HTML page content by removing specific tags.
        - Convert the cleaned HTML content to plain text.

    ### Args:
        - `page`: str
            The HTML content of the page as a string.

    ### Returns:
        - `text`: str
            The plain text content of the page with certain tags removed and formatted with new lines.

    ### How does the function work:
        - Parse the HTML content using BeautifulSoup
        - Identify and remove specific tags like header, nav, footer, script, and style
        - Extract and return the cleaned plain text content using new lines as separators
    """
    soup = BeautifulSoup(page, "html.parser")

    tags_to_remove = ["header", "nav", "footer", "script", "style"]

    for tag in tags_to_remove:
        matches = soup.select(tag)
        for match in matches:
            _ = match.extract()

    return soup.get_text(separator="\n\n", strip=True)


async def zyte_worker(url: str, zyte_key: str) -> str | None:
    """
    ### Responsibility:
        - Fetch the HTML content of a given URL using the Zyte API.

    ### Args:
        - `url`: str
            The URL of the page to be scraped.
        - `zyte_key`: str
            The API key for authenticating with Zyte.

    ### Returns:
        - `browser_html`: str | None
            The HTML content of the page if successfully fetched, otherwise None.

    ### Raises:
        - `ValueError`:
            Raised when the page cannot be fetched after multiple retries.

    ### How does the function work:
        - Attempt to fetch the page content using Zyte API up to 5 times in case of failures
        - Use httpx.AsyncClient to make POST requests to Zyte's extract endpoint
        - Return the browser HTML content if the request is successful
        - Print error message and retry on failure
        - Raise ValueError if the page cannot be fetched after the specified number of retries
    """

    retries = 0
    while retries < 5:
        try:
            async with httpx.AsyncClient() as client:
                api_response = await client.post(
                    "https://api.zyte.com/v1/extract",
                    auth=(zyte_key, ""),
                    json={"url": url, "browserHtml": True},
                    timeout=60,
                )

            browser_html: str = api_response.json()["browserHtml"]
            return browser_html

        except Exception as e:
            print(
                f"Error fetching page with zyte: {type(e).__name__}: {e}. Retrying..."
            )
            retries += 1
            continue

    raise ValueError(f"Unable to scrape page {url}")


async def entry_handle_page_fetch(url: str, zyte_key: str) -> str:
    """
    ### Responsibility:
        - Fetch and parse the HTML content of a given URL.

    ### Args:
        - `url`: str
            The URL of the page to be fetched and parsed.
        - `zyte_key`: str
            The API key for authenticating with Zyte.

    ### Returns:
        - `simple_page`: str
            The plain text content of the page after removing unnecessary HTML tags.

    ### How does the function work:
        - Call `zyte_worker` to fetch the raw HTML content of the page using Zyte API
        - Pass the raw HTML content to `parse_page` to clean and convert it to plain text
        - Return the cleaned plain text content
    """

    raw_page = await zyte_worker(url, zyte_key)
    simple_page = parse_page(raw_page)

    return simple_page


if __name__ == "__main__":
    import os
    from dotenv import load_dotenv

    load_dotenv()

    page = asyncio.run(
        entry_handle_page_fetch(
            "https://www.amazon.com/New-Balance-Womens-Sneaker-Nimbus/dp/B093QLTD9Q/",
            os.getenv("ZYTE_KEY"),
        )
    )

    with open("page.md", "w", encoding="utf-8") as wf:
        wf.write(page)

    print(page)
