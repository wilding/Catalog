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



 Questions:
    - is passing STATE through <script> safe? no
    - post method inside article or in seperate function?
    - why joinedload_all for delete comments?
    - transition animations not worth it?



To Do:
    - fix mobile
    - optimize images
    - prevent internal server errors by limiting characters in <input>

    - hide edit/delete on small width
    - no redirect on comment CRUD/isolate to comments section
    - animate profile pic on login
    - shrink g-signin on resize
    - form height on window resize

    - windows start menu-like layout
    - rating system
    - card size by rating


Deployment Instructions:

IP Address: 52.34.98.169
port: 2200
url: http://ec2-52-34-98-169.us-west-2.compute.amazonaws.com/

summary:
    - sshed into server as root
    - created new user grader
    - locally generated new key pair
    - added new public key to /home/grader/.ssh/authorized_keys
    - switched owner and group of both .ssh/ directory and authorized_keys file from root to grader
    - added superuser permission for grader in /etc/sudoers.d/grader
    - changed port from 22 to 2200 in /etc/ssh/sshd_config
    - logged out of root and sshed into grader @ port 2200
    - disabled remote root login in /etc/ssh/sshd_config

    - configured uncomplicated firewall to deny all incoming connections by default
    - configured uncomplicated firewall to allow all outgoing connections by default
    - configured uncomplicated firewall to allow connections from ports 2200, 80, and 123
    - enabled uncomplicated firewall

    - used apt-get to install apache2, libapache2-mod-wsgi, libapache2-mod-wsgi python-dev, postgresql, git, python-pip, python-psycopg2, libpq-dev, and fail2ban
    - used apt-get to update and upgrade all packages
    - set up automatic security updates

    - created Catalog/ directory in /var/www/
    - inside the Catalog/ directory, cloned the git repository for the Catalog flask app
    - changed project.py to __init__.py
    - used pip install to download virtualenv
    - created virtual environment catalogenv
    - inside the virtual environment, used pip to install Flask, oauth2client, psycopg2, and Flask-SQLAlchemy
    - created and enabled new virtual host in /etc/apache2/sites-enabled/Catalog.conf
    - added catalog.wsgi file to /var/www/Catalog/ (*note: not the git clone, its parent)
    - added line pointing to the wsgi file inside /etc/apache2/sites-enabled/000-default.conf
    - inside virtual environment, created postgresql user catalog
    - altered create_engine() line in both __init__.py and database_setup.py to match postgresql form:
        ('postgresql://catalog:catalog@localhost/catalog')
    - changed line in /etc/postgresql/9.3/main/pg_hba.conf from 'peer' to 'md5'
    - altered lines in __init__.py that referred to client_secrets.json to include the full path
    - altered line in __init__.py gconnect function from login_session['credentials'] = credentials to login_session['access_token'] = credentials.access_token
    - logged into default postgres user and created the catalog database
    - connected the catalog user to the catalog database
    - ran __init__.py in the virtual environment
    - altered oauth2 web client credentials to include url in authorized javascript origins



third party resources:
    - https://www.digitalocean.com/community/tutorials/how-to-deploy-a-flask-application-on-an-ubuntu-vps
    - http://killtheyak.com/use-postgresql-with-django-flask/
    - https://www.digitalocean.com/community/tutorials/how-to-install-and-use-postgresql-on-ubuntu-14-04
    - https://stackoverflow.com/questions/28253681/you-need-to-install-postgresql-server-dev-x-y-for-building-a-server-side-extensi
    - http://docs.sqlalchemy.org/en/rel_1_0/core/engines.html
    - https://stackoverflow.com/questions/29565392/error-storing-oauth-credentials-in-session-when-authenticating-with-google
    - https://help.ubuntu.com/community/AutomaticSecurityUpdates
    - https://www.digitalocean.com/community/tutorials/how-to-protect-ssh-with-fail2ban-on-ubuntu-14-04
