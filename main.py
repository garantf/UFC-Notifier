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
        cookies = {'STYXKEY_region': 'CANADA_FRENCH.CA.fr-ca.QUEBEC'}
        headers = {
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
            'cache-control': 'max-age=0',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36',
        }

        response = requests.get('https://www.ufc.com/event/ufc-' + event_number, cookies=cookies, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        script_tag = soup.find('script', {'type': 'application/json', 'data-drupal-selector': 'drupal-settings-json'})
        if script_tag:
            data = json.loads(script_tag.string)
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

def fetch_data(fight_id):
    try:
        url = f"https://d29dxerjsp82wz.cloudfront.net/api/v3/event/live/{fight_id}.json"
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Failed to retrieve the webpage. Status code: {response.status_code} Error: {e}")
        return None

def read_file(filename):
    if os.path.exists(filename) and os.path.getsize(filename) > 0:
        try:
            with open(filename, "r", encoding='utf-8') as f:
                saved_data_str = f.read()
                old_data = json.loads(saved_data_str)
            return old_data
        except Exception as e:
            print(f"Error reading file: {e}")
    return None

def save_data(data):
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving file: {e}")

def compare_data(old, new):
    if old != new:
        save_data(new)
        print("Data has changed, updating file.")
        return True
    return False


# ✅ Corrected check_for_changes()
def check_for_changes(fight_to_be_notified, new_data):
    fight_card = new_data.get("LiveEventDetail", {}).get("FightCard", [])
    
    # ✅ Completed fights summary
    completed_fights = []
    for fight in fight_card:
        if fight.get("Status") == "Final":
            red = fight["Fighters"][0]["Name"]["FirstName"] + " " + fight["Fighters"][0]["Name"]["LastName"]
            blue = fight["Fighters"][1]["Name"]["FirstName"] + " " + fight["Fighters"][1]["Name"]["LastName"]
            winner = next((f for f in fight["Fighters"] if f["Outcome"]["Outcome"] == "Win"), None)
            loser = next((f for f in fight["Fighters"] if f["Outcome"]["Outcome"] == "Loss"), None)
            if winner and loser:
                method = fight["Result"].get("Method", "Unknown")
                round_num = fight["Result"].get("EndingRound", "?")
                time_ended = fight["Result"].get("EndingTime", "?")
                submission = fight["Result"].get("EndingSubmission")
                method_detail = f"{method} ({submission})" if submission else method
                completed_fights.append(
                    f"{winner['Name']['FirstName']} {winner['Name']['LastName']} def. "
                    f"{loser['Name']['FirstName']} {loser['Name']['LastName']} "
                    f"via {method_detail} in Round {round_num} ({time_ended})"
                )

    if completed_fights:
        print("\n✅ Completed fights so far:")
        for result in completed_fights:
            print("  -", result)
        print()

    # ✅ Accurate “fights left” count (includes current fight)
    target = int(fight_to_be_notified)
    not_done_statuses = {"Upcoming", "Live"}
    remaining_fights = [
        f for f in fight_card
        if f.get("Status") in not_done_statuses
        and isinstance(f.get("FightOrder"), int)
        and f["FightOrder"] >= target
    ]

    total_remaining = len(remaining_fights)
    if total_remaining > 0:
        print(f"⏳ {total_remaining-1} fight(s) remaining including the current fight until your selected fight.\n")
    else:
        print("🔥 Your selected fight may be live or next!\n")

    # ✅ Notify when the fight BEFORE the selected one ends
    for fight in fight_card:
        if fight.get("FightOrder") == target + 1 and fight.get("Status") == "Final":
            print("🎯 Previous fight just ended — your fight is next!")
            send_email(email_body_2)


def main(fight_id, fight_to_be_notified):
    if fight_id:
        new_data = fetch_data(fight_id)
        if new_data:
            old_data = read_file(filename)
            if compare_data(old_data, new_data):
                check_for_changes(fight_to_be_notified, new_data)

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

        print("**If left empty, the program will automatically check today's UFC Fight Night.**")
        print("**Otherwise, for a specific event, enter the event number (e.g., 300).**\n")

        event_number = input("Please enter the UFC event number or leave blank for today's Fight Night: ").strip()

        # ✅ Auto-handle today's Fight Night if left blank
        if not event_number:
            today = datetime.now()
            event_number = f"fight-night-{today.strftime('%B').lower()}-{today.strftime('%d')}-{today.strftime('%Y')}"
            print(f"Auto-selected event: {event_number}")

        fight_to_be_notified = input("Please enter the fight order number (1 = main event fight): ")
        fight_to_be_notified = int(fight_to_be_notified) 
        fight_to_be_notified = str(fight_to_be_notified)

        repeat_duration = float(input("Enter duration (in hours) to run the program: "))
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
