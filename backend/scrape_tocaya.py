"""
Scraper for Tocaya torradores de café (tocaya.com.br/cafes-e-afins/).

Fetches the product list via the public WordPress REST API, then iterates
each product page to extract data from JSON-LD schema + WooCommerce
data-product_variations attributes.

Usage:
    pip install requests beautifulsoup4
    python scrape_tocaya.py

Output:
    Writes results to tocaya_beans.json (raw) and prints seed-compatible
    Python dicts ready to paste into seed_data.py.
"""

import json
import time
import re
import html as html_module

import requests
from bs4 import BeautifulSoup

CATALOG_URL = "https://tocaya.com.br/wp-json/wp/v2/product?per_page=100&status=publish"
BASE_URL = "https://tocaya.com.br/cafes-e-afins"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}
REQUEST_DELAY = 1.5  # polite delay between requests


def get_product_list() -> list[dict]:
    """Fetches the list of products from WP REST API."""
    resp = requests.get(CATALOG_URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    products = resp.json()
    print(f"Found {len(products)} products in catalog.")
    return products


def parse_product_page(html_content: str, slug: str) -> dict | None:
    """
    Extracts bean data from a product page HTML source.

    Returns a dict with:
      - name, description, prices, variations, image_url, sku
    or None if the page is not a coffee product.
    """
    # --- JSON-LD Product schema ---
    product_schema = None
    schemas = re.findall(
        r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        html_content,
        re.DOTALL,
    )
    for s in schemas:
        try:
            data = json.loads(s)
            graph = data.get("@graph", [data])
            for item in graph:
                if item.get("@type") == "Product":
                    product_schema = item
                    break
            if product_schema:
                break
        except Exception:
            pass

    # --- Fallback: og:title + og:description (used by simple products like Gesha) ---
    og_title = re.search(
        r'<meta[^>]*property="og:title"[^>]*content="([^"]+)"', html_content
    )
    og_desc = re.search(
        r'<meta[^>]*property="og:description"[^>]*content="([^"]+)"', html_content
    )
    og_title_text = og_title.group(1) if og_title else ""
    og_desc_text = og_desc.group(1) if og_desc else ""

    if not product_schema:
        # For products without a Product schema (e.g. Gesha with no variations),
        # fall back to og: meta and try to extract price from the HTML text.
        if not og_title_text:
            return None
        name = re.sub(r"\s*-\s*Tocaya torradores de café\s*$", "", og_title_text).strip()
        description = html_module.unescape(og_desc_text).strip()
    else:
        name = product_schema.get("name", og_title_text.replace(" - Tocaya torradores de café", "").strip())
        description = product_schema.get("description", og_desc_text).replace("\r\n", " ").strip()

    image_url = ""
    if product_schema:
        if isinstance(product_schema.get("image"), dict):
            image_url = product_schema["image"].get("url", "")
        elif isinstance(product_schema.get("image"), list) and product_schema["image"]:
            first_img = product_schema["image"][0]
            image_url = first_img.get("url", "") if isinstance(first_img, dict) else str(first_img)
        sku = product_schema.get("sku", "")
    else:
        sku = ""

    # --- WooCommerce product attributes (weight, dimensions) ---
    weight = ""
    dims = ""
    attr_table = re.search(
        r'<table[^>]*class="[^"]*woocommerce-product-attributes[^"]*"[^>]*>(.*?)</table>',
        html_content,
        re.DOTALL,
    )
    if attr_table:
        rows = re.findall(r"<tr[^>]*class=\"woocommerce-product-attributes-item[^>]*>(.*?)</tr>", attr_table.group(1), re.DOTALL)
        for row in rows:
            th_m = re.search(r'<th[^>]*>(.*?)</th>', row, re.DOTALL)
            td_m = re.search(r'<td[^>]*>(.*?)</td>', row, re.DOTALL)
            if th_m and td_m:
                label = re.sub(r"<[^>]+>", "", th_m.group(1)).strip()
                value = re.sub(r"<[^>]+>", "", td_m.group(1)).strip()
                if "weight" in label.lower() or "peso" in label.lower():
                    weight = value
                elif "dimens" in label.lower():
                    dims = value

    # --- WooCommerce variations ---
    variations = []
    var_match = re.search(r'data-product_variations="([^"]+)"', html_content)
    if var_match:
        raw = var_match.group(1)
        decoded = html_module.unescape(raw).replace("&quot;", '"')
        try:
            variations = json.loads(decoded)
        except Exception as e:
            print(f"  [WARN] Failed to parse variations: {e}")

    # --- Price: try schema first, then regex R$ in HTML ---
    price = ""
    if product_schema:
        offer_schema = product_schema.get("offers", {})
        if isinstance(offer_schema, dict):
            price = offer_schema.get("lowPrice", "")
        elif isinstance(offer_schema, list) and offer_schema:
            price = offer_schema[0].get("lowPrice", "")

    if not price and variations:
        # Use lowest display_price across variations
        prices = [v.get("display_price", "") for v in variations if v.get("display_price")]
        if prices:
            price = min(prices)

    if not price:
        # Last resort: scan HTML for R$ price (handles Gesha / simple products)
        brl_match = re.search(r'R\$\s*([\d.,]+)', html_content)
        if brl_match:
            price = brl_match.group(1)

    # --- Tasting notes: first sentence of description, before "P.S." ---
    # Skip "Ficha técnica:" header on special products like Gesha
    desc_for_notes = description
    if desc_for_notes.lower().startswith("ficha técnica"):
        desc_for_notes = re.sub(
            r"^Fich[ae] técnica:\s*[^\.]+\.\s*Perfil:\s*",
            "",
            desc_for_notes,
            flags=re.IGNORECASE,
        )
    # Truncate at "Conteúdo:" / "P.S." / "&nbsp" noise markers
    desc_for_notes = re.split(
        r"(?i)\s*conteúdo\s*[:留]?\s*|(&nbsp|nbsp;)\s*",
        desc_for_notes,
    )[0]
    raw_notes = desc_for_notes.split("P.S.")[0].strip().rstrip(".")
    # Clean HTML entities
    raw_notes = html_module.unescape(raw_notes).strip()
    # Parse comma/space-separated notes into a list
    parts = re.split(r"[,;]\s*|\s+e\s+", raw_notes)
    tasting_notes = [
        p.strip().capitalize()
        for p in parts
        if p.strip()
    ] if raw_notes else None

    return {
        "name": name,
        "description": description,
        "tasting_notes": tasting_notes,
        "price": price,
        "sku": sku,
        "image_url": image_url,
        "weight": weight,
        "dimensions": dims,
        "variations": variations,
    }


def extract_bean(raw: dict, slug: str) -> dict:
    """
    Normalises raw product data into a seed_data-compatible bean dict.

    Maps WooCommerce product fields onto BeanCreate schema fields.
    Fields that aren't exposed on the site (roast_level, origin, variety,
    processing, altitude, producer, farm, region, acidity, sweetness, body)
    are left as None so they can be filled in manually or enriched later.
    """
    # Use the first variation as the canonical "base" product
    variations = raw.get("variations", [])
    first = variations[0] if variations else {}

    # Collect unique grind types and weights across all variations
    grind_types = sorted(set(v.get("attributes", {}).get("attribute_moagem", "") for v in variations))
    weights = sorted(set(v.get("attributes", {}).get("attribute_pa_peso", "") for v in variations))

    # Price: use low price from schema, fallback to first variation
    price = raw.get("price") or first.get("display_price", "")

    return {
        "name": raw.get("name", slug.replace("-", " ").title()),
        "roaster": "Tocaya",
        "roast_level": None,       # not exposed on site — fill in manually
        "origin": None,             # not exposed on site — fill in manually
        "variety": None,
        "processing": None,
        "altitude": None,
        "producer": None,
        "farm": None,
        "region": None,
        "tasting_notes": raw.get("tasting_notes"),  # extracted from description
        "acidity": None,
        "sweetness": None,
        "body": None,
        # Extra fields from Tocaya site (not in schema, but useful for DB)
        "_description": raw.get("description", ""),
        "_price_brl": price,
        "_sku": raw.get("sku", ""),
        "_image_url": raw.get("image_url", ""),
        "_weights": weights,
        "_grind_types": grind_types,
        "_raw_slug": slug,
    }


def main():
    print("Fetching product list from WP REST API...")
    products = get_product_list()

    beans = []
    errors = []

    for product in products:
        pid = product["id"]
        slug = product.get("slug", "")
        title = product.get("title", {}).get("rendered", "") or product.get("title", "")
        if isinstance(title, dict):
            title = title.get("rendered", "")

        # Skip non-coffee products (books, mugs, shirts, etc.)
        if slug in [
            "livro-por-tras-da-sua-xicara",
            "camisetas",
            "instantaneo-da-tocaya",
            "diner-mug-da-tocaya-copia",
        ]:
            print(f"  [SKIP] Non-coffee product: {slug}")
            continue

        url = f"{BASE_URL}/{slug}/"
        print(f"  Scraping [{pid}] {slug} ...", end=" ")

        try:
            resp = requests.get(url, headers=HEADERS, timeout=15)
            resp.raise_for_status()
        except requests.RequestException as e:
            print(f"[ERROR] {e}")
            errors.append({"slug": slug, "error": str(e)})
            continue

        raw = parse_product_page(resp.text, slug)
        if raw:
            bean = extract_bean(raw, slug)
            beans.append(bean)
            print(
                f"OK — {bean['name']} | "
                f"variations={len(raw['variations'])} | "
                f"price=R${bean['_price_brl']}"
            )
        else:
            print("[WARN] No product schema found")
            errors.append({"slug": slug, "error": "No product schema"})

        time.sleep(REQUEST_DELAY)

    print(f"\n{'='*60}")
    print(f"Scraped {len(beans)} coffee products ({len(errors)} errors).\n")

    # Write raw results for inspection
    with open("tocaya_beans.json", "w", encoding="utf-8") as f:
        json.dump(beans, f, ensure_ascii=False, indent=2)
    print("Raw data written to tocaya_beans.json\n")

    # Print seed_data-compatible dicts
    print("=" * 60)
    print("# Paste into seed_data.py beans_data list:")
    print("=" * 60)
    for b in beans:
        print(
            f'    {{"name": {json.dumps(b["name"], ensure_ascii=False)}, '
            f'"roaster": "Tocaya", '
            f'"roast": {json.dumps(b["roast_level"], ensure_ascii=False)}, '
            f'"origin": {json.dumps(b["origin"], ensure_ascii=False)}, '
            f'"variety": {json.dumps(b["variety"], ensure_ascii=False)}, '
            f'"processing": {json.dumps(b["processing"], ensure_ascii=False)}, '
            f'"altitude": {json.dumps(b["altitude"], ensure_ascii=False)}, '
            f'"producer": {json.dumps(b["producer"], ensure_ascii=False)}, '
            f'"farm": {json.dumps(b["farm"], ensure_ascii=False)}, '
            f'"region": {json.dumps(b["region"], ensure_ascii=False)}, '
            f'"tasting_notes": {json.dumps(b["tasting_notes"], ensure_ascii=False)}, '
            f'"acidity": {json.dumps(b["acidity"], ensure_ascii=False)}, '
            f'"sweetness": {json.dumps(b["sweetness"], ensure_ascii=False)}, '
            f'"body": {json.dumps(b["body"], ensure_ascii=False)}}},'
        )


if __name__ == "__main__":
    main()
