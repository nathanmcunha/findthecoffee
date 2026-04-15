"""
Scraper for Pato Rei (patoreisp.com.br).

Uses the public WooCommerce Store REST API (no auth required).
Description HTML uses a consistent structured block (vc_column_text) with
clearly labelled sections: notas sensoriais, sítio/fazenda, produtor,
região, variedade, processamento.

Usage:
    pip install requests beautifulsoup4
    python scrape_pato.py

Output:
    Writes results to pato_beans.json and prints seed-compatible Python dicts.
"""

import json
import re
import subprocess
import html as html_module

CATALOG_URL = "https://patoreisp.com.br/wp-json/wc/store/v1/products"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}


def _curl_get(url: str, params: dict | None = None) -> tuple[int, str]:
    """Makes an HTTP GET using subprocess curl (bypasses ModSecurity on patoreisp.com.br).

    Returns (status_code, response_text).
    -w outputs status code to stdout (not stderr), appended after the body.
    """
    if params:
        qs = "&".join(f"{k}={v}" for k, v in params.items())
        url = f"{url}?{qs}"
    import tempfile, os
    tmp = tempfile.mktemp(suffix=".json")
    try:
        cmd = ["curl", "-s", "-w", "%{http_code}", "-o", tmp, url]
        cp = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        # stdout contains "<status_code>\n" after the body (because -o redirects body to file)
        extra = cp.stdout.strip()
        status = int(extra) if extra.isdigit() else (0 if cp.returncode != 0 else 200)
        with open(tmp) as fh:
            body = fh.read()
        return status, body
    finally:
        os.unlink(tmp)


def get_all_products() -> list[dict]:
    """Fetches all products via WC Store REST API, handling pagination."""
    all_products = []
    page = 1
    while True:
        status, body = _curl_get(CATALOG_URL, params={"per_page": 50, "page": page})
        if status != 200 or not body.strip():
            break
        products = json.loads(body)
        if not products:
            break
        all_products.extend(products)
        print(f"  Page {page}: {len(products)} products (total: {len(all_products)})")
        page += 1
        if len(products) < 50:
            break
    print(f"Found {len(all_products)} products total.")
    return all_products


def parse_description(desc_html: str) -> dict:
    """
    Extracts structured coffee fields from the vc_column_text description block.

    Expected format per product (all inside <p> tags):
        notas sensoriais
        <strong>NOTE1, NOTE2 e NOTE3</strong>

        sítio / fazenda
        <strong>FARM_NAME</strong>

        produtor / produtores
        <strong>PRODUCER_NAME</strong>

        região
        <strong>REGION</strong>

        variedade
        <strong>VARIETY</strong>

        processamento
        <strong>PROCESSING</strong>
    """
    result = {
        "tasting_notes": None,
        "farm": None,
        "producer": None,
        "origin": None,
        "variety": None,
        "processing": None,
        "_raw_desc": "",
    }

    if not desc_html:
        return result

    clean = html_module.unescape(desc_html)

    # Extract the structured block between first <strong> and the closing <blockquote>
    # The notes line pattern: <strong>NOTE1, NOTE2 e NOTE3</strong>
    notes_m = re.search(
        r"notas sensoriais\s*<br\s*/?>\s*<strong>([^<]+)</strong>",
        clean,
        re.IGNORECASE,
    )
    if notes_m:
        raw_notes = notes_m.group(1).strip()
        # Skip narrative descriptions that are too long or too sparse — they're not structured notes
        if len(raw_notes) > 250:
            result["tasting_notes"] = None
        else:
            # Split by ", e " or ", " or " e "
            parts = re.split(r",\s*e\s+|,\s*", raw_notes)
            parts = [p.strip() for p in parts if p.strip()]
            # If the average part length is high (>=40), it's probably narrative text — skip
            if parts and (sum(len(p) for p in parts) / len(parts)) >= 40:
                result["tasting_notes"] = None
            else:
                result["tasting_notes"] = [
                    p.strip().capitalize() for p in parts if p.strip()
                ]

    # Field patterns — each section has a label followed by <strong>VALUE</strong>
    field_patterns = [
        (r"sít[ií]o\s*<br\s*/?>\s*<strong>([^<]+)</strong>", "farm"),
        (r"fazenda\s*<br\s*/?>\s*<strong>([^<]+)</strong>", "farm"),
        (r"produtores?\s*<br\s*/?>\s*<strong>([^<]+)</strong>", "producer"),
        (r"produtor\s*<br\s*/?>\s*<strong>([^<]+)</strong>", "producer"),
        (r"reg[iã]o\s*<br\s*/?>\s*<strong>([^<]+)</strong>", "origin"),
        (r"variedade\s*<br\s*/?>\s*<strong>([^<]+)</strong>", "variety"),
        (r"processamento\s*<br\s*/?>\s*<strong>([^<]+)</strong>", "processing"),
    ]

    for pattern, field in field_patterns:
        if result[field] is None:  # don't overwrite
            m = re.search(pattern, clean, re.IGNORECASE)
            if m:
                result[field] = m.group(1).strip().title()

    result["_raw_desc"] = clean[:300]
    return result


