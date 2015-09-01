from flask import Flask , make_response, render_template, jsonify, send_from_directory,request,redirect
from flaskext.mysql import MySQL
from flask.ext.login import LoginManager,login_user,logout_user,login_required,current_user
import json
import datetime
from flask.ext.bcrypt import Bcrypt
import requests
from config import *
from terminate import terminate
from twilio.rest import TwilioRestClient
import difflib
import locale

# Currency Locale set1111
locale.setlocale( locale.LC_ALL, 'en_CA.UTF-8' )


app = Flask(__name__,static_url_path='/static')
app.debug = True
app.secret_key = 'BD$b7v5vbr494rfci7cv47b'

#MySQL Config.

mysql = MySQL()
app.config['MYSQL_DATABASE_USER'] = MYSQL_DATABASE_USER
app.config['MYSQL_DATABASE_PASSWORD'] = MYSQL_DATABASE_PASSWORD
app.config['MYSQL_DATABASE_DB'] = MYSQL_DATABASE_DB
app.config['MYSQL_DATABASE_HOST'] = MYSQL_DATABASE_HOST
mysql.init_app(app)


#Bcrypt Config

bcrypt = Bcrypt(app)


# #LoginManager Instansiated
login_manager = LoginManager()

# #LoginManager Initialized
login_manager.init_app(app) 

login_manager.login_view = 'login'


# Twilio Credentials(Temp)

TWILIO_ACCOUNT_SID = 'ACd1e13b7f6f530d73dd47f13ce91224d5'
TWILIO_AUTH_TOKEN = '67b23de6936fea29f8982a341276c070'

# Twilio Client Object 
twilio_client = TwilioRestClient(TWILIO_ACCOUNT_SID,TWILIO_AUTH_TOKEN)


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


def query(sql,params=[]):
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


def lead_details(sql,params=[]):
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
	if field == 'agent':
		sendmail(user_id=value,lead_id=lead_id)
	if field == 'status':
		# Add in disposition table
		create_disposition_record(lead_id=lead_id,agent_id=current_user.user_id,time=datetime.datetime.now(),status=value)
		# Alert Email to the Agent
		return 'OK'
	else:
		save = update_lead(lead_id,field,value)
		return 'OK'

	return 'Error updating the Lead'
	
def d_types(user):
	sql = 'SELECT `text`,value FROM disposition_types WHERE user = %s'
	params = [user,]
	details = lead_details(sql=sql,params=params)
	for i in details:
		i['text'] = str(i['text'])
		i['value'] = str(i['value'])
	return details

@app.route('/status')
@login_required
def disposition_types():
	user = request.args.get('user')
	if not user:
		user = 'agent'

	dispositions = d_types(user)
	return str(dispositions)


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
@login_required
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


@app.route('/charts', methods=['GET'])
@login_required
def charts():
	time_unit = request.args.get('unit')
	type_filter = request.args.get('type_filter')
	params = []
	if not type_filter:
		sql = 'SELECT entry_date FROM lead_details'
	else:
		params = [type_filter]
		sql = 'SELECT entry_date FROM lead_details WHERE status = %s'
	lead_dates,foo = query(sql,params)
	lead_dates = data_distribution(lead_dates,time_unit)
	foo = {}

	for i in lead_dates:
		foo[to_timestamp(i)] = lead_dates[i]

	lead_dates = foo
	result = []

	for i in lead_dates:
		result.append([i,lead_dates[i]])

	result.sort()

	result = {'chart_data':result}
	print len(lead_dates)
	return json.dumps(result)

def to_timestamp(dt):
	return (dt - datetime.datetime(1970, 1, 1)).total_seconds()*1000

def data_distribution(lead_dates,time_unit):
	lead_dates = [row[0] for row in lead_dates]

	if time_unit == 'day':
		lead_dates = [i.replace(hour=0,minute=0,second=0,microsecond=0) for i in lead_dates]
	if time_unit == 'month':
		lead_dates = [i.replace(day=1,hour=0,minute=0,second=0,microsecond=0) for i in lead_dates]
	if time_unit == 'year':
		lead_dates = [i.replace(month=1,day=1,hour=0,minute=0,second=0,microsecond=0) for i in lead_dates]
	if time_unit == 'quarter':
		lead_dates = [i.replace(month=quarter(i.month),day=1,hour=0,minute=0,second=0,microsecond=0) for i in lead_dates]
	if time_unit == 'hour':
		lead_dates = [i.replace(minute=0,second=0,microsecond=0) for i in lead_dates]
	if time_unit == 'week':
		lead_dates = [i.replace(hour=0,minute=0,second=0,microsecond=0) for i in lead_dates]




	distinct = set(lead_dates)
	count = dict(zip(distinct,[0 for i in range(len(distinct))]))

	for i in lead_dates:
		count[i] += 1
	return count

