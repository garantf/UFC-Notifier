import requests
import smtplib
import creds
import ssl
import time
from email.message import EmailMessage
import os
import json
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

# Email that sends notification
email_sender = creds.email_user
email_sender_pass = creds.email_password2

# File to store the data
filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fight-data.json")

# Email settings
email_subject = 'UFC UPDATE'
email_body = 'This fighter: %s won by %s in the %s round. \n'
email_body_2 = 'The fight you want to watch is next. Get your popcorn ready. \n'

headers = {
    'accept': '*/*',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'origin': 'https://www.ufc.com',
    'priority': 'u=1, i',
    'referer': 'https://www.ufc.com/',
    'sec-ch-ua': '"Chromium";v="129", "Not=A?Brand";v="8"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Linux"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'cross-site',
    'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
}

def find_fight_id(event_number):
    try:
        # Cookies and headers as provided
        cookies = {
            'STYXKEY_region': 'CANADA_FRENCH.CA.fr-ca.QUEBEC',
        }

        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'cache-control': 'max-age=0',
            'if-modified-since': 'Sat, 05 Oct 2024 16:56:49 GMT',
            'if-none-match': 'W/"1728147409"',
            'priority': 'u=0, i',
            'sec-ch-ua': '"Chromium";v="129", "Not=A?Brand";v="8"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Linux"',
            'sec-fetch-dest': 'document',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-user': '?1',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        }

        # Requesting the webpage
        response = requests.get('https://www.ufc.com/event/ufc-' + event_number, cookies=cookies, headers=headers)

        # Check for request failure
        response.raise_for_status()

        # Parsing the webpage using BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')

        # Finding the JSON script tag
        script_tag = soup.find('script', {'type': 'application/json', 'data-drupal-selector': 'drupal-settings-json'})

        if script_tag:
            # Loading the JSON data
            data = json.loads(script_tag.string)

            # Extracting the event_fmid value
            event_fmid = data.get('eventLiveStats', {}).get('event_fmid')

            if event_fmid:
                print(f"event_fmid: {event_fmid}")
                return event_fmid
            else:
                print("event_fmid not found")
        else:
            print("Script tag not found")
    except requests.RequestException as e:
        print(f"Error fetching fight ID: {e}")

# Send an email function
def send_email(email_body):
    try:
        em = EmailMessage()
        em['From'] = email_sender
        em['To'] = creds.email_receiver
        em['Subject'] = email_subject
        em.set_content(email_body)

        context = ssl.create_default_context()

        with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as smtp:
            smtp.login(email_sender, email_sender_pass)
            smtp.sendmail(email_sender, creds.email_receiver, em.as_string())
    except Exception as e:
        print(f"Error sending email: {e}")

# Fetch data from the given URL
def fetch_data(fight_id):
    try:
        # URL of the site to check
        url = f"https://d29dxerjsp82wz.cloudfront.net/api/v3/event/live/{fight_id}.json"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.RequestException as e:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code} Error: {e}")
        return None

# Read data from the file
def read_file(filename):
    if os.path.exists(filename) and os.path.getsize(filename) > 0:  # Check if the file exists and is not empty
        try:
            with open(filename, "r", encoding='utf-8') as f:
                saved_data_str = f.read()
                old_data = json.loads(saved_data_str)
            return old_data
        except Exception as e:
            print(f"Error reading file: {e}")
    return None

# Save data to the file
def save_data(data):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving file: {e}")

# Compare old and new data, and save if different
def compare_data(old, new):
    if old != new:
        save_data(new)
        print("Data has changed, updating file.")
        return True
    return False

# Check for changes in the fight results and send notifications
def check_for_changes(fight_to_be_notified, new_data):
    fight_card = new_data.get("LiveEventDetail", {}).get("FightCard", [])
    for fight in fight_card:
        if fight.get("FightOrder") == int(fight_to_be_notified):
            if fight.get("Status") == "Final":
                send_email(email_body_2)

# Main function
def main(fight_id, fight_to_be_notified):
    if fight_id:
        new_data = fetch_data(fight_id)
        if new_data:
            old_data = read_file(filename)
            if compare_data(old_data, new_data):
                check_for_changes(fight_to_be_notified, new_data)


# Run the main function
if __name__ == "__main__":
    try:
        print("\033[31m" + """
 _   _ ______  _____   _   _  _____  _____  _____ ______ 
| | | ||  ___|/  __ \ | \ | ||  _  ||_   _||_   _||  ___|
| | | || |_   | /  \/ |  \| || | | |  | |    | |  | |_   
| | | ||  _|  | |     | . ` || | | |  | |    | |  |  _|  
| |_| || |    | \__/\ | |\  |\ \_/ /  | |   _| |_ | |    
 \___/ \_|     \____/ \_| \_/ \___/   \_/   \___/ \_|    
                                                         
""" + "\033[0m")
        print("This program will notify you when a fight has ended.")
        print("It will also notify before a fight starts.")
        print("You can interrupt the program at any time by pressing Ctrl+C.\n")

        event_number = input("Please enter the UFC event number: ")
        fight_to_be_notified = input("Please enter the fight order number (1=main event fight): ")
        fight_to_be_notified = int(fight_to_be_notified)+1
        fight_to_be_notified = str(fight_to_be_notified)
        repeat_duration = float(input("Enter the duration (in hours) for how long the program should repeat: "))
        if repeat_duration <= 0:
            raise ValueError("Duration must be a positive number.")
        end_time = datetime.now() + timedelta(hours=repeat_duration)
        fight_id = find_fight_id(event_number)

        while datetime.now() < end_time:
            main(fight_id, fight_to_be_notified)
            time.sleep(60)
    except ValueError as e:
        print(f"Invalid input: {e}")
    except KeyboardInterrupt:
        print("Program interrupted by the user. Exiting...")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
