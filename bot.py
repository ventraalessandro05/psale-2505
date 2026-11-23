import requests
from playwright.sync_api import sync_playwright

NTFY_TOPIC = "psale-2505"

SITI = {
    "PS Direct - Slim Digital 30th Anniversary": "https://www.playstation.com/it-it/ps5/playstation-digital-edition-console-model-group-slim/product/30th-anniversary-limited-edition-bundle/",
    "PS Direct - Slim Digital Astro Bot": "https://www.playstation.com/it-it/ps5/playstation-digital-edition-console-model-group-slim/product/astro-bot-bundle/",
    "PS Direct - Slim Digital 2 Controller": "https://www.playstation.com/it-it/ps5/playstation-digital-edition-console-model-group-slim/product/playstation-5-digital-edition-two-dualsense-wireless-controllers-bundle/",
    "PS Direct - Slim Digital Fortnite": "https://www.playstation.com/it-it/ps5/playstation-digital-edition-console-model-group-slim/product/fortnite-cobalt-star-bundle/",
    "PS Direct - Slim Digital Ricondizionata": "https://www.playstation.com/it-it/ps5/certified-refurbished-ps5-slim-digital-edition/product/PSD001-PSDE00234_23-PS5GRADEDDMBTOTE/",
    "PS Direct - PS5 Pro Ricondizionata": "https://www.playstation.com/it-it/ps5/certified-refurbished-playstation-5-pro-console/product/PSD001-PSDE00356_47-RECERTIFIE3YQNSE/",
    "Unieuro - PS5 Slim": "https://www.unieuro.it/online/Console-Playstation-5/Console-PlayStation-5-edizione-gruppo-modello---slim-pidSON1000049741",
    "Unieuro - PS5 Digital Edition": "https://www.unieuro.it/online/Console-Playstation-5/PlayStation-5-Digital-Edition-pidSON1000049749",
    "GameLife - PS5 Slim Digital": "https://www.gamelife.it/hwp50056-playstation-5-slim-digital-edition-e-chassis?attribute_values=4",
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