def quarter(month):
	if 1 <= month <= 3:
		return 1
	elif 4 <= month <= 6:
		return 4
	elif 7 <= month <= 9:
		return 7
	else:
		return 10

def truncate_datetime(dt,**kwargs):
	for name,value in kwargs.items():
		dt = dt.replace(name=value)
	return dt

@app.route('/get_dispositions')
@login_required
def get_dispositions():
	lead_id = request.args.get('lead_id')
	params = [lead_id,]
	sql = 'SELECT dt.text status, ltu.name, dr.timestamp, dr.notes FROM disposition_record dr LEFT JOIN lead_track_users ltu\
																		ON ltu.id = dr.agent_id \
																		LEFT JOIN disposition_types dt\
																		ON dr.status = dt.value\
																		WHERE lead_id = %s ORDER BY dr.timestamp desc'
	return json.dumps(lead_details(sql,params))


def create_disposition_record(lead_id,agent_id,status,time,notes=''):
	conn = mysql.connect()
	cursor = conn.cursor()
	sql = 'INSERT IGNORE INTO disposition_record (lead_id,notes,agent_id,status,`timestamp`) VALUES(%s,%s,%s,%s,%s)'
	params = [lead_id,notes,agent_id,status,time]
	update_lead(lead_id,'status',status)

	try:
		with conn:
			cursor.execute(sql,params)
			# conn.close()
			return True
	except Exception,e:
		print e
		# conn.close()
		return False




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

@app.route('/profile',methods=['GET'])
@login_required
def profile():
	lead_id = request.args.get('lead_id')
	sql = 'SELECT * FROM lead_details WHERE lead_id = %s'
	params = [lead_id,]
	row,column = query(sql,params)
	details = dict(zip(column,row[0]))
	names = [
		'first_name' , 'Fist Name',
		'last_name' ,'Last Name',
		'phone_number' , 'Phone Number',
		'email' , 'Email',
		'zip' , 'Zip',
		'street' , 'Street',
		'city' , 'City',
		'state' , 'State',
		'country', 'Country',

	]
	dispositions = d_types('agent')
	# print dispositions

	# print details
	return render_template('profile.html',details=details,names=names,dispositions=dispositions)

@app.route('/create_disposition',methods=['POST'])
@login_required
def create_disposition():
	params = request.form
	notes = params['notes']
	status = params['status']
	lead_id = params['lead_id']
	print notes,status,lead_id
	agent_id = current_user.user_id
	if create_disposition_record(lead_id=lead_id,time=datetime.datetime.now(),status=status,agent_id=agent_id,notes=notes):
		return 'OK'
	else:
		print 'Error Creating Disposition Record.'
		return 'OK'

@app.route('/test',methods=['GET','POST'])
@login_required
def text_sms():
	if request.method == 'GET':
		return render_template('test_sms.html')

	if request.method == 'POST':
		params = request.form
		reciever = params['reciever']
		body = params['body']

		from_  = '15595127617'

		message = send_text(to=reciever,from_=from_,body=body)
		sid = message.sid

		return render_template('test_sms.html',success=True,sid=sid)

def send_text(to,from_,body):
	message = twilio_client.messages.create(
				to=to,
				body=body,
				from_=from_
				)

	return message


@app.route('/esap',methods=['POST','GET'])
def esap_process():
	if request.method == 'GET':
		step = request.args.get('step')
		if not step:
			step = 1
		return render_template('esap.html',step=step,terminate=False)
	
	if request.method == 'POST':
		params = request.form
		extras = {}
		step = int(params['step'])
		print step

		if process_resolution(step=step,params=params,extras=extras):
			step += 1
			return render_template('esap.html',step=step,params=params,terminate=False,extras=extras)

		terminate_message = ''
		if step == 7:
			lead_id = match_address(make_address(params))
			terminate_message = status_terminate(lead_id=lead_id)

		return render_template('esap.html',
								terminate=True,
								step=step,
								terminate_message=terminate_message)


def status_terminate(lead_id):
	sql = 'SELECT status FROM lead_details WHERE lead_id = %s'
	sql_params = [lead_id,]

	rows,foo = query(sql,sql_params)
	status = rows[0][0]

	return terminate(status)


def guess_address(zip_code):
	sql = 'SELECT City FROM zip_codes WHERE zip_code = %s'
	sql_params = [zip_code,]
	city, foo = query(sql,sql_params)

	city = city[0][0]
	return city



