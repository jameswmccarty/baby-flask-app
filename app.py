from flask import Flask, render_template, json, request, session, redirect, url_for
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_USER'] = 'babyflask'
app.config['MYSQL_PASSWORD'] = 'place_mysql_password_here_after_install'
app.config['MYSQL_DB'] = 'babytracker'
app.config['MYSQL_HOST'] = 'localhost'
mysql = MySQL(app)

app.secret_key = 'place_app_secret_here_after_install'

@app.route('/')
def main():
	return render_template('index.html')


@app.route('/signup')
def showSignUp():
	return render_template('signup.html')


@app.route('/signin')
def showSignin():
	return render_template('signin.html')

@app.route('/success/<msg>')
def success(msg):
	return render_template('success.html', message=str(msg))

@app.route('/error/<err>')
def error(err):
	return render_template('error.html', error=str(err))

@app.route('/api/validateLogin', methods=['POST'])
def validateLogin():
	try:
		_username = request.form['inputEmail']
		_password = request.form['inputPassword']
		with app.app_context():
			cursor = mysql.connection.cursor()
			cursor.callproc('sp_validateLogin', (_username,))
			data = cursor.fetchall()
			if len(data) > 0:
				if check_password_hash(str(data[0][3]), _password):
					session['user'] = data[0][0]
					return redirect('/userHome')
				else:
					return render_template('error.html', error='Wrong Email address or Password')
			else:
				return render_template('error.html', error='Wrong Email address or Password')
	except Exception as e:
		return render_template('error.html', error=str(e))

@app.route('/deleteEvent', methods=['POST'])
def deleteEvent():
	try:
		if session.get('user'):
			_user = session.get('user')
			_event_id = request.form['spId']
			cursor = mysql.connection.cursor()
			cursor.callproc('sp_deleteEvent',(_event_id,_user,))
			data = cursor.fetchall()
			if len(data) == 0:
				mysql.connection.commit()
				cursor.close()
				return json.dumps({'status':'OK'})
			else:
				cursor.close()
				return json.dumps({'status':'An Error occured'})
	except Exception as e:
		return render_template('error.html',error = str(e))

@app.route('/getAllEvents')
def getAllEvents():
	try:
		if session.get('user'):
			_user = session.get('user')
			cursor = mysql.connection.cursor()
			cursor.callproc('sp_getEventsByUser',(_user,))
			result = cursor.fetchall()
			events_dict = []
			for event in result:
				e_type = event[3]
				if e_type == "diaper":
					event_dict = {
							'Id':event[0],
							'Time':event[2],
							'Description': "Diaper",
							'Comment':event[7]}
					if event[4]: event_dict['Description'] += " 💩"
					if event[5]: event_dict['Description'] += " 🌊"
					events_dict.append(event_dict)
				if e_type == "bottle":
					event_dict = {
							'Id': event[0],
							'Time':event[2],
							'Description': "Bottle " + str(event[6]) + " oz.",
							'Comment':event[7]}
					events_dict.append(event_dict)
				if e_type == "note":
					event_dict = {
							'Id': event[0],
							'Time':event[2],
							'Description': "Note",
							'Comment':event[7]}
					events_dict.append(event_dict)
			return json.dumps(events_dict)
		else:
			return render_template('error.html', error = 'Unauthorized Access')
	except Exception as e:
		return render_template('error.html',error = str(e))

@app.route('/api/signup', methods=['POST'])
def signUp():
	try:
		_name = request.form['inputName']
		_email = request.form['inputEmail']
		_password = request.form['inputPassword']
		# validate the received values
		if _name and _email and _password:

			# All Good, let's call MySQL
			with app.app_context():
				cursor = mysql.connection.cursor()
				_hashed_password = generate_password_hash(_password)
				cursor.callproc('sp_createUser', (_name, _email, _hashed_password))
				data = cursor.fetchall()
				if len(data) == 0:
					mysql.connection.commit()
					cursor.close()
					return redirect(url_for('success', msg='User created successfully !'))
				else:
					cursor.close()
					return redirect(url_for('error', err=str(data[0])))
			return redirect(url_for('error', err='Enter the required fields!'))

	except Exception as e:
		return redirect(url_for('error', err='Enter the required fields!'))

@app.route('/showAddDiaper')
def showAddDiaper():
	if session.get('user'):
		return render_template('addDiaper.html')
	else:
		render_template('error.html', error = 'Unauthorized Access')

@app.route('/showAddBottle')
def showAddBottle():
	if session.get('user'):
		return render_template('addBottle.html')
	else:
		render_template('error.html', error = 'Unauthorized Access')

@app.route('/showAddNote')
def showAddNote():
	try:
		if session.get('user'):
			return render_template('addNote.html')
		else:
			render_template('error.html', error = 'Unauthorized Access')
	except Exception as e:
		return render_template('error.html', error=str(e))

@app.route('/showDashboard')
def showDashboard():
	try:
		if session.get('user'):
			return render_template('Dashboard.html')
		else:
			render_template('error.html', error = 'Unauthorized Access')
	except Exception as e:
		return render_template('error.html', error=str(e))

@app.route('/addDiaper',methods=['POST'])
@app.route('/addBottle',methods=['POST'])
@app.route('/addNote',methods=['POST'])
def addEvent():
	try:
		if session.get('user'):
			data = ["error"]
			_user = session.get('user')
			_comment = request.form['comment']
			_time = request.form['time']

			_type = request.form.get('type')

			if _type == "diaper":

				_wet = 0 if request.form.get('wet') is None else 1
				_dirty = 0 if request.form.get('dirty') is None else 1

				cursor = mysql.connection.cursor()
				cursor.callproc('sp_addDiaper',(_dirty,_wet,_time,_user,_comment))
				data = cursor.fetchall()

			if _type == "bottle":
				_oz = request.form['bottle_oz']

				cursor = mysql.connection.cursor()
				cursor.callproc('sp_addBottle',(_oz,_time,_user,_comment))
				data = cursor.fetchall()

			if _type == "note":

				cursor = mysql.connection.cursor()
				cursor.callproc('sp_addNote',(_time,_user,_comment))
				data = cursor.fetchall()


			if len(data) == 0:
				mysql.connection.commit()
				return redirect('/userHome')
			else:
				return render_template('error.html',error = 'An error occurred!')
		else:
			return render_template('error.html',error = 'Unauthorized Access')
	except Exception as e:
		return render_template('error.html',error = str(e))

@app.route('/userHome')
def userHome():
	if session.get('user'):
		return render_template('userHome.html')
	else:
		return render_template('error.html', error='Unauthorized Access')


@app.route('/logout')
def logout():
	session.pop('user', None)
	return redirect('/')


if __name__ == "__main__":
	app.run()
