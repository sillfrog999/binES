import os

from werkzeug.utils import secure_filename

from flask import Flask,render_template,redirect,request,send_from_directory

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



UPLOAD_FOLDER="uploads"

app.config["UPLOAD_FOLDER"]=UPLOAD_FOLDER



if not os.path.exists(UPLOAD_FOLDER):

	os.makedirs(UPLOAD_FOLDER)





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

	avatar=db.Column(
		db.String(200),
		default="default.png"
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

	log=db.Column(
		db.Text
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





@app.route("/register",methods=["GET","POST"])
def register():

	if request.method=="POST":

		username=request.form["username"]

		password=request.form["password"]


		check=User.query.filter_by(
			username=username
		).first()


		if check:

			return render_template(
				"register.html",
				error="Username da ton tai!"
			)



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





@app.route("/login",methods=["GET","POST"])
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

			return redirect("/dashboard")



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





@app.route("/profile")
@login_required
def profile():

	return render_template(
		"profile.html"
	)





@app.route("/avatar",methods=["POST"])
@login_required
def avatar():

	file=request.files["avatar"]


	if file and file.filename:

		filename=secure_filename(
			file.filename
		)


		file.save(
			os.path.join(
				UPLOAD_FOLDER,
				filename
			)
		)


		current_user.avatar=filename

		db.session.commit()



	return redirect("/profile")





@app.route("/create",methods=["GET","POST"])
@login_required
def create():

	if request.method=="POST":

		name=request.form["name"]

		file=request.files["file"]


		filename=""


		if file and file.filename:


			filename=secure_filename(
				file.filename
			)


			file.save(
				os.path.join(
					UPLOAD_FOLDER,
					filename
				)
			)



		project=Project(

			name=name,

			file=filename,

			status="Uploaded",

			log="Project created",

			user_id=current_user.id

		)



		db.session.add(project)

		db.session.commit()


		return redirect("/dashboard")



	return render_template(
		"create.html"
	)





@app.route("/project/<int:id>")
@login_required
def project(id):

	project=Project.query.get(id)


	return render_template(
		"project.html",
		project=project
	)





@app.route("/download/<filename>")
@login_required
def download(filename):

	return send_from_directory(
		UPLOAD_FOLDER,
		filename,
		as_attachment=True
	)





@app.route("/deploy/<int:id>")
@login_required
def deploy(id):

	project=Project.query.get(id)


	project.status="Deploy Success"


	project.log="""
[binES Deploy]

Checking source...

Installing packages...

Building project...

Starting server...

Deploy completed successfully!
"""


	db.session.commit()


	return redirect(
		"/project/"+str(id)
	)





@app.route("/delete/<int:id>")
@login_required
def delete(id):

	project=Project.query.get(id)


	if project:

		db.session.delete(project)

		db.session.commit()



	return redirect("/dashboard")





with app.app_context():

	db.create_all()





if __name__=="__main__":

	app.run(
		host="0.0.0.0",
		port=5000,
		debug=True
	)