def check_zip(params,extras):
	zip_code = params['zip_code']
	sql = 'SELECT * from zip_codes WHERE zip_code = %s'
	sql_params = [zip_code,]
	q = query(sql,sql_params)[0]
	if q:
		extras['city'] = guess_address(zip_code)
		return True
	return False

def check_provider(params,extras):
	gas = params['gas']
	electric = params['electric']

	if gas == 'other' and electric == 'other':
		return False
	return True

def members(params,extras):
	extras['required_income'] = required_income(params)
	return True

def home_age(params):
	age = params['age']
	if age == 'yes':
		return True
	return False

def match_address(address):
	sql = 'SELECT apartment_number,street,city,state,lead_id from lead_details'
	rows = query(sql)[0]

	suspects = {}

	for row in rows:
		suspect = row[0] + row[1] + row[2] + row[3]
		suspects[suspect] = row[4]
	
	matches = difflib.get_close_matches(address,suspects.keys(),cutoff=0.95)

	if matches:
		return suspects[matches[0]]
	return False


def make_address(params):
	return params['street'] + params['city'] + params['state']


def check_address(params):
	
	address = make_address(params)
	match = match_address(address)

	if match:
		return False
	return True


def add_details(params,extras):


	first_name = params['first_name']
	last_name = params['last_name']

	email = params['email']
	print email

	mobile_phone = params['phone_number']
	home_phone = params['home_phone']

	zip_code = params['zip_code']
	members = params['members']

	street = params['street']
	if 'apartment_number' in params.keys():
		apartment_number = params['apartment_number']
	else:
		apartment_number = ''

	if params['own'] == 'no':
		landlord_name = params['landlord_name']
		landlord_contact = params['landlord_contact']
	else:
		landlord_contact = ''
		landlord_name = ''
	city = params['city']
	state = params['state']
	country = 'Unites States'

	sql = 'INSERT INTO lead_details(first_name,\
									last_name,\
									email,\
									phone_number,\
									home_phone,\
									zip,\
									members,\
									street,\
									apartment_number,\
									city,\
									state,\
									Country,\
									landlord_name,\
									landlord_contact) \
						 VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'

	sql_params = [first_name,last_name,email,mobile_phone,home_phone,zip_code,members,street,apartment_number,city,state,country,landlord_name,landlord_contact,]

	conn = mysql.connect()

	with conn:
		cursor = conn.cursor()
		cursor.execute(sql,sql_params)
		extras['lead_id'] = cursor.lastrowid
		print 'id : ',cursor.lastrowid
		
	return True

def add_referer(params,extras):

	lead_id = params['lead_id']
	referer_name = params['referer_name']
	referer_email = params['referer_email']
	referer_phone_number = params['referer_phone_number']
	referer_relation = params['referer_relation']

	sql = 'UPDATE lead_details set referer_name = %s,\
									referer_email = %s,\
									referer_phone = %s,\
									referer_relation = %s \
									 WHERE lead_id = %s'

	sql_params = [referer_name,referer_email,referer_phone_number,referer_relation,lead_id]

	conn = mysql.connect()

	with conn:
		cursor = conn.cursor()
		cursor.execute(sql,sql_params)

	return False


member_income = {
		1 : 31860,
		2 : 31860,
		3 : 40180,
		4 : 48500,
		5 : 56820,
		6 : 65140,
		7 : 73460,
		8 : 81780
	}

def required_income(params):
	members = int(params['members'])
	required_income = 0
	if members <= 9:
		required_income = member_income[members]
	else:
		difference = members - 9
		extra_income = difference * 8320
		required_income = member_income[8] + extra_income
	return locale.currency(required_income,grouping=True)


def check_income(params):
	income = params['income']
	if income == 'no':
		return False
	return True

def check_own(params):
	own = params['own']
	return True


def check_referer(params):
	referer = params['referer']
	if referer == 'yes':
		return True
	return False


def process_resolution(step,params,extras):
	if step == 1:
		print params
		return check_zip(params=params, extras=extras)

	elif step == 2:
		return check_provider(params,extras)

	elif step == 3:
		return members(params,extras)
	elif step == 4:
		return check_income(params)

	elif step == 5:
		return home_age(params)

	elif step == 6:
		return check_own(params)

	elif step == 7:
		return check_address(params)
	
	elif step == 8:
		return add_details(params,extras)
	elif step == 9:
		return check_referer(params)
	elif step == 10:
		return add_referer(params,extras)
	elif step == 11:
		return False





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