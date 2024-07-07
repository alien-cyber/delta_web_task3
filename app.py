from flask import Flask, render_template, request, session, url_for, redirect, jsonify
from flask_cors import CORS
from pymongo import MongoClient


app = Flask(__name__)
app.secret_key = '123456789'  
CORS(app)


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
                session['email']=email
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
        mydoc = likes.find_one(myquery)
        
        if mydoc:
            msg="Email Already Exist"
            
        else:
            msg="Signup Success"
            mydict = { "username": username, "email": email,"password":password }
            likes.insert_one(mydict)

            return redirect(url_for('login'))


 
    return render_template('signup.html',msg=msg)

@app.route('/dashboard', methods=('GET', 'POST'))
def dashboard():
  
    
    


    return render_template('dashboard.html')

@app.route('/like_update', methods=['POST'])
def like_update():
    data = request.get_json()
    url=data['url']
    email=session['email']
    cursor=likes.find_one({'email':email,'url':url})
    if cursor!=None:
        if cursor['count']==1:
            count=0
        else:
            count=1
        myquery = {'email':email,'url':url}
        newvalues = { "$set": { "count": count } }   
        likes.update_one(myquery, newvalues)
    else:
        mydict = { 'email':email, 'url': url,'count':1 }
        likes.insert_one(mydict)
    
    return jsonify({'message': 'Data received successfully'})

@app.route('/get_count', methods=['POST'])
def get_count():
    data = request.get_json()
    email=session['email']
    url=data['url']
    cursor=likes.find({'url':url})
    cursor=list(cursor)
    count=0
    color='grey'
    if cursor:
        for doc in cursor:
            if doc['count']==1:
                count+=1
                if doc['email']==email:
                    color='red'
    
       
       
    return jsonify({'count': count,'color':color})
    


@app.route('/logout')
def logout():
    session.pop('email', None)  
    session.clear() 
    return redirect(url_for('login'))





if __name__ == '__main__':
    app.run(debug=True)