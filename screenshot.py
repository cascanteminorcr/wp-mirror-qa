import asyncio
from playwright.async_api import async_playwright

async def take_screenshot(url, filename, viewport="desktop"):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080} if viewport=="desktop" else {"width": 375, "height": 812}
        )
        page = await context.new_page()
        await page.goto(url, timeout=60000, wait_until="load")
        await page.screenshot(path=filename, full_page=True)
        await browser.close()
