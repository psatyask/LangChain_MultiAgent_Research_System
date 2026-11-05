
from langchain.tools import tool
from dotenv import load_dotenv
from tavily import TavilyClient
from bs4 import BeautifulSoup
from readability import Document

import requests
import trafilatura
import os
import re
import ipaddress
import socket
from urllib.parse import urlparse

# Load environment variables
load_dotenv()

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY is missing from your .env file.")

tavily = TavilyClient(api_key=TAVILY_API_KEY)


# --------------------------------------------------
# Helper: Clean extracted text
# --------------------------------------------------

def clean_text(text: str, max_chars: int = 5000) -> str:
    """Remove extra whitespace and limit text length."""
    cleaned = re.sub(r"\s+", " ", text).strip()
    return cleaned[:max_chars]


# --------------------------------------------------
# Tool 1: Tavily Web Search
# --------------------------------------------------

@tool
def web_search(query: str) -> str:
    """
    Search the web using Tavily.

    Use this tool to find relevant webpages,
    articles, and sources for a research query.
    """
    try:
        results = tavily.search(
            query=query,
            max_results=5,
            search_depth="basic"
        )

        output = []

        for result in results.get("results", []):
            title = result.get("title", "No title")
            url = result.get("url", "")
            snippet = result.get("content") or ""

            output.append(
                f"Title: {title}\n"
                f"URL: {url}\n"
                f"Snippet: {snippet[:300]}"
            )

        if not output:
            return "No search results found."

        return "\n\n--------------------\n\n".join(output)

    except Exception as e:
        return f"Web search failed: {e}"


# --------------------------------------------------
# Helper: Basic public URL validation
# --------------------------------------------------

def validate_public_url(url: str) -> None:
    """Reject invalid URLs and non-public IP destinations."""
    parsed = urlparse(url)

    if parsed.scheme not in ("http", "https"):
        raise ValueError("Only HTTP and HTTPS URLs are allowed.")

    if not parsed.hostname:
        raise ValueError("URL must contain a hostname.")

    if parsed.username or parsed.password:
        raise ValueError("URLs containing credentials are not allowed.")

    if parsed.port not in (None, 80, 443):
        raise ValueError("Only standard HTTP/HTTPS ports are allowed.")

    addresses = socket.getaddrinfo(
        parsed.hostname,
        parsed.port or (443 if parsed.scheme == "https" else 80),
        type=socket.SOCK_STREAM
    )

    for address in addresses:
        ip = ipaddress.ip_address(address[4][0])
        if not ip.is_global:
            raise ValueError("Private or non-public destinations are blocked.")


# --------------------------------------------------
# Tool 2: Web Scraper
# --------------------------------------------------

@tool
def scrape_url(url: str) -> str:
    """
    Scrape a public webpage and extract readable text.

    Uses Trafilatura, Readability, and BeautifulSoup
    as fallback extraction strategies.

    Use this tool after web_search to read a source.
    """
    try:
        validate_public_url(url)

        headers = {
            "User-Agent": "ResearchBot/1.0",
            "Accept-Language": "en-US,en;q=0.9",
        }

        # Fetch webpage
        response = requests.get(
            url,
            headers=headers,
            timeout=15,
            allow_redirects=False,
            stream=True
        )

        # Do not follow redirects automatically
        if 300 <= response.status_code < 400:
            return "Redirect encountered. Search for the final public URL."

        response.raise_for_status()

        content_type = response.headers.get(
            "Content-Type", ""
        ).lower()

        if not (
            "text/html" in content_type
            or "application/xhtml+xml" in content_type
        ):
            return "URL does not point to an HTML webpage."

        # Limit download size to 2 MB
        max_bytes = 2 * 1024 * 1024
        chunks = []
        total_bytes = 0

        for chunk in response.iter_content(chunk_size=16384):
            total_bytes += len(chunk)

            if total_bytes > max_bytes:
                return "Webpage exceeds the maximum allowed size."

            chunks.append(chunk)

        html = b"".join(chunks).decode(
            response.encoding or "utf-8",
            errors="replace"
        )

        # ------------------------------------------
        # Strategy 1: Trafilatura
        # ------------------------------------------

        extracted = trafilatura.extract(
            html,
            include_comments=False,
            include_tables=False
        )

        if extracted and len(extracted.strip()) > 200:
            cleaned = clean_text(extracted)

            return (
                f"Source: {url}\n\n"
                f"Content:\n{cleaned}"
            )

        # ------------------------------------------
        # Strategy 2: Readability
        # ------------------------------------------

        doc = Document(html)
        clean_html = doc.summary()

        soup = BeautifulSoup(
            clean_html,
            "html.parser"
        )

        for tag in soup([
            "script",
            "style",
            "nav",
            "footer",
            "header",
            "aside",
            "form"
        ]):
            tag.decompose()

        text = soup.get_text(
            separator=" ",
            strip=True
        )

        if len(text) > 200:
            cleaned = clean_text(text)

            return (
                f"Source: {url}\n\n"
                f"Content:\n{cleaned}"
            )

        # ------------------------------------------
        # Strategy 3: BeautifulSoup Fallback
        # ------------------------------------------

        soup = BeautifulSoup(
            html,
            "html.parser"
        )

        for tag in soup([
            "script",
            "style",
            "nav",
            "footer",
            "header",
            "aside",
            "form",
            "noscript"
        ]):
            tag.decompose()

        main_content = (
            soup.find("article")
            or soup.find("main")
            or soup.body
            or soup
        )

        text = main_content.get_text(
            separator=" ",
            strip=True
        )

        cleaned = clean_text(text)

        if cleaned:
            return (
                f"Source: {url}\n\n"
                f"Content:\n{cleaned}"
            )

        return "Could not extract meaningful content from this page."

    except requests.exceptions.Timeout:
        return "Request timed out while scraping the URL."

    except requests.exceptions.HTTPError as e:
        return f"HTTP error occurred: {e}"

    except requests.exceptions.RequestException as e:
        return f"Network error while scraping: {e}"

    except Exception as e:
        return f"Could not scrape URL: {e}"


# --------------------------------------------------
# Test Tools
# --------------------------------------------------

if __name__ == "__main__":

    print("\nTesting Tavily Web Search...\n")

    search_result = web_search.invoke({
        "query": "Latest developments in Agentic AI"
    })

    print(search_result)

    print("\nTesting Web Scraper...\n")

    scrape_result = scrape_url.invoke({
        "url": "https://www.python.org/about/"
    })

    print(scrape_result)
