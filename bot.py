import requests
from playwright.sync_api import sync_playwright

NTFY_TOPIC = "ps5-bot"

# Sostituisci questi link con gli URL veri delle pagine della PS5 Slim Digital
SITI = {
    "Unieuro": "https://www.unieuro.it/online/INCOLLA-QUI-LINK-PS5",
    "PlayStation Direct": "https://direct.playstation.com/it-it/INCOLLA-QUI-LINK-PS5",
    "MediaWorld": "https://www.mediaworld.it/it/product/INCOLLA-QUI-LINK-PS5",
}

PAROLE_DISPONIBILE = ["aggiungi al carrello", "acquista ora", "aggiungi"]
PAROLE_ESAURITO = ["non disponibile", "esaurito", "attualmente non disponibile", "avvisami"]


def manda_notifica(negozio, url):
    requests.post(
        f"https://ntfy.sh/{NTFY_TOPIC}",
        data=f"PS5 disponibile su {negozio}!\n{url}".encode("utf-8"),
        headers={
            "Title": f"PS5 IN STOCK - {negozio}",
            "Priority": "urgent",
            "Click": url,
        },
        timeout=15,
    )


def controlla_siti():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            locale="it-IT",
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
        )
        page = context.new_page()

        for negozio, url in SITI.items():
            try:
                print(f"Controllo {negozio}...")
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                page.wait_for_timeout(4000)

                testo = page.inner_text("body").lower()

                ha_tasto_acquisto = any(k in testo for k in PAROLE_DISPONIBILE)
                e_esaurito = any(k in testo for k in PAROLE_ESAURITO)

                if ha_tasto_acquisto and not e_esaurito:
                    print(f"TROVATA su {negozio}!")
                    manda_notifica(negozio, url)
                else:
                    print(f"Niente su {negozio} (ancora esaurita o bloccata).")
            except Exception as e:
                print(f"Errore su {negozio}: {e}")

        browser.close()


if __name__ == "__main__":
    controlla_siti()
