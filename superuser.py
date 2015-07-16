from main import create_user, bcrypt
from getpass import getpass
name = 'SuperUser'
access = 'superadmin'

email = raw_input("Email : ")
for i in range(3):
	pwd = getpass()
	confirmpwd = getpass("Confirm Password : ")
	if pwd == confirmpwd:
		pwd_hash = bcrypt.generate_password_hash(pwd)
		if create_user(name=name,email=email,access=access,password=pwd_hash):
			print "Super User created successfully !!"
			break
		else:
			print "Error creating super user contact the admin :("
			break

