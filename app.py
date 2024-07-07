from flask import Flask, render_template, request, session, url_for, redirect

from pymongo import MongoClient


app = Flask(__name__)
app.secret_key = '123456789'  


client = MongoClient('mongodb://localhost/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.2.10')
db = client.flask_db
db.users.insert_one({"dummy": "data"})
db.users.delete_one({"dummy": "data"})
db.likes.insert_one({"dummy": "data"})
db.likes.delete_one({"dummy": "data"})
db.playlists.insert_one({"dummy": "data"})
db.playlists.delete_one({"dummy": "data"})
users = db.users
likes = db.likes
playlists = db.playlists




@app.route('/', methods=('GET', 'POST'))
def login():
    msg="Login"
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        myquery = { "email": email }
        mydoc = users.find_one(myquery)
        print('Password')
        print(mydoc)
        if mydoc:
            if password==mydoc['password']:
                return redirect(url_for('dashboard'))
            else:
                msg="Incorrect Password"
        else:
            msg="Email does not exist "


    return render_template('login.html',msg=msg)


@app.route('/signup', methods=('GET', 'POST'))
def signup():
    msg="Signup"
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        username = request.form['username']
        myquery = { "email": email }
        mydoc = users.find_one(myquery)
        
        if mydoc:
            msg="Email Already Exist"
            
        else:
            msg="Signup Success"
            mydict = { "username": username, "email": email,"password":password }
            users.insert_one(mydict)

            return redirect(url_for('login'))


 
    return render_template('signup.html',msg=msg)

@app.route('/dashboard', methods=('GET', 'POST'))
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)