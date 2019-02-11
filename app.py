from flask import Flask, request, render_template, flash, redirect, url_for, session
import sqlite3
from wtforms import Form, StringField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)
app.debug = True


@app.route('/')
def index():
	return render_template('index.html')


@app.route('/dashboard')
def dashboard():
	return render_template('dashboard.html')


# register form class
class RegisterForm(Form):
	name = StringField('Name', [validators.Length(min=1, max=50)])
	# username = StringField('Username', [validators.Length(min=4, max=25)])
	email = StringField('Email', [validators.Length(min=6, max=50)])
	password = PasswordField('Password', [
		validators.DataRequired(),
		validators.EqualTo('confirm', message='Password do not match')
	])
	confirm = PasswordField('Confirm Password')


# user register
@app.route('/register', methods=['GET', 'POST'])
def register():
	form = RegisterForm(request.form)
	if request.method == 'POST' and form.validate():
		name = form.name.data
		email = form.email.data
		# username = form.username.data
		password = sha256_crypt.encrypt(str(form.password.data))

		connection = sqlite3.connect('test.db')
		cursor = connection.cursor()
		cursor.execute("INSERT INTO users(name,email,password) VALUES('"+name+"','"+email+"','"+password+"')")
		connection.commit()
		connection.close()

		flash('You are now registered and can log in', 'success')

		return redirect(url_for('index'))       

	return render_template('register.html', form=form)


# User Login
@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		email = request.form['email']
		password_candidate = request.form['password']

		connection = sqlite3.connect('test.db')
		cursor = connection.cursor()
		result = cursor.execute("SELECT * FROM users WHERE email = '"+email+"'")
		if result.arraysize > 0:
			data = cursor.fetchone()
			password = data[2
			]
			if sha256_crypt.verify(password_candidate, password):
				app.logger.info('PASSWORD MATCHED')
				session['logged_in'] = True
				session['email'] = email

				flash('You are now logged in', 'success')

				return redirect(url_for('dashboard'))

			else:
				app.logger.info('PASSWORD NOT MATCHED')
				error = 'Incorrect Password'
				return render_template('login.html', error=error)

			cursor.close()
		else:
			app.logger.info('NO USER')
			error = 'Username not found'
			return render_template('login.html', error=error)

	return render_template('login.html')


# check if user is logged in
def is_logged_in(f):
	@wraps(f)
	def wrap(*args, **kwargs):
		if 'logged_in' in session:
			return f(*args, **kwargs)
		else:
			flash('Unauthorized, Please login', 'danger')
			return redirect(url_for('login'))
	return wrap


# logout
@app.route('/logout')
@is_logged_in
def logout():
	session.clear()
	flash('You are now logged out ', 'success')
	return redirect(url_for('login'))


if __name__ == '__main__':
	app.secret_key = "secret123"
	app.run()
