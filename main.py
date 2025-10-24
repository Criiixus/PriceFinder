import time
import random
import re
import csv
import pandas as pd
from typing import List, Dict, Optional
from urllib.parse import urlparse, quote_plus

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import NoSuchElementException

NUM_RESULTS = 5
HEADLESS = True
WAIT_BETWEEN_ACTIONS = (2, 5)
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120 Safari/537.36"

ECOMMERCE_DOMAINS = [
    "mercadolivre.com.br",
    "amazon.com.br",
    "americanas.com.br",
    "magazineluiza.com.br",
    "submarino.com.br",
    "shopee.com.br",
    "casasbahia.com.br",
]

def rand_sleep():
    time.sleep(random.uniform(*WAIT_BETWEEN_ACTIONS))

def normaliza_preco(text: str) -> Optional[float]:
    if not text:
        return None
    s = re.sub(r"[^\d,\.]", "", text)
    if s.count(",") == 1 and s.count(".") == 0:
        s = s.replace(",", ".")
    elif s.count(".") > 1:
        s = s.replace(".", "")
    s = s.replace(",", ".")
    try:
        return float(s)
    except:
        return None

def start_driver() -> webdriver.Chrome:
    options = Options()
    if HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument(f"user-agent={USER_AGENT}")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {"source": "Object.defineProperty(navigator, 'webdriver', {get: () => false})"})
    return driver

def domain_of(url: str) -> str:
    net = urlparse(url).netloc.lower()
    for d in ECOMMERCE_DOMAINS:
        if d in net:
            return d
    return net

def buscar_links(driver: webdriver.Chrome, produto: str, max_links=20) -> List[str]:
    query = quote_plus(produto)
    url = f"https://duckduckgo.com/?q={query}&t=h_&ia=web"
    driver.get(url)
    rand_sleep()
    links = []
    items = driver.find_elements(By.CSS_SELECTOR, "a.result__a")
    for i in items:
        href = i.get_attribute("href")
        if any(d in href for d in ECOMMERCE_DOMAINS):
            links.append(href)
        if len(links) >= max_links:
            break
    return links

def extrair_preco(driver: webdriver.Chrome, url: str) -> Optional[float]:
    driver.get(url)
    rand_sleep()
    dom = domain_of(url)
    try:
        if "mercadolivre.com.br" in dom:
            el = driver.find_element(By.CSS_SELECTOR, "span.price-tag-fraction")
            cents_el = driver.find_element(By.CSS_SELECTOR, "span.price-tag-cents")
            preco_text = f"{el.text},{cents_el.text if cents_el else '00'}"
            return normaliza_preco(preco_text)
        if "amazon.com.br" in dom:
            sel = ["#priceblock_ourprice", "#priceblock_dealprice", ".a-price .a-offscreen"]
            for s in sel:
                try:
                    el = driver.find_element(By.CSS_SELECTOR, s)
                    return normaliza_preco(el.text)
                except: continue
        if "americanas.com.br" in dom or "submarino.com.br" in dom:
            el = driver.find_element(By.CSS_SELECTOR, "span#price-value") 
            return normaliza_preco(el.text)
        if "magazineluiza.com.br" in dom or "casasbahia.com.br" in dom:
            el = driver.find_element(By.CSS_SELECTOR, "[data-testid='product-price']")
            return normaliza_preco(el.text)
        if "shopee.com.br" in dom:
            el = driver.find_element(By.CSS_SELECTOR, "meta[property='product:price:amount']")
            return normaliza_preco(el.get_attribute("content"))
    except NoSuchElementException:
        return None
    return None

def buscar_precos(produto: str, top_n=NUM_RESULTS) -> List[Dict]:
    driver = start_driver()
    try:
        links = buscar_links(driver, produto, max_links=50)
        if not links:
            return []
        collected = []
        for link in links:
            preco = extrair_preco(driver, link)
            if preco:
                collected.append({"site": domain_of(link), "link": link, "price": preco})
        collected.sort(key=lambda x: x["price"])
        return collected[:top_n]
    finally:
        driver.quit()

def gerar_html(resultados: List[Dict], filename="comparativo_precos.html"):
    if not resultados:
        html = "<html><body><h2>Nenhum resultado encontrado</h2></body></html>"
        with open(filename, "w", encoding="utf-8") as f: f.write(html)
        return
    menor = min(r["price"] for r in resultados)
    rows_html = ""
    for r in resultados:
        cls = "best" if r["price"] == menor else ""
        price_str = f"R$ {r['price']:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        rows_html += f"<tr class='{cls}'><td>{r['site']}</td><td class='price'>{price_str}</td><td><a href='{r['link']}' target='_blank'>Abrir</a></td></tr>"
    html = f"<html><head><meta charset='utf-8'><title>Comparativo</title></head><body><table><thead><tr><th>Site</th><th>Preço</th><th>Link</th></tr></thead><tbody>{rows_html}</tbody></table></body></html>"
    with open(filename, "w", encoding="utf-8") as f: f.write(html)
    print("HTML salvo em", filename)

def export_csv(resultados: List[Dict], filename="comparativo_precos.csv"):
    if not resultados:
        print("Nenhum resultado para exportar CSV.")
        return
    keys = ["site", "link", "price"]
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for r in resultados: writer.writerow(r)
    print("CSV salvo em", filename)

def main():
    produto = input("Digite o nome do produto a buscar: ").strip()
    if not produto:
        print("Produto vazio. Abortando.")
        return
    resultados = buscar_precos(produto)
    if not resultados:
        print("Nenhum preço encontrado.")
        return
    for r in resultados:
        print(f"{r['site']}: R$ {r['price']:.2f} | {r['link']}")
    gerar_html(resultados)
    export_csv(resultados)

if __name__ == "__main__":
    main()
