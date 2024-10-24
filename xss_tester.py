import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import argparse

# ANSI escape codes for color output
GREEN = '\033[92m'
RED = '\033[91m'
RESET = '\033[0m'

# Function to load payloads from a file
def load_payloads(file_path):
    try:
        with open(file_path, 'r') as f:
            payloads = [line.strip() for line in f if line.strip()]
        return payloads
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return []

# Function to crawl a page and collect forms and input fields
def crawl_and_collect_forms(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        forms = soup.find_all('form')
        return forms
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return []

# Function to test the payloads on input fields
def test_payloads(url, payloads, max_success):
    forms = crawl_and_collect_forms(url)
    success_count = 0
    
    print(f"\nTesting {len(forms)} forms on {url}")
    for i, form in enumerate(forms):
        print(f"\n[*] Testing Form {i + 1}: {form.get('action', url)}")
        
        # Find all input fields in the form
        input_fields = form.find_all('input')
        for payload in payloads:
            for input_field in input_fields:
                field_name = input_field.get('name')
                if field_name:
                    data = {field_name: payload}
                    try:
                        response = requests.post(url, data=data)
                        if payload in response.text:
                            success_count += 1
                            print(f"{GREEN}[+] Potential XSS vulnerability found with payload: {payload} injected into {field_name}{RESET}")
                            
                            # Stop if the maximum number of successes is reached
                            if success_count >= max_success:
                                print(f"\nReached maximum successful injections: {success_count}. Stopping further tests.")
                                return success_count
                        else:
                            print(f"{RED}[-] Payload not successful: {payload}{RESET}")
                    except requests.exceptions.RequestException as e:
                        print(f"Error submitting form: {e}")
    return success_count

# Function to handle DOM-based XSS using Selenium
def test_dom_xss(url, payloads, max_success):
    options = Options()
    options.add_argument("--start-maximized")  # Open the browser in maximized mode
    service = Service('E:/kgsflink_apk/chromedriver-win64/chromedriver.exe')  # Adjust the path as necessary
    driver = webdriver.Chrome(service=service, options=options)
    
    driver.get(url)
    print(f"\nTesting DOM-based XSS on {url}")
    success_count = 0
    
    for payload in payloads:
        try:
            # Inject payload into the page and observe changes
            driver.execute_script(f"document.body.innerHTML += '<script>alert(1);</script>' + '{payload}';")
            time.sleep(2)  # Wait to observe the result
            
            # Check if the payload has executed
            if "alert(1)" in driver.page_source:  # Adjust this check as per your payload
                success_count += 1
                print(f"{GREEN}[+] DOM-based XSS found with payload: {payload}{RESET}")
                
                # Stop if the maximum number of successes is reached
                if success_count >= max_success:
                    print(f"\nReached maximum successful injections: {success_count}. Stopping further tests.")
                    break
            else:
                print(f"{RED}[-] DOM-based XSS not triggered with payload: {payload}{RESET}")
        except Exception as e:
            print(f"Error injecting payload in DOM: {e}")
    
    driver.quit()
    return success_count

# Main function to ask for URL and perform XSS testing
def main():
    parser = argparse.ArgumentParser(description="XSS Testing Tool")
    parser.add_argument('-r', '--max-success', type=int, default=1, help='Maximum number of successful injections before stopping')
    args = parser.parse_args()

    url = input("Enter the URL to test for XSS vulnerabilities: ").strip()
    
    if not url.startswith("http"):
        url = "http://" + url
    
    print(f"\nStarting XSS testing for {url}")
    
    # Load payloads from payload.txt
    payload_file = 'payload.txt'
    payloads = load_payloads(payload_file)
    
    if not payloads:
        print("No payloads found. Exiting.")
        return

    print(f"\nLoaded {len(payloads)} payloads from {payload_file}")
    
    # Test reflected and stored XSS through form injection
    reflected_success = test_payloads(url, payloads, args.max_success)
    
    # Test DOM-based XSS using Selenium
    dom_success = test_dom_xss(url, payloads, args.max_success)

    # Print the total success summary
    total_success = reflected_success + dom_success
    print(f"\nTotal successful XSS injections found: {total_success}")

if __name__ == "__main__":
    main()
