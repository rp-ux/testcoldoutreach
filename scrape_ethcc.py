#!/usr/bin/env python3
"""Scrape EthCC[9] speakers page using pyppeteer (headless Chromium)."""

import asyncio
import json
import os

# Disable proxy for pyppeteer's chromium download and browser requests
for key in list(os.environ.keys()):
    if 'proxy' in key.lower():
        del os.environ[key]

from pyppeteer import launch

async def main():
    print("[*] Launching headless Chromium...")
    browser = await launch(
        headless=True,
        args=[
            '--no-sandbox',
            '--disable-setuid-sandbox',
            '--disable-dev-shm-usage',
            '--disable-gpu',
            '--no-proxy-server',
        ],
        handleSIGINT=False,
        handleSIGTERM=False,
        handleSIGHUP=False,
    )

    page = await browser.newPage()
    await page.setUserAgent(
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )

    print("[*] Navigating to https://ethcc.io/speakers ...")
    try:
        await page.goto('https://ethcc.io/speakers', {
            'waitUntil': 'networkidle0',
            'timeout': 60000,
        })
    except Exception as e:
        print(f"[!] Navigation error: {e}")
        # Try to work with whatever loaded
        pass

    print("[*] Waiting for page to load...")
    await asyncio.sleep(5)

    # Scroll down to load all speakers (lazy loading)
    print("[*] Scrolling to load all speakers...")
    for i in range(20):
        await page.evaluate('window.scrollBy(0, 1000)')
        await asyncio.sleep(1)

    # Scroll back up
    await page.evaluate('window.scrollTo(0, 0)')
    await asyncio.sleep(2)

    # Get the full page HTML
    content = await page.content()

    # Save raw HTML for inspection
    with open('/home/user/testcoldoutreach/ethcc_speakers_raw.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"[*] Saved raw HTML ({len(content)} chars)")

    # Try to extract speaker data from the page
    speakers = await page.evaluate('''() => {
        const results = [];

        // Try various selectors that conference sites commonly use
        const selectors = [
            '[class*="speaker"]',
            '[class*="Speaker"]',
            '[class*="person"]',
            '[class*="Person"]',
            '[class*="card"]',
            '[class*="team"]',
            '[class*="member"]',
            '[data-speaker]',
            'article',
            '.grid > div',
            'a[href*="speaker"]',
        ];

        for (const sel of selectors) {
            const elements = document.querySelectorAll(sel);
            if (elements.length > 5) {
                elements.forEach(el => {
                    const text = el.innerText?.trim();
                    if (text && text.length > 2 && text.length < 500) {
                        results.push({
                            selector: sel,
                            text: text,
                            href: el.href || el.querySelector('a')?.href || '',
                        });
                    }
                });
                if (results.length > 0) break;
            }
        }

        // Also grab all links
        const links = [];
        document.querySelectorAll('a').forEach(a => {
            const text = a.innerText?.trim();
            const href = a.href;
            if (text && text.length > 1) {
                links.push({ text, href });
            }
        });

        return { speakers: results, links: links, title: document.title, bodyText: document.body?.innerText?.substring(0, 10000) };
    }''')

    print(f"\n[*] Page title: {speakers.get('title', 'N/A')}")
    print(f"[*] Found {len(speakers.get('speakers', []))} speaker elements")
    print(f"[*] Found {len(speakers.get('links', []))} links")

    # Save extracted data
    with open('/home/user/testcoldoutreach/ethcc_speakers_data.json', 'w', encoding='utf-8') as f:
        json.dump(speakers, f, ensure_ascii=False, indent=2)

    # Print body text (first 10000 chars)
    body_text = speakers.get('bodyText', '')
    print(f"\n[*] Page body text (first 10000 chars):\n")
    print(body_text[:10000])

    await browser.close()
    print("\n[*] Done!")

asyncio.get_event_loop().run_until_complete(main())
