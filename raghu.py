from flask import Flask, request, render_template_string
import os
import threading
import time
import requests
import random

app = Flask(__name__)

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

TOKEN_FILE = os.path.join(DATA_DIR, "tokens.txt")
MESSAGE_FILE = os.path.join(DATA_DIR, "messages.txt")
COMMENT_FILE = os.path.join(DATA_DIR, "comments.txt")
TIME_MSG_FILE = os.path.join(DATA_DIR, "time_msg.txt")
TIME_CMT_FILE = os.path.join(DATA_DIR, "time_cmt.txt")
POST_URL_FILE = os.path.join(DATA_DIR, "post_url.txt")
GROUP_FILE = os.path.join(DATA_DIR, "group_number.txt")

# Save uploaded files
def save_file(file, path):
    with open(path, "wb") as f:
        f.write(file.read())

# Function to check if token is valid
def is_token_valid(token):
    url = "https://graph.facebook.com/me?access_token=" + token
    response = requests.get(url)
    return response.status_code == 200

# Function to send messages
def send_messages():
    while True:
        try:
            with open(TOKEN_FILE, "r") as f:
                tokens = [line.strip() for line in f.readlines() if line.strip()]

            with open(MESSAGE_FILE, "r") as f:
                messages = [line.strip() for line in f.readlines() if line.strip()]

            with open(GROUP_FILE, "r") as f:
                group_numbers = [line.strip() for line in f.readlines() if line.strip()]

            with open(TIME_MSG_FILE, "r") as f:
                delay_msg = int(f.read().strip())

            if not (tokens and messages and group_numbers):
                print("[!] Missing files data.")
                return

            while True:
                for token in tokens:
                    if is_token_valid(token):  # Check if token is valid before sending
                        for group in group_numbers:
                            for message in messages:
                                url = f"https://graph.facebook.com/{group}/messages"
                                payload = {'access_token': token, 'message': message}
                                headers = {'User-Agent': 'Mozilla/5.0'}
                                response = requests.post(url, json=payload, headers=headers)

                                if response.ok:
                                    print(f"[+] Message sent to {group}: {message}")
                                else:
                                    print(f"[x] Failed: {response.status_code} {response.text}")

                                time.sleep(delay_msg + random.randint(2, 5))  # Random delay
        except Exception as e:
            print(f"[!] Error: {e}")
        time.sleep(30)  # Retry every 30 seconds

# Function to post comments
def post_comments():
    while True:
        try:
            with open(TOKEN_FILE, "r") as f:
                tokens = [line.strip() for line in f.readlines() if line.strip()]

            with open(COMMENT_FILE, "r") as f:
                comments = [line.strip() for line in f.readlines() if line.strip()]

            with open(POST_URL_FILE, "r") as f:
                post_urls = [line.strip() for line in f.readlines() if line.strip()]

            with open(TIME_CMT_FILE, "r") as f:
                delay_cmt = int(f.read().strip())

            if not (tokens and comments and post_urls):
                print("[!] Missing files data.")
                return

            while True:
                for token in tokens:
                    if is_token_valid(token):  # Check if token is valid before commenting
                        for post_url in post_urls:
                            for comment in comments:
                                url = f"https://graph.facebook.com/{post_url}/comments"
                                payload = {'access_token': token, 'message': comment}
                                headers = {'User-Agent': 'Mozilla/5.0'}
                                response = requests.post(url, json=payload, headers=headers)

                                if response.ok:
                                    print(f"[+] Comment posted on {post_url}: {comment}")
                                else:
                                    print(f"[x] Failed: {response.status_code} {response.text}")

                                time.sleep(delay_cmt + random.randint(2, 5))  # Random delay
        except Exception as e:
            print(f"[!] Error: {e}")
        time.sleep(30)  # Retry every 30 seconds

# Auto Restart Every Hour
def auto_restart():
    while True:
        time.sleep(3600)  # Restart every hour
        os.execv(__file__, ["python"] + sys.argv)

threading.Thread(target=auto_restart, daemon=True).start()

# HTML Interface
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Facebook Auto Bot</title>
    <style>
        body { background-color: black; color: white; font-family: Arial, sans-serif; text-align: center; }
        .container { background: #222; max-width: 400px; margin: 50px auto; padding: 20px; border-radius: 10px; }
        h1 { color: #ffcc00; }
        input, button { padding: 10px; border-radius: 5px; margin-bottom: 10px; }
        button { background-color: #ffcc00; color: black; border: none; cursor: pointer; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Facebook Auto Bot</h1>
        <form action="/" method="post" enctype="multipart/form-data">
            <label>Upload Tokens File:</label>
            <input type="file" name="token_file" required>
            <label>Upload Messages File:</label>
            <input type="file" name="message_file" required>
            <label>Upload Comments File:</label>
            <input type="file" name="comment_file" required>
            <label>Upload Post URLs File:</label>
            <input type="file" name="post_url_file" required>
            <label>Upload Group Numbers File:</label>
            <input type="file" name="group_file" required>
            <label>Message Speed (Seconds):</label>
            <input type="number" name="delay_msg" value="5" min="1">
            <label>Comment Speed (Seconds):</label>
            <input type="number" name="delay_cmt" value="5" min="1">
            <button type="submit">Start Automation</button>
        </form>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        files = {"token_file": TOKEN_FILE, "message_file": MESSAGE_FILE, "comment_file": COMMENT_FILE, "post_url_file": POST_URL_FILE, "group_file": GROUP_FILE}
        for field, path in files.items():
            file = request.files.get(field)
            if file:
                save_file(file, path)

        threading.Thread(target=send_messages, daemon=True).start()
        threading.Thread(target=post_comments, daemon=True).start()

    return render_template_string(HTML_TEMPLATE)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=10000)
