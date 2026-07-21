import os
from werkzeug.utils import secure_filename
from flask import Flask,render_template,redirect,request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager,UserMixin,login_user,logout_user,current_user,login_required
from werkzeug.security import generate_password_hash,check_password_hash

app=Flask(__name__)

app.config["SECRET_KEY"]="bines"

app.config["SQLALCHEMY_DATABASE_URI"]="sqlite:///bines.db"


db=SQLAlchemy(app)


login=LoginManager()

login.init_app(app)

login.login_view="login"



class User(db.Model,UserMixin):

	id=db.Column(
		db.Integer,
		primary_key=True
	)

	username=db.Column(
		db.String(50),
		unique=True
	)

	password=db.Column(
		db.String(200)
	)

class Project(db.Model):

	id=db.Column(
		db.Integer,
		primary_key=True
	)

	name=db.Column(
		db.String(100)
	)

	file=db.Column(
		db.String(200)
	)

	status=db.Column(
		db.String(50)
	)

	user_id=db.Column(
		db.Integer
	)

@login.user_loader
def load_user(id):

	return User.query.get(int(id))



@app.route("/")
def home():

	return render_template(
		"index.html"
	)



@app.route(
	"/register",
	methods=["GET","POST"]
)

def register():

	if request.method=="POST":

		username=request.form["username"]

		password=request.form["password"]


		user=User(
			username=username,
			password=generate_password_hash(password)
		)


		db.session.add(user)

		db.session.commit()


		return redirect("/login")


	return render_template(
		"register.html"
	)



@app.route(
	"/login",
	methods=["GET","POST"]
)

def login():


	if request.method=="POST":

		username=request.form["username"]

		password=request.form["password"]


		user=User.query.filter_by(
			username=username
		).first()



		if user and check_password_hash(
			user.password,
			password
		):

			login_user(user)

			return redirect(
				"/dashboard"
			)



	return render_template(
		"login.html"
	)



@app.route("/logout")
def logout():

	logout_user()

	return redirect("/")



@app.route("/dashboard")
@login_required
def dashboard():

	projects=Project.query.filter_by(
		user_id=current_user.id
	).all()


	return render_template(
		"dashboard.html",
		projects=projects
	)



with app.app_context():

	db.create_all()


if __name__=="__main__":

	app.run(
		host="0.0.0.0",
		port=5000,
		debug=True
	)
@app.route("/create",methods=["GET","POST"])
@login_required
def create():

	if request.method=="POST":

		name=request.form["name"]

		file=request.files["file"]

		filename=""

		if file:

			filename=secure_filename(
				file.filename
			)

			file.save(
				"uploads/"+filename
			)


		project=Project(

			name=name,

			file=filename,

			status="Uploaded",

			user_id=current_user.id
		)


		db.session.add(project)

		db.session.commit()


		return redirect("/dashboard")


	return render_template(
		"create.html"
	)
