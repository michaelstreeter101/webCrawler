# Author: MWS
# Purpose: index page: https://portal.london.edu/http://reflector.london.edu/portalpage
# and get (among other links): https://portal.london.edu/http://reflector.london.edu/portalpage?contentPage=/mamba/portalIndex/base.jsp&treeName=Telephone&pageName=Telephone+List&source=mainMenu

#Configuration before first run:
#cd C:\Users\mstreeter\Development
#.\venv\Scripts\activate
#pip install selenium
#cd C:\Users\mstreeter\Development\Python\web_crawler_v1
#python -m idlelib.idle
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from selenium.common.exceptions import UnexpectedAlertPresentException
import ast

visited_urls = set()
visited_url_count = 1
queue = []

# Define a function to log in.
def login():
    user_id = input("User Id: ")
    user_password = input("Password: ")
    print("\n"*20) # Clear terminal screen and pause to continue...
    print("\n"*20)
    print("\n"*20)
    x = input("Press [Enter]")
    
    browser = webdriver.Firefox()
    browser.get("https://portal.london.edu/http://reflector.london.edu/portalpage")
    time.sleep(8)
    
    illDoIt = browser.find_element(By.CSS_SELECTOR, "#owInviteCancel")
    illDoIt.click()
    time.sleep(2)

    cookies = browser.find_element(By.CSS_SELECTOR, "#onetrust-pc-btn-handler")
    cookies.click()
    time.sleep(1)

    reject = browser.find_element(By.CSS_SELECTOR, ".ot-pc-refuse-all-handler")
    reject.click()
    time.sleep(1)

    login = browser.find_element(By.CSS_SELECTOR, "div.sublayout:nth-child(3) > div:nth-child(1) > div:nth-child(1) > div:nth-child(2) > section:nth-child(1) > div:nth-child(1) > p:nth-child(11) > a:nth-child(1)")
    login.click()
    time.sleep(8)

    signIn = browser.find_element(By.CSS_SELECTOR, "#i0116")
    signIn.send_keys(user_id)

    next = browser.find_element(By.CSS_SELECTOR, "#idSIButton9")
    next.click()
    time.sleep(3)

    password = browser.find_element(By.CSS_SELECTOR, "#i0118")
    password.send_keys(user_password)

    signIn = browser.find_element(By.CSS_SELECTOR, "html body.cb.remove-segoe-ui-symbol div form#i0281.provide-min-height div.login-paginated-page div#lightboxTemplateContainer.provide-min-height div.outer div.template-section.main-section div.middle.ext-middle div.full-height div.flex-column div.win-scroll div#lightbox.sign-in-box.ext-sign-in-box.fade-in-lightbox div div div.pagination-view.animate.has-identity-banner.slide-in-next div div.password-reset-links-container.ext-password-reset-links-container div.win-button-pin-bottom.boilerplate-button-bottom div.row.move-buttons div div.col-xs-24.no-padding-left-right.button-container.button-field-container.ext-button-field-container div.inline-block.button-item.ext-button-item input#idSIButton9.win-button.button_primary.button.ext-button.primary.ext-primary")
    signIn.click()

    #myElem = WebDriverWait(browser, 60).until(EC.presence_of_element_located((By.ID, 'document.querySelector("welcome_user")')))
    time.sleep(30)
    
    # At this point (after I approve sign in) we should be logged in.
    # NB: could use this to start from a node in a deep subtree: browser.get("https://portal.london.edu/http://reflector.london.edu/portalpage?forwardAzureAD=true")
    queue.append([browser.current_url, "Portal", browser.current_url])
    return browser

# Function to save a list and a set to a file
def save_to_file(queue, visited_urls, file_path):
    # Tidy up queue first
    for url in visited_urls:
        while queue.count(url) > 0:
             queue.remove(url)

    print(f"Visited URLs: {len(visited_urls)}")
    print(f"Pages to visit: {len(queue)}")
    
    with open(file_path, "w") as file:
        # Save queue as a list
        file.write(",".join(map(str, queue)))
        file.write("\n")
        
        # Save visited_urls as a set
        file.write(",".join(map(str, visited_urls)))

# Function to load a list and a set from a file
def load_from_file(file_path):
    global queue
    global visited_urls
    global visited_url_count
    
    with open(file_path, "r") as file:
        # Load queue as a list
        queue_data = file.readline().strip()
        queue = ast.literal_eval("["+queue_data+"]")
        
        # Load visited_urls as a set
        visited_urls_data = file.readline().strip()
        visited_urls = set(visited_urls_data.split(","))

    visited_url_count = len(visited_urls)
    #print(f"load_from_file: {visited_urls=}")

# Function to grow queue
def gather_links(browser):

    url = browser.current_url

    #print(browser.page_source)
    soup = BeautifulSoup(browser.page_source, 'html.parser')

    for link in soup.find_all('a', href=True):
        absolute_link = urljoin(url, link['href'])  # Use urljoin to construct absolute URLs
        netloc = urlparse(absolute_link).netloc
        if "portal" in netloc:
            if absolute_link not in visited_urls:
                queue.append([url, link.text, absolute_link])

    #print(f"{queue=}")
def message(count, link, note, csv):
    print(f"{count}, {link[0]}, {link[1]}, {link[2]}, {note}")
    csv.write(f"{count}, {link[0]}, {link[1]}, {link[2]}, {note}\n")

# Function to grow visited_links and shrink queue
def crawl(browser, pages, crawl_delay):
    global visited_url_count
    load_from_file('current_state.txt')
    max_pages = visited_url_count+pages
    csv = open("crawl"+str(visited_url_count)+".csv", "w")

    message("Page URN", ["Origin", "Link text", "href"], "Note", csv)
    while queue and visited_url_count < max_pages:
        link2 = queue.pop(0)
        url = link2[2][:]
        if url in visited_urls:
            continue

        visited_urls.add(url)
        #print(f"crawl: {visited_url_count} Crawling: {url}")
        try:
            browser.get(url)
            visited_url_count += 1
            time.sleep(crawl_delay)
            if "404 Not Found" in browser.page_source or "500 Internal Server Error" in browser.page_source:
                message(visited_url_count, link2, f"Content Error on {url} 404/500", csv)
                #print(f"Page: {link2[0]} Link text: {link2[1]}")
                #print(f"Content Error on {url} 404/500")
                #print("")
            else:
                message(visited_url_count, link2, "OK", csv)
                #soup = BeautifulSoup(browser.page_source, 'html.parser')
                #portal_div = soup.find("div", {"id": "portalcontent"})
                #if portal_div is None or not portal_div.text.strip():
                #    print(f"Page: {link2[0]} Link text: {link2[1]}")
                #    print("The div with id='portalcontent' is empty.")
                #    print("")
                gather_links(browser)
                #print(f"crawl: Queue length = {len(queue)}")
                #print()

        except UnexpectedAlertPresentException as e:
            message(visited_url_count, link2, f"UnexpectedAlertPresentException: {e}", csv)
            #print(f"UnexpectedAlertPresentException on {url}: {e}")
    save_to_file(queue, visited_urls, 'current_state.txt')
    csv.close()

browser = login()
crawl(browser, pages=15, crawl_delay=4)
