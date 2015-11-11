**** So I meant to add style to this project but I spent the entire last day trying to fix an OAuth problem (which basically boiled down to the fact that I spelled 'access' wrong in one spot).  All the functionality should work now, but I can resubmit it in a few days and make it actually look nice with CSS if you want.



 to create database:
 1. Install Vagrant and Virtualbox if not previously installed
 2. Place the directory that contains this README into the vagrant directory
 3. Navigate to the vagrant directory in the terminal
 4. type 'vagrant up' and 'vagrant ssh' into terminal to enter VM
 5. navigate to the catalog directory by typing 'cd /vagrant/catalog/' into the VM
 6. run the database setup script by typing 'python database_setup.py' into the VM

 to run web server:
 7. run the webserver script by typing 'python project.py' into the VM