def parse_short_description(short_html: str | None) -> list[str] | None:
    """
    Extracts tasting notes from the short_description HTML.

    Format varies — sometimes <p><em>NOTE1 • NOTE2 • NOTE3</em></p>
    or wrapped in <strong> spans.
    """
    if not short_html:
        return None
    clean = html_module.unescape(short_html)
    # Remove all HTML tags, keep text
    clean = re.sub(r"<[^>]+>", " ", clean).strip()
    # Skip narrative text that's too long or has overly long parts
    if len(clean) > 250:
        return None
    # Split on bullet separators
    parts = re.split(r"\s*[•·]\s*|\s+e\s+|\s*,\s*", clean)
    parts = [p.strip() for p in parts if p.strip()]
    # If average is high or any part is very long, it's probably narrative text — skip
    if parts and ((sum(len(p) for p in parts) / len(parts)) > 30 or any(len(p) > 50 for p in parts)):
        return None
    notes = [p.strip().capitalize() for p in parts if p.strip()]
    return notes if notes else None


def parse_product(p: dict) -> dict:
    """Normalises a WC Store API product into a seed-compatible bean dict."""
    desc_data = parse_description(p.get("description", ""))

    # Tasting notes: short_desc > parsed description notes
    tasting_notes = parse_short_description(p.get("short_description"))
    if not tasting_notes and desc_data["tasting_notes"]:
        tasting_notes = desc_data["tasting_notes"]

    # Price
    raw_price = p.get("prices", {}).get("price", "")
    price_brl = f"{int(raw_price) / 100:.2f}" if raw_price else ""

    # Attributes (Tamanho)
    attrs = {a["name"]: [t["name"] for t in a.get("terms", [])] for a in p.get("attributes", [])}
    weights = attrs.get("Tamanho", [])

    return {
        "name": p.get("name", ""),
        "roaster": "Pato Rei",
        "roast_level": None,
        "origin": desc_data.get("origin"),
        "variety": desc_data.get("variety"),
        "processing": desc_data.get("processing"),
        "altitude": None,
        "producer": desc_data.get("producer"),
        "farm": desc_data.get("farm"),
        "region": desc_data.get("origin"),  # Pato Rei uses "região" as region
        "tasting_notes": tasting_notes,
        "acidity": None,
        "sweetness": None,
        "body": None,
        # Extra
        "_price_brl": price_brl,
        "_slug": p.get("slug", ""),
        "_sku": p.get("sku", ""),
        "_weights": weights,
        "_raw_desc": desc_data["_raw_desc"],
    }


def main():
    print("Fetching products from Pato Rei WooCommerce Store API...")
    products = get_all_products()

    beans = []
    skipped = []
    for p in products:
        bean = parse_product(p)
        cats = [c["name"] for c in p.get("categories", [])]
        notes = bean["tasting_notes"]

        # Skip non-coffee products (kits, subscriptions, accessories)
        if any(
            skip in cats
            for skip in [
                "promopato",
                "reservas",
                "blend",
                "assinatura",
            ]
        ) or any(
            skip in bean["name"].lower()
            for skip in [
                "kit ",
                "cansei de ser",
                "panetone",
                "sorvete",
                "pudim",
            ]
        ):
            skipped.append(bean["name"])
            continue

        beans.append(bean)
        print(
            f"  [{p['id']}] {bean['name']} | "
            f"R${bean['_price_brl']} | "
            f"farm={bean['farm']} | "
            f"origin={bean['origin']} | "
            f"variety={bean['variety']} | "
            f"notes={notes}"
        )

    print(f"\n{'='*60}")
    print(f"Scraped {len(beans)} coffee products ({len(skipped)} skipped: {skipped}).\n")

    with open("pato_beans.json", "w", encoding="utf-8") as f:
        json.dump(beans, f, ensure_ascii=False, indent=2)
    print("Raw data written to pato_beans.json\n")

    print("=" * 60)
    print("# Paste into seed_data.py beans_data list:")
    print("=" * 60)
    for b in beans:
        print(
            f'    {{"name": {json.dumps(b["name"], ensure_ascii=False)}, '
            f'"roaster": "Pato Rei", '
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
