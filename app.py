from utils import MongoDb, ImageDownloard, SeleniumScraper
import time, re, logging
import hashlib

TARGET_URL = "https://www2.hm.com/fr_fr/femme/nouveautes/view-all.html"


def generate_product_id(title, image_url):
    """Crée un identifiant unique basé sur le titre et l'image."""
    key = f"{title}_{image_url}"
    return hashlib.md5(key.encode('utf-8')).hexdigest()

def parse_article_card(card):
    """
    Parse un WebElement Selenium représentant un produit et retourne un dictionnaire.
    """
    try:
        # Titre XPath exact
        title_elem = card.find_element("xpath", ".//div[2]/div/div/a/h2")
        title = title_elem.text.strip() if title_elem else ""

        # Prix XPath exact
        price_elem = card.find_element("xpath", ".//div[2]/div/div/p/span")
        price = price_elem.text.strip() if price_elem else ""

        # Image XPath (span avec style background-image)
        img_span = card.find_element("xpath", ".//div[1]/div[1]/a/div/div/span")
        style = img_span.get_attribute("style") if img_span else ""
        image_url = ""
        try:
            img_span = card.find_element("xpath", ".//div[1]/div[1]/a/div/div/span")
            style = img_span.get_attribute("style")
            if style and "url(" in style:
                image_url = style.split("url(")[1].split(")")[0].replace("'", "").replace('"', '')
            else:
                # Vérifier s'il y a un <img> dans le span
                img_tag = img_span.find_element("tag name", "img")
                image_url = img_tag.get_attribute("src")
        except:
            image_url = ""

        # Génération d'un product_id
        product_id = generate_product_id(title, image_url)
        return {
            "product_id": product_id,
            "title": title,
            "price": price,
            "image_url": image_url
        }

    except Exception as e:
        logging.error(f"Error parsing article card: {e}")
        return None
    
def main():
    mongo = MongoDb()
    downloader = ImageDownloard()
    scraper = SeleniumScraper(headless=True)

    try:
        scraper.driver.get(TARGET_URL)
        time.sleep(5)

        page = 1
        while True:
            print(f"\n--- Page {page} ---")
            product_cards = scraper.driver.find_elements(
                "xpath", '//*[@id="products-listing-section"]/ul/li'
            )
            print(f"Nombre de produits trouvés sur la page: {len(product_cards)}")

            for card in product_cards:
                product = parse_article_card(card)
                if not product:
                    continue

                print("Produit parsé:", product)
                filename_hint = product["product_id"]
                product["image_path"] = downloader.download(product["image_url"], filename_hint)
                mongo.insertproduct(product)
                time.sleep(0.3)

            # Tenter de cliquer sur le bouton "Suivant"
            try:
                next_button = scraper.driver.find_element(
                    "xpath", '//*[@id="products-listing-section"]/div[2]/div/button'
                )

                # Vérifier si le bouton est désactivé
                if "disabled" in next_button.get_attribute("class"):
                    print("🚫 Dernière page atteinte.")
                    break

                # Faire défiler jusqu'au bouton et cliquer
                scraper.driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                time.sleep(1)
                scraper.driver.execute_script("arguments[0].click();", next_button)
                time.sleep(5)  # attendre le chargement des nouveaux produits
                page += 1

            except Exception as e:
                print("⚠️ Pas de bouton suivant trouvé :", e)
                break

        print("✅ Scraping terminé et toutes les pages ont été traitées.")

    except Exception as e:
        logging.error(f"Erreur de scraping : {e}")

    finally:
        scraper.close()


if __name__ == "__main__":
    main()