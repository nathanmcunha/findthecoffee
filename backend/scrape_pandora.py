"""
Scraper for Pandora Coffee Roasters (pandoraroasters.com.br).

Uses the public WooCommerce Store REST API (/wc/store/v1/products) — no
browser rendering required.

API returns: name, slug, short_description, full description (HTML with
structured paragraphs), prices, attributes (Peso, Moagem).
Coffee fields not in the API (altitude, farm, acidity, sweetness, body)
are extracted by parsing the description text.

Usage:
    pip install requests beautifulsoup4
    python scrape_pandora.py

Output:
    Writes results to pandora_beans.json (raw) and prints seed-compatible
    Python dicts ready to paste into seed_data.py.
"""

import json
import re
import html as html_module

import requests

CATALOG_URL = "https://pandoraroasters.com.br/wp-json/wc/store/v1/products"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}


def get_product_list() -> list[dict]:
    """Fetches all products via the public WooCommerce Store REST API."""
    resp = requests.get(CATALOG_URL, params={"per_page": 50}, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    products = resp.json()
    print(f"Found {len(products)} products in store.")
    return products


def parse_description(desc_html: str) -> dict:
    """
    Extracts structured coffee fields from the HTML description.

    Parses <p> paragraphs to find:
      - origin / region (e.g. "Alta Mogiana Mineira")
      - farm (e.g. "Fazenda Terracota")
      - producer (e.g. "Felipe Carvalho")
      - variety (e.g. "Aranãs")
      - processing (e.g. "fermentação aeróbica de 72 horas")
    """
    result = {
        "origin": None,
        "farm": None,
        "producer": None,
        "variety": None,
        "processing": None,
        "altitude": None,
        "_description_clean": "",
    }

    if not desc_html:
        return result

    # Strip HTML, keeping strong/em text
    clean = html_module.unescape(desc_html)
    # Combine all paragraph text for cross-paragraph context
    all_text = re.sub(r"<[^>]+>", " ", clean)
    all_text = re.sub(r"\s+", " ", all_text).strip()

    result["_description_clean"] = all_text[:500]

    # --- Farm (Fazenda X) ---
    farm_m = re.search(r"Fazenda\s+([A-Z][^\.<,]+)", all_text)
    if farm_m:
        result["farm"] = farm_m.group(1).strip().title()

    # --- Producer (produtor X or "Felipe Carvalho utiliza") ---
    producer_m = re.search(
        r"produtor\s+([A-Z][a-zà-ÿ]+\s+[A-Z][a-zà-ÿ]+)",
        all_text,
    )
    if producer_m:
        result["producer"] = producer_m.group(1).strip()
    elif "Felipe Carvalho" in all_text:
        result["producer"] = "Felipe Carvalho"

    # --- Variety (utiliza a variedade X / variedade X) ---
    variety_m = re.search(
        r"variedade\s+([A-Z][a-zà-ÿ\-]+(?:\s+[A-Z][a-zà-ÿ\-]+)*)",
        all_text,
    )
    if variety_m:
        result["variety"] = variety_m.group(1).strip()

    # --- Processing method (fermentação XYZ) ---
    process_m = re.search(
        r"fermentação\s+(?:[a-zà-ÿ]+\s+)?(?:de\s+)?([0-9]+\s+horas|[a-zà-ÿ\s]+)",
        all_text,
        re.IGNORECASE,
    )
    if process_m:
        result["processing"] = f"Fermentação {process_m.group(1).strip()}"

    # --- Origin / Region ---
    origin_m = re.search(
        r"(?:Alta\s+)?Mogiana\s+Mineira|Mogiana|Sul\s+de\s+Minas|Cerrado|Xingu",
        all_text,
        re.IGNORECASE,
    )
    if origin_m:
        result["origin"] = origin_m.group(0).strip()

    return result


def parse_tasting_notes(short_desc_html: str | None) -> list[str] | None:
    """Extracts tasting notes from short_description HTML.

    Format: <p><em>Maracujá  •  Abacaxi  •  Nibs de Cacau</em></p>
    """
    if not short_desc_html:
        return None
    clean = html_module.unescape(short_desc_html)
    clean = re.sub(r"<[^>]+>", "", clean).strip()
    # Replace bullet separators with commas, then split
    parts = re.split(r"\s*[•·]\s*", clean)
    notes = [p.strip().capitalize() for p in parts if p.strip()]
    return notes if notes else None


def parse_product(p: dict) -> dict:
    """Normalises a WC Store API product into a seed-compatible bean dict."""
    desc_data = parse_description(p.get("description", ""))
    tasting_notes = parse_tasting_notes(p.get("short_description"))

    # Price in cents → BRL
    raw_price = p.get("prices", {}).get("price", "")
    price_brl = f"{int(raw_price) / 100:.2f}" if raw_price else ""

    # Attributes: Peso, Moagem
    attrs = {a["name"]: a.get("options", []) for a in p.get("attributes", [])}
    weights = attrs.get("Peso", [])
    grinds = attrs.get("Moagem", [])

    return {
        "name": p.get("name", ""),
        "roaster": "Pandora Coffee Roasters",
        "roast_level": None,
        "origin": desc_data.get("origin"),
        "variety": desc_data.get("variety"),
        "processing": desc_data.get("processing"),
        "altitude": desc_data.get("altitude"),
        "producer": desc_data.get("producer"),
        "farm": desc_data.get("farm"),
        "region": None,
        "tasting_notes": tasting_notes,
        "acidity": None,
        "sweetness": None,
        "body": None,
        # Extra (not in BeanCreate schema)
        "_price_brl": price_brl,
        "_slug": p.get("slug", ""),
        "_sku": p.get("sku", ""),
        "_weights": weights,
        "_grind_types": grinds,
        "_description_clean": desc_data["_description_clean"],
    }


def main():
    print("Fetching products from WooCommerce Store API...")
    products = get_product_list()

    beans = []
    for p in products:
        bean = parse_product(p)
        beans.append(bean)
        notes = bean["tasting_notes"]
        print(
            f"  [{p['id']}] {bean['name']} | "
            f"R${bean['_price_brl']} | "
            f"origin={bean['origin']} | "
            f"variety={bean['variety']} | "
            f"notes={notes}"
        )

    print(f"\n{'='*60}")
    print(f"Scraped {len(beans)} products.\n")

    with open("pandora_beans.json", "w", encoding="utf-8") as f:
        json.dump(beans, f, ensure_ascii=False, indent=2)
    print("Raw data written to pandora_beans.json\n")

    print("=" * 60)
    print("# Paste into seed_data.py beans_data list:")
    print("=" * 60)
    for b in beans:
        print(
            f'    {{"name": {json.dumps(b["name"], ensure_ascii=False)}, '
            f'"roaster": "Pandora Coffee Roasters", '
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
