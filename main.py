from flask import Flask , make_response, render_template, jsonify, send_from_directory,request,redirect
from flaskext.mysql import MySQL
from flask.ext.login import LoginManager,login_user,logout_user,login_required,current_user
import json
import datetime
from flask.ext.bcrypt import Bcrypt
import requests

app = Flask(__name__,static_url_path='/static')
app.debug = True
app.secret_key = 'BD$b7v5vbr494rfci7cv47b'

#MySQL Config.

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'badman1108'
app.config['MYSQL_DATABASE_DB'] = 'lead'
app.config['MYSQL_DATABASE_HOST'] = 'localhost'
mysql.init_app(app)


#Bcrypt Config

bcrypt = Bcrypt(app)


# #LoginManager Instansiated
login_manager = LoginManager()

# #LoginManager Initialized
login_manager.init_app(app) 

login_manager.login_view = 'login'


class User(object):
	"""docstring for User"""
	def __init__(self):
		pass
	def get(self,email):
		try:
			conn = mysql.connect()
			cursor = conn.cursor()
			cursor.execute('SELECT id,email,access,authenticated,name,password FROM lead_track_users WHERE email = %s',[email,])
			user = cursor.fetchone()
			conn.close()
			self.email = user[1]
			self.user_id = str(user[0])
			self.authenticated = user[3]
			self.access = user[2]
			self.name = user[4]
			self.password = user[5]
			return True

		except:
			return False

	def is_active(self):
		return True

	def get_id(self):
		return unicode(self.email)

	def is_authenticated(self):
		return self.authenticated

	def is_anonymous(self):
		return False

	def save(self):
		conn = mysql.connect()
		try:
			with conn:
				cursor = conn.cursor()
				params = [self.email, self.access, self.authenticated, self.name, self.user_id]
				save_sql = 'UPDATE lead_track_users SET email = %s , access = %s , authenticated = %s , name = %s WHERE id = %s'
				cursor.execute(save_sql,params)
				# conn.close()
			return True

		except Exception,e:
			print e
			return False



def create_user(name,email,access,password):
	conn = mysql.connect()
	with conn:
		cursor = conn.cursor()
		params = [name,email,access,password]
		sql = 'INSERT INTO lead_track_users(id,name,email,access,password) VALUES (NULL,%s,%s,%s,%s);'
		cursor.execute(sql ,params)
	return True


def query(sql,params):
	conn = mysql.connect()
	cursor = conn.cursor()
	cursor.execute(sql,params)
	rows = cursor.fetchall()
	rows = [list(row) for row in rows]
	columns = [desc[0] for desc in cursor.description]
	conn.close()
	return (rows,columns)

def update_lead(lead_id,column,value):
	conn = mysql.connect()
	cursor = conn.cursor()
	params  = [value,lead_id]
	sql = '''UPDATE lead_details SET ''' + column + ''' = %s WHERE lead_id = %s;'''
	print sql
	try:
		with conn:
			cursor.execute(sql,params)
			return True
	except Exception,e:
		print e
	conn.close()
	return False


def delete_lead(lead_id_list):
	print len(lead_id_list)
	conn = mysql.connect()
	cursor = conn.cursor()
	sql = "DELETE  FROM lead_details WHERE lead_id IN (%s)" % (','.join(['%s']*len(lead_id_list)))
	print sql
	try:
		with conn:
			cursor.execute(sql,lead_id_list)
			return True
	except Exception,e:
		print e
	conn.close()
	return False


def lead_details(sql,params):
	rows,columns = query(sql,params)
	result = []
	for row in rows:
		for idx,element in enumerate(row):
			if type(element) == datetime.datetime:
				row[idx] = element.strftime("%A, %d. %B %Y %I:%M%p")
		row = dict(zip(columns,row))
		result.append(row)
	return result

@app.route('/leads')
@login_required
def display():
	user_id = request.args.get('user_id')
	params = []
	if current_user.access != 'agent':
		sql = 'SELECT * FROM lead_details \
								ORDER BY `lead_details`.`entry_date` DESC'
	else:
		sql = 'SELECT * FROM lead_details \
						WHERE agent = %s							 \
								ORDER BY `lead_details`.`entry_date` DESC'
		params = [user_id]

	return json.dumps(lead_details(sql,params))


@app.route('/')
@login_required
def home():
	return render_template('admin_dashboard.html')

@app.route('/edit',methods = ['POST'])
@login_required
def edit():
	params = request.form
	lead_id = params['pk']
	field = params['name']
	value = params['value']
	save = update_lead(lead_id,field,value)
	if save:
		if field == 'agent':
			sendmail(user_id=value,lead_id=lead_id)

		return 'OK'
	
	else:
		return 'Error updating the Lead'
	

@app.route('/status')
@login_required
def status():
	result =   [
			              {'value': 'default' , 'text': '--status--'},
			              {'value': 'previously_enrolled', 'text': 'Previosly Enrolled'},
			              {'value': 'appointment_set', 'text': 'Appointment Set'},
			              {'value': 'out_of_territory', 'text': 'Out of Territory'},
			              {'value': 'customer_refused', 'text': 'Customer Refused'},
			              {'value': 'working_on_lead', 'text': 'Working on Lead'}
           				]
   			 

   	return str(result)

