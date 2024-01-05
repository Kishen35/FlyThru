import client # client.py
import item # item.py
import order # order.py
import openAIspeech

import time
from flask import Flask, render_template, request, url_for, redirect, session, send_file, flash, send_from_directory, jsonify
#from flask_cors import CORS

app = Flask(__name__)
#CORS(app)
app.config['SECRET_KEY'] = 'flythru'

@app.route('/', methods=["GET", "POST"])
def home():
    return render_template("index.html")

@app.route('/initiate_order')
def initiate_order():
    # create order id and ready system for order taking
    session['order_id'] = order.create_order(session['clientEmail'])
    openAIspeech.intialize(session['clientEmail'], session['order_id'])
    return redirect(url_for("ordering"))
    
@app.route('/ordering')
def ordering():
    return render_template("index.html")

@app.route('/ready_order')
def ready_order():
    openAIspeech.chat_with_open_ai()

@app.route('/end_order')
def end_order():
    # Get JSON data from the request
    session['order_id'] = None
    openAIspeech.loop = False
    return redirect(url_for("home"))

@app.route('/update_display')
def update_display():
    return order.update_display(session['clientEmail'], session['order_id'])


@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        name = request.form.get('name')

        if client.create_account(email, password, name) == 0:
            return redirect(url_for("home"))
        else:
            return render_template("register.html", email_exists=True)

    return render_template("register.html")


@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get('email')
        password = request.form.get('password')
        
        login = client.login(email, password)
        if login != 1:
            session['logged_in'] = True
            session['clientEmail'] = email
            session['clientName'] = login.get("clientName") # function returns name
            session['merchant_id'] = login.get("merchant_id") # function returns id
            return redirect(url_for("home"))
        else:
            return render_template("login.html", not_found=True)
        
    return render_template("login.html")

@app.route('/account')
def account():
    return render_template("account.html")

@app.route('/updateAccount', methods=["POST"])
def updateAccount():
    password = request.form.get('password')
    name = request.form.get('name')
    client.update_account(session['clientEmail'], password, name)
    return redirect(url_for("logout"))

@app.route('/logout')
def logout():
    session.pop("logged_in", None)
    session.pop("clientEmail", None)
    session.pop("clientName", None)
    session.pop("merchant_id", None)
    return redirect(url_for("home"))


@app.route('/getMenu', methods=["POST"])
def getMenu():
    merchant_id = request.form.get('merchant_id')
    id = item.get_menu(session['clientEmail'], merchant_id)
    if id == 1: # invalid id
        return render_template("account.html", invalid_id=True)

    client.update_merchantid(id, session['clientEmail'])
    session['merchant_id'] = id
    return redirect(url_for("home"))

@app.route('/merchant_id')
def merchant_id():
    return send_file("templates\merchant_id.png", mimetype='image/gif')

@app.route('/icon/<path:filename>')
def icon(filename):
    return send_from_directory(directory="../assets/favicon_io", path=filename)

if __name__ == "__main__":
    app.run(debug=True)

    # {% for chat in session['conversation'] %}

    #   {% if chat['role'] == 'assistant': %}
    #   <div class="message received">
    #       <p>{{ chat['content'] }}</p>
    #       <span class="time">Assistant</span>
    #   </div>

    #   {% elif chat['role'] == "user": %}
    #   <div class="message sent">
    #       <p>{{ chat['content'] }}</p>
    #       <span class="time">Customer</span>
    #   </div>
    #   {% endif %}

    # {% endfor %}