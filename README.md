# 🥊 UFC Fight Notifier

Welcome to the **UFC Fight Notifier**! This script allows you to receive email notifications about UFC events, such as when a specific fight is about to start or has ended. It uses web scraping to get real-time data from the UFC website and sends alerts directly to your email.

## 🚀 Features

- Receive notifications before a UFC fight starts.
- Get notified when a specific fight ends.
- Easy setup and configuration.

## 🛠️ Prerequisites

Before using this script, ensure you have the following:

1. **Python 3** installed. 🐍
2. Required packages installed (listed below).
3. A Gmail account for sending notifications. Refer to this tutorial for help setting up a Gmail account: [YouTube tutorial](https://youtu.be/g_j6ILT-X0k).

## 📦 Installation

1. Clone the repository or copy the script to your local machine.
2. Install the necessary Python packages using pip:

   ```sh
   git clone https://github.com/garantf/UFC-Notifier.git
   cd UFC-Notifier/
   pip install -r requirements.txt
   ```

3. Edit the `creds.py` file containing your email credentials:

   ```python
   email_user = "your_email@example.com"
   email_password2 = "your_app_password"
   email_receiver = "receiver_email@example.com"
   ```

   **Note**:

   - `email_user` is the email that will send the notifications.
   - `email_password` is the [App Password](https://support.google.com/accounts/answer/185833) for your Gmail account, not your account password.
   - To receive SMS notifications instead of an email, check your mobile provider's email-to-SMS gateway. For more information, visit [this website](https://email2sms.info/).

> ⚠️ **Important**: The script uses Gmail's SMTP server for sending emails. Ensure you have [App Passwords](https://support.google.com/accounts/answer/185833) enabled on your Google account.

## 📝 Usage Instructions

Follow these steps to use the UFC Fight Notifier:

1. **Run the script**:

   ```sh
   python3 main.py
   ```

2. **Enter Event and Fight Information**:

   - When prompted, enter the UFC event number (e.g., for UFC 280, enter "280").
   - Enter the fight order number you wish to be notified about (e.g., "1" for the main event).

3. **Set Notification Duration**:

   - Enter the number of hours for which the script should keep checking for updates.

4. **Receive Notifications**:

   - The script will notify you before a fight starts and after it ends. 🎉

## ⚠️ Error Handling

- If an error occurs while sending the email, an error message will be printed in the console.
- Make sure the UFC event number is correct, or the script won't be able to fetch fight details.

## 🔒 Security Notes

- Store your credentials (`creds.py`) securely. **Do not share** your email or password publicly.
- To avoid exposing your credentials, consider using environment variables or a secure vault.

## 🛑 Stopping the Script

- You can stop the script at any time by pressing `Ctrl + C`. ⏹️

## 📋 Example

```
 _   _ ______  _____   _   _  _____  _____  _____ ______
| | | ||  ___|/  __ \ | \ | ||  _  ||_   _||_   _||  ___|
| | | || |_   | /  \/ |  \| || | | |  | |    | |  | |_
| | | ||  _|  | |     | . ` || | | |  | |    | |  |  _|
| |_| || |    | \__/\ | |\  |\ \_/ /  | |   _| |_ | |
 \___/ \_|     \____/ \_| \_/ \___/   \_/   \___/ \_|

This program will notify you when a fight has ended.
It will also notify you before a fight starts.
You can interrupt the program at any time by pressing Ctrl+C.

Please enter the UFC event number: 308
Please enter the fight order number (1=main event fight): 1
Enter the duration (in hours) for how long the program should repeat: 10
```

## 🤝 Contributing

Contributions are welcome! Feel free to submit a pull request or open an issue to help improve this project.

## 📄 License

This project is licensed under the MIT License. Feel free to use it in your own projects. 😊

---

**Happy Watching! 🥳**
