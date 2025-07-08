import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging
import time
import urllib.robotparser
import random
from datetime import datetime
import re

logging.basicConfig(filename="scrapper.log", level=logging.INFO)

def check_robots_txt():
    """Check robots.txt compliance"""
    try:
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url("https://www.flipkart.com/robots.txt")
        rp.read()
        
        # Check if we can fetch search pages
        can_fetch = rp.can_fetch("*", "https://www.flipkart.com/search")
        if not can_fetch:
            print("Warning: robots.txt may not allow scraping")
            return False
        return True
    except Exception as e:
        logging.warning(f"Could not check robots.txt: {e}")
        return True  # Proceed with caution

def rate_limited_request(url, delay=3, retries=5):
    for attempt in range(retries):
        try:
            time.sleep(delay + random.uniform(2, 3))
            response = uReq(url)
            return response
        except Exception as e:
            if "HTTP Error 429" in str(e):
                wait_time = 2 ** (attempt + 1)
                print(f"⚠️ Too Many Requests - waiting {wait_time}s before retrying...")
                time.sleep(wait_time)
            else:
                raise e
    raise Exception("❌ Failed after multiple retries due to rate limiting.")



def scrape_flipkart_reviews(search_string):
    try:
        # Check robots.txt compliance
        if not check_robots_txt():
            print("Scraping may not be allowed by robots.txt")
            user_input = input("Continue anyway? (y/n): ")
            if user_input.lower() != 'y':
                return []

        print("✓ Robots.txt compliance checked")

        # Clean search string
        search_string_cleaned = search_string.replace(" ", "")
        print(f"Searching for: {search_string_cleaned}")
        flipkart_url = "https://www.flipkart.com/search?q=" + search_string_cleaned
        print(f"Fetching URL: {flipkart_url}")

        print("Fetching product search results...")

        # Get product page with rate limiting
        url_client = rate_limited_request(flipkart_url)
        flipkart_page = url_client.read()
        url_client.close()
        flipkart_html = bs(flipkart_page, "html.parser")

        # Handle dynamic content - wait a bit for page to load
        time.sleep(5)

        # Find products with multiple selectors for better reliability
        all_product = flipkart_html.find_all("div", {"class": "cPHDOP col-12-12"})
        
        print(f"Found {len(all_product)} products on the page")
        if not all_product:
            # Try alternative selector
            all_product = flipkart_html.find_all("div", {"class": "_1AtVbE col-12-12"})
        
        # if len(all_product) > 2:
        #     del all_product[0:2]
        first_product = all_product[1] 
        # print(first_product)
        
        if not first_product:
            logging.error("No products found")
            return []

        # Get product link
        product_partial_link = first_product.div.div.div.a['href']
        # product_anchor = first_product.find("a", href=True)

        # if product_anchor:
        #     product_partial_link = product_anchor['href']
        # else:
        #     logging.error("❌ Product link not found in first_product")
        #     return []

        
        product_link = "https://www.flipkart.com" + product_partial_link
        # print(f"✓ Found product link: {product_link}")

        # Extract product ID from link
        try:
            product_id = product_partial_link.split("/p/")[1].split("?")[0]
        except:
            product_id = "Not Found"
            logging.info("Product ID not found")

        print(f"✓ Found product: {product_id}")
        print("Fetching product details...")

        product_client = rate_limited_request(product_link)
        product_page = product_client.read()
        product_client.close()
        product_html = bs(product_page, "html.parser")

        # Get actual product name
        try:
            product_name_element = product_html.find("span", class_="VU-ZEz")  # New Flipkart product title class
            if not product_name_element:
                product_name_element = product_html.find("span", class_="B_NuCI")  # Old class fallback
            product_name = product_name_element.text.strip() if product_name_element else "Unknown Product"
        except Exception as e:
            product_name = "Unknown Product"
            logging.info(f"Product name not found: {e}")

        print(f"✓ Found product name: {product_name}")


        # Handle dynamic content
        time.sleep(2)

        import re

