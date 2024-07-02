from bs4 import BeautifulSoup
import pandas as pd
import re
import urllib.request

# Fully Functional Google Search Extractor in less than 100lines of code
def get_html(url):
    request = urllib.request.Request(url)    # Perform the request
    # Set a normal User Agent header, otherwise Google will block the request.
    request.add_header('User-Agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36')
    raw_response = urllib.request.urlopen(request).read()

    html = raw_response.decode("utf-8")    # Read the response as a utf-8 string
    return html

def update_google_search_url(base_url, page_number):
    page_number = int(page_number)
    start_index = (page_number - 1) * 10
    if 'start=' not in base_url:    # Check if the start parameter is in the URL, if not add it
        if '?' in base_url:
            updated_url = f"{base_url}&start={start_index}"
        else:
            updated_url = f"{base_url}?start={start_index}"
    else:
        updated_url = re.sub(r"start=\d+", f"start={start_index}", base_url)
    return updated_url

def scrape_google_results(site, role, location, pg = 1):
    url = f'https://www.google.com/search?q=site:{site}.com+"{role}"+"{location}"' #My personal favourite
    # url = f'https://www.google.com/search?q=site:{site}.com+"{role}"+"{location}"+"@gmail.com"' #Code adds .com and @gmail.com by default if not needed remove it
    # url = f'https://www.google.com/search?q=site:{siteurl}+"{role}"+"{location}"' #Can use this for general search 
    divs = []
    for i in range(1, int(pg)+1):
        url = update_google_search_url(url, i)
        html = get_html(url)        # Get the HTML contents
        soup = BeautifulSoup(html, 'html.parser')        # Parse the HTML using BeautifulSoup
        divs += soup.select("#search div.g")        # Find all the search result divs
    divs = list(set(divs))  # Remove duplicates
    return divs

def data_table(divs):
    product = []
    for div in divs:
        # Search for a h3 tag
        results = div.select("h3")
        # Check if we have found a result
        if len(results) >= 1:
            # Print the title
            tempTitle = results[0].get_text()
            for link in div.find_all('a', href=True):
                tempLink = link['href']
                product.append({'Name': tempTitle, 'Link': tempLink})
    df = pd.DataFrame(product)
    df = df.sort_values('Name')  # Sort the dataframe by 'Name' column
    return df

def main():
    print("This script searches google for a specific role in a specific location on a specific website and returns the results")
    print("Enter the website you want to search for: ")
    print("Options\t1: Linkedin\t2: Facebook\t3: Instagram\tOthers:Enter Site name")
    site = input()
    if site == "1":
        site = "Linkedin"
    elif site == "2":
        site = "Facebook"
    elif site == "3":
        site = "Instagram"
    else:
        site = site.replace(" ", "+")
    print("Enter the role you want to search for: ")
    print("Options\t1: CEO\t2: CTO\t3: Marketer\t4: HR\t5:Software Engineer\t6: Developer\tOthers:Enter Role name")
    role = input()
    if role == "1":
        role = "CEO"
    elif role == "2":
        role = "CTO"
    elif role == "3":
        role = "Marketer"
    elif role == "4":
        role = "HR"
    elif role == "5":
        role = "Software+Engineer"
    elif role == "6":
        role = "Developer"
    else:
        role = role.replace(" ", "+")

    print("Enter the location you want to search for: ")
    location = input()
    location = location.replace(" ", "+")
    print("Enter no of pages you want to scrape (NOTE:High no has more chances of ban from google I recommend keep it less than 5): ")
    pgNo = input()

    divs = scrape_google_results(site, role, location, pgNo) # All the search results in a div list
    df = (data_table(divs))
    df['Hyperlink'] = df.apply(lambda x: f'=HYPERLINK("{x["Link"]}", "{x["Name"]}")', axis=1)
    df[['Hyperlink']].to_csv('google_search.csv', mode='a', header=False, index=False)
    print("Results saved to google_search.csv")

if __name__ == "__main__":
    main()