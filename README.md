# 🥊 UFC Fight Notifier

Welcome to the **UFC Fight Notifier**!  
This script sends **real-time email notifications** when a UFC fight is about to start or has just ended.  
It automatically tracks fight cards live from the official UFC website and alerts you right before your selected fight begins. 💥

---

## 🚀 Features

- 📨 **Email alerts** when your chosen fight is about to start.  
- 🏁 **Updates when fights end**, including winner, method, and round.  
- 🕒 **Automatic Fight Night detection** — if you leave the event field blank, it finds **today’s UFC Fight Night** automatically.  
- ⚡ **Accurate fight counter**, showing how many fights remain (including the current one).  
- 🔔 **Smart notification** — sends an alert when the *previous fight* ends, so you can get ready in time.

---

## 🛠️ Prerequisites

Make sure you have the following before running the script:

1. **Python 3** installed. 🐍  
2. All required packages (see below).  
3. A Gmail account with [App Passwords](https://support.google.com/accounts/answer/185833) enabled.

---

## 📦 Installation

1. Clone this repository or download the script files:
   ```bash
   git clone https://github.com/garantf/UFC-Notifier.git
   cd UFC-Notifier/
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure your email credentials in `creds.py`:
   ```python
   email_user = "your_email@example.com"
   email_password2 = "your_app_password"
   email_receiver = "receiver_email@example.com"
   ```

> ⚠️ **Tip:**  
> You must use an **App Password**, not your actual Gmail password.  
> Learn how here → [Google App Password Guide](https://support.google.com/accounts/answer/185833)

---

## 📝 Usage Instructions

1. **Run the program:**
   ```bash
   python3 main.py
   ```

2. **Choose the event:**
   - To track a specific UFC numbered event, enter its number (e.g., `300`).  
   - To track **today’s Fight Night**, just **press Enter** — the script will detect it automatically.

3. **Select your fight:**
   - Enter the fight order number (`1` = main event, `2` = co-main, etc.).  
   - The program will notify you **when the previous fight ends**, so you know yours is coming up.

4. **Set runtime duration:**
   - Specify how many hours the program should keep checking for updates.

---

## 🧠 Example

```bash
 _   _ ______  _____   _   _  _____  _____  _____ ______ 
| | | ||  ___|/  __ \ | \ | ||  _  ||_   _||_   _||  ___|
| | | || |_   | /  \/ |  \| || | | |  | |    | |  | |_   
| | | ||  _|  | |     | . ` || | | |  | |    | |  |  _|  
| |_| || |    | \__/\ | |\  |\ \_/ /  | |   _| |_ | |    
 \___/ \_|     \____/ \_| \_/ \___/   \_/   \___/ \_|    

This program will notify you when a fight has ended.
It will also notify before a fight starts.

**If left empty, the program automatically selects today’s Fight Night.**

Please enter the UFC event number or leave blank for today's Fight Night:  
👉 (User presses Enter)
Auto-selected event: fight-night-october-11-2025  

Please enter the fight order number (1=main event fight): 1  
Enter duration (in hours) to run the program: 6
```

Output example:
```
✅ Completed fights so far:
  - Jhonata Diniz def. Mario Pinto via KO in Round 2 (2:45)

⏳ 4 fight(s) remaining including the current fight until your selected fight.

🎯 Previous fight just ended — your fight is next!
```

![IMG_9236](https://github.com/user-attachments/assets/5a6de179-e2a8-4378-9137-a9a4b3d99028)

---

## ⚙️ Error Handling

- If an error occurs while sending emails, you’ll see a message in the console.  
- If the UFC event number is invalid, the script will inform you instead of crashing.  
- Connection or API errors will retry gracefully.

---

## 🔒 Security Notes

- Keep your `creds.py` private — **never share it or upload it publicly**.  
- You may use environment variables or a `.env` file for improved security.

---

## 🛑 Stopping the Script

Press `Ctrl + C` at any time to safely exit. ⏹️

---

## 🤝 Contributing

Contributions are welcome!  
Open an issue or submit a pull request if you’d like to add new features (like Telegram or Discord alerts).

---

## 📄 License

This project is licensed under the **MIT License**.  
Feel free to fork and modify for personal use.

---

**👊 Stay ready — never miss the walkout again! 🥳**
