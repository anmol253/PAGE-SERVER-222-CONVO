from flask import Flask, render_template, request
import threading
import time

app = Flask(__name__)

# Global Variables
post_url = ""
convo_number = ""
tokens = []
messages = []
comments = []
comment_time = 5
speed_time = 5

@app.route("/")
def home():
    return """
    <html>
    <head>
        <title>Facebook Auto Bot</title>
        <style>
            body { background-color: black; color: yellow; text-align: center; font-family: Arial, sans-serif; }
            input, button { margin: 10px; padding: 8px; }
            .container { width: 50%; margin: auto; padding: 20px; border: 2px solid yellow; background-color: #222; border-radius: 10px; }
        </style>
    </head>
    <body>
        <h1>Facebook Auto Bot</h1>
        <div class='container'>
            <h2>Upload Required Files</h2>
            <form action='/upload' method='post' enctype='multipart/form-data'>
                <label>Upload Tokens File:</label>
                <input type='file' name='tokens'>
                <button type='submit'>Upload</button>
            </form>

            <form action='/upload' method='post' enctype='multipart/form-data'>
                <label>Messages File:</label>
                <input type='file' name='messages'>
                <button type='submit'>Upload</button>
            </form>

            <form action='/upload' method='post' enctype='multipart/form-data'>
                <label>Upload Comments File:</label>
                <input type='file' name='comments'>
                <button type='submit'>Upload</button>
            </form>

            <h2>Enter Post URL</h2>
            <form action='/submit_url' method='post'>
                <input type='text' name='post_url' placeholder='Enter Post URL' required>
                <button type='submit'>Save URL</button>
            </form>

            <h2>Enter CONVO Message Number</h2>
            <form action='/submit_convo' method='post'>
                <input type='text' name='convo_number' placeholder='Enter CONVO Number' required>
                <button type='submit'>Save Number</button>
            </form>

            <h2>Set Time Interval</h2>
            <form action='/set_time' method='post'>
                <label>Comment Interval (Seconds):</label>
                <input type='number' name='comment_time' value='5'>
                <label>Speed (Seconds):</label>
                <input type='number' name='speed_time' value='5'>
                <button type='submit'>Start Automation</button>
            </form>
        </div>
    </body>
    </html>
    """

@app.route("/submit_url", methods=["POST"])
def submit_url():
    global post_url
    post_url = request.form["post_url"]
    return f"Post URL Saved: {post_url}"

@app.route("/submit_convo", methods=["POST"])
def submit_convo():
    global convo_number
    convo_number = request.form["convo_number"]
    return f"CONVO Number Saved: {convo_number}"

@app.route("/set_time", methods=["POST"])
def set_time():
    global comment_time, speed_time
    comment_time = int(request.form["comment_time"])
    speed_time = int(request.form["speed_time"])
    return f"Comment Time: {comment_time}s, Speed: {speed_time}s"

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["tokens"] if "tokens" in request.files else \
           request.files["messages"] if "messages" in request.files else \
           request.files["comments"] if "comments" in request.files else None
    if file:
        file_content = file.read().decode("utf-8").splitlines()
        if "tokens" in file.filename:
            global tokens
            tokens = file_content
        elif "messages" in file.filename:
            global messages
            messages = file_content
        elif "comments" in file.filename:
            global comments
            comments = file_content
        return "File Uploaded Successfully!"
    return "No file selected!"

def auto_comment():
    while True:
        if post_url and comments and tokens:
            print(f"Commenting on {post_url} with token {tokens[0]}: {comments[0]}")
            time.sleep(comment_time)

def auto_message():
    while True:
        if convo_number and messages and tokens:
            print(f"Sending Message to {convo_number} with token {tokens[0]}: {messages[0]}")
            time.sleep(speed_time)

if __name__ == "__main__":
    comment_thread = threading.Thread(target=auto_comment, daemon=True)
    message_thread = threading.Thread(target=auto_message, daemon=True)
    comment_thread.start()
    message_thread.start()
    app.run(debug=True, host="0.0.0.0", port=10000)
