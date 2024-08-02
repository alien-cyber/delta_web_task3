from flask import Flask, render_template, request, session, url_for, redirect, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from dotenv import load_dotenv,find_dotenv
import os
import hashlib
import jwt
import datetime

from functools import wraps

load_dotenv(find_dotenv())
app = Flask(__name__)

app.secret_key =  os.urandom(12)
CORS(app)

 
mongo_url=os.getenv("mongo_url")
client = MongoClient(mongo_url)
db = client.flask_db
db.users.insert_one({"dummy": "data"})
db.users.delete_one({"dummy": "data"})
db.likes.insert_one({"dummy": "data"})
db.likes.delete_one({"dummy": "data"})
db.playlists.insert_one({"dummy": "data"})
db.playlists.delete_one({"dummy": "data"})
db.playlists_name.insert_one({"dummy": "data"})
db.playlists_name.delete_one({"dummy": "data"})
users = db.users
likes = db.likes
playlists = db.playlists
playlists_name=db.playlists_name






def token_required(func):
   
    @wraps(func)
    def decorated(*args, **kwargs):
        
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        try:
            token=session['token']
            data = jwt.decode(token, app.secret_key, algorithms=["HS256"])
        except:
             return redirect(url_for('login'))
        return func(*args, **kwargs)
    return decorated



@app.route('/', methods=('GET', 'POST'))
def login():

    

    msg="Login"
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        myquery = { "email": email }
        mydoc = users.find_one(myquery)
   
        if mydoc:
            try:
                stored_password=mydoc['password']
                salt=stored_password[:32]
                stored_hash = stored_password[32:]
                hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
            except:
                    msg="Invalid crediential"
                    return render_template('login.html',msg=msg)

            
            if stored_hash==hashed_password:
                session['email']=email
    
                
                token = jwt.encode({'email':email,'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)}, app.secret_key, algorithm="HS256")
                session['logged_in']=True
                session['token']=token
                
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
        salt=os.urandom(32)
        hashed_password = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, 100000)
        username = request.form['username']
        myquery = { "email": email }
        mydoc = users.find_one(myquery)
        
        if mydoc:
            msg="Email Already Exist"
            
        else:
            msg="Signup Success"
            mydict = { "username": username, "email": email,"password":salt+hashed_password }
            users.insert_one(mydict)

            return redirect(url_for('login'))


 
    return render_template('signup.html',msg=msg)

@app.route('/dashboard', methods=('GET', 'POST'))
@token_required
def dashboard():

    return render_template('dashboard.html')

@app.route('/like_update', methods=['POST'])
def like_update():
   
    data = request.get_json()
    url=data['url']
    email=session['email']
    img=data['image']
    name=data['name']
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
        mydict = { 'email':email, 'url': url,'count':1,'image':img,'songname':name }
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
    session.pop('token', None)
    session.pop('logged_in', None)  

    
    session.clear() 
    return redirect(url_for('login'))


@app.route('/playlist')
@token_required
def playlist():

    return render_template('playlist.html')


@app.route('/create_playlist', methods=['POST'])
def create_playlist():

    data = request.get_json()
    email=session['email']
    name = data['c_playlist']
    img=data['upload_image']
    mydict = { "name": name, "email": email,"image":img,'duration':0 }
    playlists_name.insert_one(mydict)
  
    return jsonify({'message':'got it'})


@app.route('/get_names', methods=['POST'])
def get_names():
    data = request.get_json()
    email=session['email']
    query={'email':email}
    names_cursor = playlists_name.distinct('name',query)
    names = list(names_cursor)

   
    for name in names:
        if '_id' in name:
            name['_id'] = str(name['_id'])

  
    return jsonify({'names':names})

@app.route('/add_song', methods=['POST'])
def add_song():
    email=session['email']
  
 
    selected_playlists =  request.get_json()
   
    url=selected_playlists['url']
    img_url=selected_playlists['img']
    songname=selected_playlists['name']
   



    for name in selected_playlists:
        if name!='url':
            if name!='img':
                if name!='name':
                    if name!='duration':
                        query={'email':email,'name':name}
                        names_cursor = playlists_name.find(query)
                        duration=list(names_cursor)[0]['duration']+int(selected_playlists['duration'])
                        print("duration:",duration)
                        newvalues = { "$set": { "duration": duration } }
                        playlists_name.update_one(query, newvalues)
                        myquery = {'email':email,'url':url,'image':img_url,'playlist_name':name,'songname':songname}
                        playlists.insert_one(myquery)
                
   

    
    return jsonify({'message':'got it'})



@app.route('/get_playlists', methods=['POST'])
def get_playlists():
 
    email=session['email']
    query={'email':email}
    names_cursor = playlists_name.find(query)
    names = list(names_cursor)
    duplicate=[]
    filtered=[]

    for name in names:
        if '_id' in name:
            name['_id'] = str(name['_id'])
        if name['name'] not in duplicate:
            duplicate.append(name['name'])
            filtered.append(name)
            
    
  
    return jsonify({'names':filtered})

@app.route('/get_songs', methods=['POST'])
def get_songs():
    data = request.get_json()
   
  
    session['songname']=data['songname']


    return jsonify({'message':'got it'})

    
@app.route('/play_songs', methods=('GET', 'POST'))
@token_required
def play_songs():
    return render_template('playlist_songs.html')



@app.route('/songs', methods=['POST'])
def songs():
    email=session['email']
    name=session['songname']
    if name=='liked_songs':
        cursor=likes.find({'email':email,'count':1})
        img=''
        filtered=list(cursor)
        for doc in filtered:
            if '_id' in doc:
                doc['_id'] = str(doc['_id'])
        print(filtered)
    else:
        image_cursor=playlists_name.find_one({'email':email,'name':name})
        img=image_cursor['image']
        query={'email':email,'playlist_name':name}
        cursor=playlists.find(query)
        cursor=list(cursor)
        duplicate=[]
        filtered=[]
        for doc in cursor:
            if '_id' in doc:
                doc['_id'] = str(doc['_id'])
            if doc['songname'] not in duplicate:
                duplicate.append(doc['songname'])
                filtered.append(doc)
    
    return jsonify({'cursor':filtered,'name':name,'image':img})






if __name__ == '__main__':
    app.run(debug=True)
