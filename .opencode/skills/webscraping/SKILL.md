---
name: webscraping
description: >
  Padrões e boas práticas para web scraping com httpx, BeautifulSoup4, selectolax e Playwright
  neste monorepo. Use quando precisar extrair dados de páginas web, lidar com paginação,
  JavaScript renderizado, rate limiting ou estruturar dados raspados.
argument-hint: "[URL alvo ou tipo de dados a extrair]"
---

# Web Scraping — httpx + BeautifulSoup4 / selectolax / Playwright

## Stack por caso de uso

| Cenário | Stack recomendada |
|---------|------------------|
| HTML estático, alto volume | `httpx` + `selectolax` (parser C, 10x mais rápido) |
| HTML estático, seletores complexos | `httpx` + `BeautifulSoup4` + `lxml` |
| JavaScript renderizado (SPA, lazy load) | `playwright` (async) |
| APIs JSON disfarçadas de páginas | `httpx` direto na XHR/Fetch endpoint |

```toml
dependencies = [
    "httpx>=0.27",
    "httpx-retries>=0.4",
    "selectolax>=0.3",     # parser HTML rápido (C)
    "beautifulsoup4>=4.12",
    "lxml>=5",
    "playwright>=1.44",    # apenas se precisar de JS
]
```

## Scraper estático com selectolax (padrão para volume)

```python
import httpx
from selectolax.parser import HTMLParser
from dataclasses import dataclass

@dataclass
class Product:
    name: str
    price: float
    url: str

def scrape_products(base_url: str, pages: int = 1) -> list[Product]:
    products: list[Product] = []

    with httpx.Client(
        headers={"User-Agent": "Mozilla/5.0 (compatible; research-bot/1.0)"},
        timeout=httpx.Timeout(15.0),
        follow_redirects=True,
    ) as client:
        for page in range(1, pages + 1):
            response = client.get(base_url, params={"page": page})
            response.raise_for_status()

            tree = HTMLParser(response.text)
            for node in tree.css("div.product-card"):
                name_node = node.css_first("h2.product-name")
                price_node = node.css_first("span.price")
                link_node = node.css_first("a")

                if not all([name_node, price_node, link_node]):
                    continue

                products.append(Product(
                    name=name_node.text(strip=True),
                    price=float(price_node.text(strip=True).replace("R$", "").replace(",", ".")),
                    url=link_node.attributes.get("href", ""),
                ))

    return products
```

## Scraper com BeautifulSoup4 (seletores complexos)

```python
from bs4 import BeautifulSoup
import httpx

def extract_article(url: str) -> dict[str, str]:
    with httpx.Client(timeout=10.0) as client:
        response = client.get(url)
        response.raise_for_status()

    soup = BeautifulSoup(response.text, "lxml")

    return {
        "title": soup.select_one("h1.article-title").get_text(strip=True),
        "body": "\n".join(p.get_text(strip=True) for p in soup.select("article p")),
        "author": soup.select_one('meta[name="author"]')["content"],
        "published": soup.select_one('time[datetime]')["datetime"],
    }
```

## Scraper assíncrono com paginação

```python
import asyncio
import httpx
from selectolax.parser import HTMLParser

async def scrape_all_pages(base_url: str, max_pages: int = 50) -> list[dict]:
    results: list[dict] = []

    async with httpx.AsyncClient(
        timeout=httpx.Timeout(15.0),
        headers={"User-Agent": "Mozilla/5.0"},
        follow_redirects=True,
    ) as client:
        page = 1
        while page <= max_pages:
            response = await client.get(base_url, params={"page": page})
            if response.status_code == 404:
                break
            response.raise_for_status()

            tree = HTMLParser(response.text)
            items = tree.css("li.item")
            if not items:
                break  # fim da paginação

            for item in items:
                results.append({"text": item.text(strip=True)})

            page += 1
            await asyncio.sleep(0.5)  # rate limiting cortesia

    return results
```

## Playwright para JavaScript renderizado

```python
import asyncio
from playwright.async_api import async_playwright, Page

async def scrape_spa(url: str) -> list[dict]:
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page: Page = await browser.new_page()

        # bloqueia recursos desnecessários para economizar banda
        await page.route("**/*.{png,jpg,gif,svg,woff,woff2}", lambda r: r.abort())

        await page.goto(url, wait_until="networkidle")
        await page.wait_for_selector("div.results", timeout=10_000)

        items = await page.query_selector_all("div.results li")
        results = []
        for item in items:
            text = await item.inner_text()
            results.append({"text": text.strip()})

        await browser.close()
        return results
```

## Tratamento de erros e robustez

```python
import time
import httpx

def fetch_with_backoff(url: str, max_attempts: int = 4) -> httpx.Response:
    """Retry manual com backoff exponencial para rate limits."""
    for attempt in range(max_attempts):
        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(url)

            if response.status_code == 429:
                retry_after = int(response.headers.get("Retry-After", 2 ** attempt))
                time.sleep(retry_after)
                continue

            response.raise_for_status()
            return response

        except httpx.TimeoutException:
            if attempt == max_attempts - 1:
                raise
            time.sleep(2 ** attempt)

    raise RuntimeError(f"Falha após {max_attempts} tentativas: {url}")
```

## Boas práticas obrigatórias

- **User-Agent descritivo**: identifique o bot com contato (ex: `research-bot/1.0 (contact@domain.com)`)
- **Rate limiting**: sempre adicione `sleep` entre requisições (mínimo 500ms por domínio)
- **robots.txt**: verifique e respeite as regras de `robots.txt` antes de scraping
- **Sessão/cookies**: use `httpx.Client` persistente para manter cookies entre requisições
- **HTML muda**: use seletores baseados em atributos de dados (`data-*`) em vez de classes CSS quando disponíveis
- **Extraia somente o necessário**: não armazene HTML cru — parse e persista apenas os campos necessários

## Testes

Use `httpx.MockTransport` ou fixtures com HTML estático — nunca faça requisições reais nos testes.

```python
def test_scrape_products_parses_name_and_price():
    html = """
    <div class="product-card">
      <h2 class="product-name">Widget Pro</h2>
      <span class="price">R$ 49,90</span>
      <a href="/products/1">ver</a>
    </div>
    """
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=html, headers={"content-type": "text/html"})

    # injeta o transport no cliente interno da função
    ...
```
