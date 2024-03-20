from __future__ import division
import requests
import re
import random
import math
import nltk
import os
from bs4 import BeautifulSoup
import urllib.request
from urllib.error import URLError
from urllib.parse import unquote, urlparse, parse_qs
from rake_nltk import Rake
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk import word_tokenize
from collections import Counter
from random import randint

def dict_search(dict, searchTerm):
    for k in dict:
        if searchTerm in k:
            return True
    return False

def get_search_results(query, num_results):
    # Replace spaces in query with '+'
    formatted_query = '+'.join(query.split())

    # Google search URL
    search_url = f"https://www.google.com/search?q={formatted_query}"
    headers = {"User-Agent": "Mozilla/5.0"}

    # Perform the Google search
    response = requests.get(search_url, headers=headers)

    # Parse the search results
    soup = BeautifulSoup(response.text, 'html.parser')
    search_items = soup.find_all('a')

    # Dictionary to hold search results
    search_results = {}

    # Counter for the number of results added
    results_count = 0

    # Fetch top 10 search result URLs
    for item in search_items:
        link = item.get('href')
        if link and '/url?q=' in link:
            actual_url = parse_qs(urlparse(link).query).get('q')
            if actual_url:
                # Extract the URL and decode it
                actual_url = unquote(actual_url[0])
                if "maps.google.com" not in actual_url and "support.google.com" not in actual_url and "accounts.google.com" not in actual_url: # Avoid Google Maps
                    temp = actual_url.split("/")
                    temp2 = ""
                    if len(temp) > 2:
                        temp2 = temp[2]
                        # print(temp2)
                    if actual_url not in search_results and not dict_search(search_results, temp2):  # Avoid duplicates
                        if results_count < num_results:  # Limit to top 10 results
                            try:
                                result_response = requests.get(actual_url, headers=headers, timeout=5)
                                result_content = result_response.text

                                # Add the result to the dictionary
                                search_results[actual_url] = result_content
                                results_count += 1
                            except Exception as e:
                                continue
                        else:
                            break

    return search_results

def extract_text_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    # kill all script and style elements
    for script in soup(["script", "style"]):
        script.extract()  # rip it out
    # get text
    text = soup.get_text()
    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split())
    # drop blank lines
    text = '\n'.join(chunk for chunk in chunks if chunk)
    return text

def mix_sample(query, keywords):
    result = ""
    num_words = randint(3,6)
    if len(keywords) > num_words:
        result = ' '.join(random.sample(keywords, num_words))
    else:
        # mix with term database 2:1
        num_webpage = num_words - math.floor(num_words / 3)
        num_dict = num_words - num_webpage
        result = ' '.join(random.sample(keywords, num_webpage)) + ' '.join(random.sample(query, num_dict))
    return result

def generate_fake_query(original_query, query_dict):
    r = Rake()
    fake_queries = []
    for query in query_dict:
        webpage = query_dict[query]
        html_text = extract_text_from_html(webpage)
        r.extract_keywords_from_text(html_text)
        key_words = r.get_ranked_phrases()
        cleaned_keywords = []
        for word in key_words:
            new_word = re.sub(r'[^\w\s]', '', word.lower())
            if (len(new_word) < 15) and (new_word not in stopwords.words('english')) and (len(new_word) > 1) and (not any(char.isdigit() for char in new_word)):
                cleaned_keywords.append(new_word.strip().replace('  ',' '))
        result = mix_sample(original_query, cleaned_keywords)   
        fake_queries.append(result) 
    return fake_queries
    
if __name__ == "__main__":
    nltk.download('stopwords')
    nltk.download('punkt')
    os.system('cls' if os.name == 'nt' else 'clear')

    query = input("Enter your search query: ")
    num_results = input("Up to how many results to return: ")
    results = get_search_results(query, int(num_results))
    for url, content in results.items():
        print(url)
    list_query = list(query.split(" "))
    print(generate_fake_query(list_query, results))
