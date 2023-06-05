from flask import Flask, render_template, request
from flask_pymongo import PyMongo
from flask import jsonify
from flask_socketio import SocketIO, send
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app)

app.config["MONGO_URI"] = "mongodb+srv://Test:WeatherUlm@weathercluster.zhdkvmz.mongodb.net/?retryWrites=true&w=majority"

mongo = PyMongo(app)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('message')
def handle_message(data):
    pin = data['pin']
    username = data['username']
    message = data['message']

    chatrooms = mongo.cx.Chatroom.Chatroom
    chatroom = chatrooms.find_one({'pin': pin})

    if chatroom is not None:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        new_message = {'username': username, 'text': message, 'timestamp': timestamp}
        chatrooms.update_one({'pin': pin}, {'$push': {'messages': new_message}})

    send(new_message, broadcast=True)

@app.route('/chatroom', methods=['GET', 'POST'])
def chatroom():
    if request.method == 'POST':
        username = request.form.get('username')
        pin = request.form.get('pin')

        chatrooms = mongo.cx.Chatroom.Chatroom
        chatroom = chatrooms.find_one({'pin': pin})

        messages = []

        if chatroom is None:
            chatrooms.insert_one({'pin': pin, 'messages': []})
        else:
            messages = chatroom['messages']

        return render_template('chatroom.html', username=username, pin=pin, messages=messages)
    
if __name__ == '__main__':
    socketio.run(app, debug=True)