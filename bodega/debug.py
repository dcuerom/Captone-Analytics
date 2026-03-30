from playwright.sync_api import sync_playwright

START_URL = "https://www.portalinmobiliario.com/venta/bodega/_DisplayType_M_item*location_lat:-33.69426558778418*-33.42734340088877,lon:-70.82396230109555*-70.39377889045102"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
    page = context.new_page()
    page.goto(START_URL)
    page.wait_for_load_state('domcontentloaded')
    import time
    time.sleep(3)
    links = page.locator('a').all()
    count = 0
    for l in links:
        href = l.get_attribute('href')
        cls = l.get_attribute('class')
        if href and 'MLC' in href:
            print(f"CLASS: {cls} | HREF: {href}")
            count += 1
    print(f"Total MLC links: {count}")
    browser.close()
    browser.close()
