from flask import Flask, request, jsonify
import time
app = Flask(__name__)

@app.route('/message', methods=['POST'])
def handle_message():
    data = request.get_json()
    message = data.get('message')

    # Process the message and prepare the response
    response_message = f"Received message: '{message}'. This is the backend responding!"
    #time.sleep(5)
    return jsonify({'response': response_message})

if __name__ == "__main__":
    app.run(port=5001)
