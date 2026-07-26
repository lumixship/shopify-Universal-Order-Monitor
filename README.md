What is it used for?
Universal Order Monitor is a cross-platform desktop and mobile application built with Python, Kivy, and KivyMD 🖥️📱.

What is it used for?
It is specifically designed for online store owners and e-commerce sellers (Shopify, WooCommerce, etc.) who want to track their sales in real-time without constantly refreshing their inbox or opening dashboards.

Automated Background Surveillance 🔄: It securely connects to your Gmail inbox via the IMAP protocol and continuously monitors for new unread order confirmation emails containing keywords like "order" or "commande".

Smart Data Extraction (Parsing) 🧠: As soon as a sale drops in, the app uses BeautifulSoup and regular expressions (re) to automatically pull out the most important details:

🔢 Order Number

👤 Customer Name

🛍️ Total Items Quantity

💰 Total Price & Currency

Sleek Modern UI 🌙: Every new order pops up instantly as a gorgeous visual card inside a clean Dark Mode Material Design interface, keeping you instantly notified second by second.

🛠️ 3. Installation Help (Step-by-Step Guide)
Follow these simple steps to install and run the program on your machine:

Step 1: Prerequisites 💻
Make sure you have Python (version 3.8 or higher) installed on your computer.

Step 2: Download the Code 📥
Download or clone the source code file (e.g., main.py) into a dedicated folder on your computer.

Step 3: Install Dependencies 📦
Open your terminal (Command Prompt, PowerShell, or Terminal on Mac/Linux), navigate to your project folder, and run the following command to install the required libraries:

Bash
[pip install kivymd beautifulsoup4]
(Note: Core modules like imaplib, email, threading, and re come pre-installed natively with Python).

Step 4: Set up a Gmail App Password 🔐
For security reasons, Google blocks standard password access for external apps. You need to generate a dedicated App Password:

Go to your Google Account settings and head to the Security tab.

Ensure 2-Step Verification is turned on.

Search for and open App Passwords (at the bottom of the security page).

Enter a custom name (e.g., Universal Order Monitor) and click Generate.

Copy the 16-character code provided.

Step 5: Run the Application ▶️
Execute the script from your terminal:

Bash
python app.py

How to use it inside the app:
Enter your Gmail address.

Paste your 16-character App Password (do not use your regular Google password).

Click the START MONITORING button and watch your live sales roll in! 🎉
