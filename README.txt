The Chronicle is a newspaper web app with user-submitted content.

	•	Developed in Python with Flask web-development microframework
	•	Uses object relational mapping with SQLAlchemy to build and interface with the database for persistent data storage (both SQLite and PostgreSQL supported)
	•	User authentication and protection with OAuth2
	•	HTML templates use Bootstrap to achieve responsive design
	•	Configured and hosted app on an Ubuntu web server


Instructions:

to create database and run web server:
 1. Install Vagrant and Virtualbox if not previously installed
 3. Navigate to the Catalog directory in the terminal
 4. type 'vagrant up' and 'vagrant ssh' into terminal to enter VM
 5. navigate to the catalog directory by typing 'cd /vagrant/catalog/' into the VM
 6. run the database setup script by typing 'python database_setup.py' into the VM
 7. run the webserver script by typing 'python project.py' into the VM