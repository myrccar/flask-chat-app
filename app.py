from flask import Flask,render_template,redirect,request,url_for
from flask_login import LoginManager, login_required, login_user, UserMixin,logout_user,current_user
from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
import os,json


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'asenfe'
socket = SocketIO(app)



lm = LoginManager()
lm.init_app(app)
db = SQLAlchemy(app=app)


class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))
    
    def __init__(self, username, password):
        self.username = username
        self.password = password
    def __repr__(self):
        return '<User %r>' % self.username


@lm.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@lm.unauthorized_handler
def unauthorized_callback():
    return redirect('/login')

   
@app.route('/')
@login_required
def chat():
    return render_template("index.html",username=current_user.username)

@app.route('/login',methods =["GET", "POST"])
def login():
    #if fourm data, try to login
    if request.method == "POST":
        user = User.query.filter_by(username=request.form.get("username","")).first()
        if user == None:
            return render_template("login.html",error="invaled username")
        if user.password == request.form.get("password",""):
            login_user(user=user)
            return redirect("/")
        else:
            return render_template("login.html",error="invaled password")
    #if no fourm data, just render html
    return render_template("login.html")

@app.route("/signup",methods =["GET", "POST"])
def signup():
    #if fourm data, try to signup
    if request.method == "POST":
        user = User.query.filter_by(username=request.form.get("username","")).first()
        if user is None:
            user = User(request.form.get("username",""),request.form.get("password",""))
            db.session.add(user)
            db.session.commit()
            login_user(user)
            return redirect("/")
        else:
            return render_template("signup.html",error="username taken")
    else:
        return render_template("signup.html",error="")
    #if not, just render html
    return render_template("signup.html")

@app.route('/logout')
@login_required
def logout():
    #logs out current user and brings them to the login page
    logout_user()
    return redirect("/login")

@socket.on("new_message_client")
def new_message(data):
    print(data)
    socket.emit('new_message_server',data)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    print("app starting(LAN)...")
    print("open http://192.168.1.109:5000/ to view")
    print("running with flask_socketio")
    print("press ctrl+c to quit")
    socket.run(app=app,host='0.0.0.0', port=5000)