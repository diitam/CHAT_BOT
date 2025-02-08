from flask import Flask, render_template, request, jsonify
import openai
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chats.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Set up OpenAI API credentials
openai.api_key = 'your_actual_api_key'

# Database Model for Chat Messages
class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_message = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)

# Create the database tables
with app.app_context():
    db.create_all()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api", methods=["POST"])
def api():
    data = request.json
    message = data.get("message")
    model = data.get("model", "gpt-3.5-turbo")

    # Get response from OpenAI
    completion = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": message}]
    )

    response = completion.choices[0].message["content"]

    # Store the chat in the database
    new_chat = Chat(user_message=message, bot_response=response)
    db.session.add(new_chat)
    db.session.commit()

    return jsonify({"content": response})

@app.route("/history", methods=["GET"])
def get_history():
    chats = Chat.query.all()
    chat_list = [{"user": chat.user_message, "bot": chat.bot_response} for chat in chats]
    return jsonify(chat_list)

if __name__ == '__main__':
    app.run(debug=True)