@app.route('/agents')
@login_required
def agents():
	agents = query('SELECT id,name FROM lead_track_users WHERE access = "agent"',[])[0]
	result = [{'value':'0','text' : '--Assign Lead--'}]
	for user in agents:
		result.append(dict(zip(('value','text'),(int(user[0]),str(user[1])))))
	return str(result)

@app.route('/delete',methods=['POST'])
@login_required
def delete():
	dataa = request.data
	print dataa
	lead_id_list = json.loads(dataa)["lead_id_list"]
	print lead_id_list
	if delete_lead(lead_id_list):
		return 'OK'
	return '500'

@app.route('/create_user',methods=['POST','GET'])
# @login_required
def create():

	# Agents not allowed to create Users.
	if current_user.access == 'agent':
		return redirect('/')


	if request.method == 'GET':
		access = current_user.access
		available_users = ['agent']
		if access == 'superadmin':
			available_users.append('admin')
		return render_template('create_user.html')
	
	if request.method == 'POST':
		params = request.form
		print params
		name = params['name']
		email = params['email']
		access = params['access']
		password = params['password']
		pwd_hash = bcrypt.generate_password_hash(password)
		if create_user(name=name,email=email,access=access,password=pwd_hash):
			return 'Success Creating User'
		else:
			return 'Failed'




@login_manager.user_loader
def load_user(user_id):
	'''User Loader for flask-login 
	:params
	 user_id -> email 
	'''
	user = User()
	if user.get(email=user_id):
		return user
	else:
		return None

@app.route('/login',methods=['GET','POST'])
def login():
	if request.method == 'GET':
		return render_template('login.html')
	if request.method == 'POST':
		params = request.form
		print params
		email = str(params['email'])
		password = params['password']
		remember = False
		if 'remember' in params:
			remember = True
		user = User()
		if user.get(email=email):
			if bcrypt.check_password_hash(user.password,password):
				user.authenticated = True
				if user.save():
					print login_user(user,remember=remember)
					print current_user.name
					return redirect('/')

		return render_template('login.html')


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    """Logout the current user."""
    user = current_user
    user.authenticated = False
    user.save()
    logout_user()
    return render_template("login.html")



def sendmail(user_id,lead_id):
	conn = mysql.connect()
	row = query('SELECT name,email FROM lead_track_users WHERE id = %s',[user_id,])
	print row
	name,email = row[0][0][0],row[0][0][1]
	message = message_creator(lead_id,name)

	return requests.post(
        "https://api.mailgun.net/v3/sandboxf32357e89d9f49879486f38f1affacc0.mailgun.org/messages",
        auth=("api", "key-49df66c0deb773d5ee957597be27f9e9"),
        data={"from": "Lead Track<mailgun@sandboxf32357e89d9f49879486f38f1affacc0.mailgun.org>",
              "to": [email],
              "subject": "Lead Assignment",
              "text": message})




def message_creator(lead_id,name):
	params = [lead_id,]
	sql = 'SELECT first_name,last_name,email,zip,street,city,state,country,members,status FROM lead_details WHERE lead_id = %s'

	details,columns = query(sql,params)
	details = tuple(details[0])
	print details

	message = "Hello {0} , you have been assigned a new lead for Highlands Enrgy Prooject.\
			   The Details about the customer are as follows: ".format(name)

	print message
	info  = '''
				  Name : {0} {1} 
				  Email : {2}
				  Zip Code : {3}
				  Address : {4}
				  City : {5}
				  State : {6}
				  Country : {7}
				  No. of Members in the Family: {8}
				  Disposition: {9}
			   '''.format(*details)
	return message + info



if __name__== '__main__':
	app.run()


# Lead Detail Pivot SQL

# INSERT INTO lead_details (lead_id,first_name,last_name,zip,street,city,state,country,phone_number,email,members,status,entry_date)



# SELECT lead_id,

# MAX(CASE WHEN field_number = '19.3' THEN value END) first_name,
# MAX(CASE WHEN field_number = '19.6' THEN value END) last_name,
# MAX(CASE WHEN field_number = '1' THEN value END) zip,
# MAX(CASE WHEN field_number = '20.1' THEN value END) street,
# MAX(CASE WHEN field_number = '20.3' THEN value END) city,
# MAX(CASE WHEN field_number = '20.4' THEN value END) state,
# MAX(CASE WHEN field_number = '20.6' THEN value END) country,
# MAX(CASE WHEN field_number = '21' THEN value END) 
# phone_number,
# MAX(CASE WHEN field_number = '22' THEN value END) 
# email,
# MAX(CASE WHEN field_number = '2' THEN value END)
# members,
# l.status,
# l.date_created entry_date

# FROM wp_rg_lead_detail ld LEFT JOIN wp_rg_lead l ON l.id = ld.lead_id 
# GROUP by lead_id