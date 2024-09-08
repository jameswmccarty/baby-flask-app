# baby-flask-app
simple flask web app backed by mysql for logging activity


1) This app requires a virtual python environment.

	$ python3 -m venv babyappenv

2) Copy the contents of this repo into the babyappenv folder.

3) Configure mysql as the root user for the database.

	CREATE DATABASE babytracker;
	CREATE USER 'babyflask'@'localhost' IDENTIFIED BY 'a_secure_password_that_you_make_up';
	GRANT ALL ON babytracker.* TO 'babyflask'@'localhost';
	quit

	Then from the command line

	$mysql -u babyflask -p < ./BabyTrackerProcedures.sql

4) Activate the virtual environment:

	$ . bin/activate

5) Install the necessary support packages:

	$pip install -r requirements.txt

6) Modify app.py to include the MySQL password established in step 3, and a secret.

7) When ready, lauch the app:

	$ gunicorn --bind 0.0.0.0:5000 wsgi:app
