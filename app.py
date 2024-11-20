from flask import Flask, render_template, request, jsonify
from datetime import datetime
import uuid

app = Flask(__name__)

messages = []

# Function to get the current time in HH:MM format
def get_current_time():
    return datetime.now().strftime("%H:%M")

# Function to generate a bot response (customize this logic as needed)
def generate_bot_response(user_input):
    return f"Bot received your message: {user_input}"

@app.route('/', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        user_input = request.form['instruction']
        
        # Generate bot's response
        response = generate_bot_response(user_input)
        
        # Store the messages (user and bot)
        id1 = str(uuid.uuid4())
        messages.append({"id": id1, "sender": "user", "text": user_input, "time": get_current_time()})
        id2 = str(uuid.uuid4())
        messages.append({"id": id2, "sender": "start", "text": response, "time": get_current_time()})

        # Check if the request is an AJAX request
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify(messages=messages)  # Return the updated messages as JSON
        
    return render_template('index.html', messages=messages)

if __name__ == '__main__':
    app.run(debug=True)