# instead of scoping to review_link_element, just search globally under product_html:
        link = product_html.find(
            "a",
            href=re.compile(r"/product-reviews/")
        )

        if link:
            review_href = link["href"]
            print(f"✓ Found review link: {review_href}")
        else:
            logging.error("Review link not found")


        # Get review page link with fallback selectors
        review_link_element = product_html.find("div", {"class":"col pPAw9M"})
        if not review_link_element:
            # Try alternative selector
            review_link_element = product_html.find("a", string=lambda text: text and "reviews" in text.lower())
        
        if not review_link_element or not review_link_element.a:
            logging.error("Review link not found")
            return []
        
        # print(f"✓ Found review link: {review_link_element.a['href']}")

        print("✓ Found review section")
        print("Fetching reviews...")

        # first_review_page_link = "https://www.flipkart.com" + review_link_element.a["href"]
        first_review_page_link = "https://www.flipkart.com" + review_href
        first_review_page_client = rate_limited_request(first_review_page_link)
        first_review_page = first_review_page_client.read()
        first_review_page_client.close()
        first_review_page_html = bs(first_review_page, "html.parser")

        # Handle dynamic content for reviews
        time.sleep(2)

        # Get review page links with better pagination handling
        nav_element = first_review_page_html.find("nav", class_="WSL9JP")
        if not nav_element:
            # Try alternative pagination selector
            nav_element = first_review_page_html.find("div", class_="yFHi8N")
        
        review_page_links = []
        if nav_element:
            review_page_all_anchors = nav_element.find_all("a")
            for i in review_page_all_anchors:
                review_page_links.append("https://www.flipkart.com" + i["href"])
        else:
            # If no pagination, just use current page
            review_page_links = [first_review_page_link]

        # Modify review page links
        for i in range(len(review_page_links)):
            idx = review_page_links[i].find("aid")
            if idx != -1:
                review_page_links[i] = review_page_links[i][:idx] + f"aid=overall&certifiedBuyer=true&sortOrder=MOST_RECENT&page={i+1}"

        del review_page_links[15:]  # only keep first 500 pages

        print(f"✓ Found {len(review_page_links)} review pages to scrape")

        # Create CSV file with timestamp
        filename = "review_temp.csv"

        file_exists = False
        try:
            with open(filename, "r", encoding='utf-8') as fr:
                file_exists = True
        except FileNotFoundError:
            file_exists = False

        fw = open(filename, "a", encoding='utf-8')
        if not file_exists:
            headers = "Product Name, Product ID, Review Text, Review Rating, Reviewer Verified\n"
            fw.write(headers)


        reviews = []
        total_scraped = 0

        # Scrape reviews with rate limiting
                # Scrape reviews with rate limiting
        for page_num, link in enumerate(review_page_links, 1):
            print(f"Scraping page {page_num}/{len(review_page_links)}...")

            review_client = rate_limited_request(link)
            review_page = review_client.read()
            review_client.close()
            review_html = bs(review_page, "html.parser")

            time.sleep(1)

            all_reviews = review_html.find_all("div", {"class": "col EPCmJX Ma1fCG"})
            if not all_reviews:
                all_reviews = review_html.find_all("div", {"class": "_27M-vq"})

            page_reviews = 0
            for review in all_reviews:
                try:
                    verified_tag = review.find("p", class_="MztJPv").text
                    verified = "Yes" if "Certified Buyer" in verified_tag else "No"
                except:
                    verified = "Unknown"
                    logging.info("Verified Purchase status not found")

                try:
                    rating_element = review.find("div", class_=lambda x: x and 'XQDdHH' in x and 'Ga3i8K' in x)
                    rating = rating_element.text.strip() if rating_element else 'No Rating'
                except Exception as e:
                    rating = 'No Rating'
                    logging.info(f"Rating extraction failed: {e}")

                try:
                    comment_element = review.find("div", class_="ZmyHeo")
                    if comment_element:
                        comment_text = comment_element.text
                        cust_comment = comment_text.split("READ MORE")[0] if "READ MORE" in comment_text else comment_text
                    else:
                        cust_comment = 'No Comment'
                except Exception as e:
                    cust_comment = 'No Comment'
                    logging.info(f"comment not found: {e}")

                mydict = {
                    "Product Name": product_name.split(",")[0].strip(),
                    "Product ID": product_id,
                    "Review Text": cust_comment,
                    "Review Rating": rating,
                    "Reviewer Verified": verified,
                }
                reviews.append(mydict)
                page_reviews += 1

                data = f"{mydict['Product Name']}, {mydict['Product ID']}, {mydict['Review Text']}, {mydict['Review Rating']}, {mydict['Reviewer Verified']}\n"
                fw.write(data)

            print(f"✓ Scraped {page_reviews} reviews from page {page_num}")
            total_scraped += page_reviews


        fw.close()
        logging.info("Scraping completed successfully")
        
        print(f"\n✓ Scraping completed! Found {total_scraped} reviews.")
        print(f"✓ Data saved to: {filename}")
        
        return reviews

    except Exception as e:
        logging.info(f"Error occurred: {e}")
        print(f"Something went wrong: {e}")
        return []


def main():
    print("Flipkart Review Scraper")
    print("-" * 30)

    search_term = input("Enter product name to search: ")

    if not search_term.strip():
        print("Please enter a valid product name.")
        return

    print(f"\n🔎 Searching for: {search_term}")
    print("⏳ Starting compliant scraping process...")

    reviews = scrape_flipkart_reviews(search_term)

    if not reviews:
        print("No reviews found or an error occurred.")

if __name__ == "__main__":
    main()