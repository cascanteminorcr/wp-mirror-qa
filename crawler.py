import asyncio
from playwright.async_api import async_playwright
from urllib.parse import urljoin

async def get_all_links(base_url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(base_url, wait_until="networkidle")

        anchors = await page.query_selector_all("a[href]")
        links = set()
        for a in anchors:
            href = await a.get_attribute("href")
            if href:
                full_url = urljoin(base_url, href)
                if base_url in full_url:
                    links.add(full_url)

        await browser.close()
        return list(links)
