from flask import Flask , make_response, render_template, jsonify, send_from_directory,request,redirect
from flaskext.mysql import MySQL
from flask.ext.login import LoginManager,login_user,logout_user,login_required,current_user
import json
import datetime
import pytz
from flask.ext.bcrypt import Bcrypt
import requests
from config import *
from terminate import terminate
from twilio.rest import TwilioRestClient
import difflib
import locale
from operator import itemgetter
from address import AddressParser

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

# MailGun Credentials

MG_BASE_URL = 'https://api.mailgun.net/v3/mg.highlandsenergy.com/messages'
MG_API_KEY = 'key-bd7254f9d0a6d6ea5c74bd6fcdd4dc72'

# SoCal Gas Email
SOCAL_GAS = 'esapleads@semprautilities.com'

# Production Variable imported from config.

# TimeZone Settings

UTC = pytz.utc
PST = pytz.timezone('US/Pacific')


class User(object):
	"""docstring for User"""
	def __init__(self):
		pass
	def get(self,email):
		try:
			conn = mysql.connect()
			cursor = conn.cursor()
			cursor.execute('SELECT id,email,access,authenticated,name,password,phone_number FROM lead_track_users WHERE email = %s',[email,])
			user = cursor.fetchone()
			conn.close()
			self.email = user[1]
			self.user_id = str(user[0])
			self.authenticated = user[3]
			self.access = user[2]
			self.name = user[4]
			self.password = user[5]
			self.phone_number = user[6]
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
				params = [self.email, self.access, self.authenticated, self.name,self.phone_number,  self.user_id]
				save_sql = 'UPDATE lead_track_users SET email = %s , access = %s , authenticated = %s , name = %s , phone_number = %s WHERE id = %s'
				cursor.execute(save_sql,params)
				# conn.close()
			return True

		except Exception,e:
			print e
			return False



def create_user(name,email,access,password,phone_number):
	conn = mysql.connect()
	with conn:
		cursor = conn.cursor()
		params = [name,email,phone_number,access,password]
		sql = 'INSERT INTO lead_track_users(id,name,email,phone_number,access,password) VALUES (NULL,%s,%s,%s,%s,%s);'
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
				element = UTC.localize(element)
				element = element.astimezone(PST)
				row[idx] = element.strftime("%A, %d. %B %Y %I:%M%p")
		row = dict(zip(columns,row))
		result.append(row)
	return result

@app.context_processor
def utility_processor():
	return dict(pretty_name=pretty_name,
				format_number=format_number,
				format_address=format_address)

def sendmail(text,to,subject):
	try:
		requests.post(
	        MG_BASE_URL,
	        auth=("api", MG_API_KEY),
	        data={"from": "Highlands Energy <mailgun@mg.highlandsenergy.com>",
	              "to": to,
	              "subject": subject,
	              "html": html_markdown(text)})
		return True
	except Exception,e:
		print e
		return False

def format_number(number):
	if '(' in number:
		return number
	if number == '':
		return ''
	result = '(123) 456-789t'
	result = result.replace('123',number[0:3])
	result = result.replace('456',number[3:6])
	result = result.replace('789t',number[6:])
	return result

def format_address(address):
	ap = AddressParser()
	address = ap.parse_address(address).full_address()
	result = ''
	for i in address:
		if i != '.':
			result += i
	return result



@app.route('/mailgun_webhook',methods=['POST'])
def show():
	print request.form
	return 'OK'



@app.route('/leads')
@login_required
def display():
	user_id = request.args.get('user_id')
	view_all = bool(request.args.get('viewall'))
	print 'viewall',view_all
	params = []
	if current_user.access != 'agent':
		sql = '''SELECT lead_id,first_name,last_name,CONCAT(street_number," ",street_name) address, \
								city, gas, electric , entry_date, status,\
								agent,apartment_number,zip,home_phone,\
								phone_number FROM lead_details 
								WHERE IF(status = 'unable_to_reach'
		  					  	 OR status = 'ready_for_assignment'
		  					  	 OR status = 'address_not_valid'
		  					  	 OR status = 'default'
		  					  	 OR status = 'utility_authorization_needed',TRUE,%s)
								ORDER BY `lead_details`.`entry_date` DESC'''
	else:
		sql = '''SELECT lead_id, first_name,last_name,CONCAT(street_number," ",street_name) address,
								city, gas, electric , entry_date, status,
								agent,apartment_number,zip,
								home_phone,phone_number,own,
								(SELECT status FROM disposition_record WHERE lead_id = lead_id
								ORDER BY `timestamp` DESC LIMIT 1,1) as last_disposition
								 FROM lead_details 
		  					  	 WHERE agent = %s
		  					  	 AND IF(status = 'unable_to_reach'
		  					  	 OR status = 'ready_for_assignment'
		  					  	 OR status = 'address_not_valid'
		  					  	 OR status = 'default'
		  					  	 OR status = 'utility_authorization_needed',TRUE,%s)
								 ORDER BY `lead_details`.`entry_date` DESC'''
		
	if current_user.access == 'agent':
		params = [user_id,view_all]
	else:
		params = [view_all]

	ld = lead_details(sql,params)
	for i in ld:
		# i['address'] = format_address(i['address'])
		if current_user.access == 'agent':
			i['home_phone'] = format_number(i['home_phone'])
			i['phone_number'] = format_number(i['phone_number'])
			i['last_disposition'] = pretty_name(i['last_disposition'])
	return json.dumps(ld)


@app.route('/')
@login_required
def home():
	view_all = request.args.get('viewall')
	if not view_all:
		view_all = ''
	view_all = 'viewall=' + view_all
	kpi_nums = kpi_numbers(current_user)
	return render_template('admin_dashboard.html',kpi_nums=kpi_nums,view_all=view_all)

@app.route('/edit',methods = ['POST'])
@login_required
def edit():
	params = request.form
	lead_id = params['pk']
	field = params['name']
	value = params['value']
	if field == 'address':
		field1 = 'street_number'
		field2 = 'street_name'
		value1,value2 = [i for i in getstno(value)]
		print value1,value2
		edit_method(lead_id=lead_id,field=field1,value=value1)
		return edit_method(lead_id=lead_id,field=field2,value=value2)

	return edit_method(lead_id=lead_id,field=field,value=value)

def getstno(address):
	street_name = ''
	street_number = ''
	for idx,i in enumerate(address):
		if i == ' ':
			delimiter = idx
			break
	street_number = address[:idx]
	street_name = address[idx+1:]
	return (street_number,street_name)


def edit_method(lead_id,field,value,notes=''):
	if field == 'agent':
		lead_assignment_mail(user_id=value,lead_id=lead_id)
	elif field == 'status':
		# Add in disposition table
		create_disposition_record(lead_id=lead_id,agent_id=current_user.user_id,time=datetime.datetime.now(),status=value,notes=notes)
		# Alert Email to the Agent
		correspondence_routing(value,lead_id,'email')
		correspondence_routing(value,lead_id,'text')
	save = update_lead(lead_id,field,value)
	if field != 'status':
		action_record(lead_id=lead_id,action=field,agent_id=current_user.user_id)
	if save:
		return 'OK'
	return 'Error updating the lead.'
	


def pretty_name(name):
	if name:
		name = name.replace('_',' ')
		name = name.capitalize()
	return name


def action_record(lead_id,action,agent_id,notes=''):
	conn = mysql.connect()
	cursor = conn.cursor()
	action = 'Edited ' + pretty_name(action)
	sql = 'INSERT IGNORE INTO action_record (lead_id,notes,agent_id,action,`timestamp`) VALUES(%s,%s,%s,%s,%s)'
	params = [lead_id,notes,agent_id,action,datetime.datetime.now()]

	try:
		with conn:
			cursor.execute(sql,params)
			# conn.close()
			return True
	except Exception,e:
		print e
		# conn.close()
		return False
	
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
		phone_number = params['phone_number']
		access = params['access']
		password = params['password']
		pwd_hash = bcrypt.generate_password_hash(password)
		if create_user(name=name,email=email,phone_number=phone_number,access=access,password=pwd_hash):
			return render_template('create_user.html',success=True)
		else:
			return render_template('create_user.html',success=False)


@app.route('/user',methods=['POST','GET'])
@login_required
def update():

	if request.method == 'GET':
		user = User()
		details = {}
		user.get(current_user.email)
		details['name'] = user.name
		details['email'] = user.email
		details['phone_number'] = user.phone_number
		return render_template('user_profile.html',user=details)

	if request.method == 'POST':
		user = User()
		params = request.form
		name = params['name']
		email = params['email']
		phone_number = params['phone_number']
		user.get(current_user.email)
		print user.name
		user.name = name
		user.email = email
		user.phone_number = phone_number
		user.save()			
		return redirect('/user')


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


def kpi_numbers(user):
	'''Provides the KPI numbers based on 
		the user'''

	user_type =  user.access

	if user_type == 'superadmin':
		sql = 'SELECT status FROM lead_details'
		dispositions,foo = query(sql)
		final = {
		'awaiting_assignment' : 0,
		'appointment_set' : 0,
		'previously_enrolled' : 0,
		'refused' : 0,
		'dnq' : 0,
		'currently_working' : 0,

		}

		for i in dispositions:
			i = i[0]#only element

			if i == 'default':
				final['awaiting_assignment'] += 1
			elif i == 'appointment_set':
				final['appointment_set'] += 1
			elif i == 'previously_enrolled':
				final['previously_enrolled'] += 1
			elif i == 'customer_refused':
				final['refused'] += 1
			elif i == 'dnq_out_of_area' or i == 'dnq_other_utility':
				final['dnq'] += 1
			elif i == 'working_on_lead':
				final['currently_working'] += 1

		return final

	elif user_type == 'admin':

		sql = 'SELECT status FROM lead_details'
		dispositions,foo = query(sql)

		final = {

				'unassigned_leads' : 0,
				'require_utility_authorization': 0,
				'require_customer_response' : 0,
				'awaiting_assignment' : 0,
		}

		for i in dispositions:
			i = i[0]

			if i == 'default':
				final['unassigned_leads'] += 1
			elif i == 'utility_authorization_needed':
				final['require_utility_authorization'] += 1
			elif i == 'appointment_set':
				final['require_customer_response'] += 1
			elif i == 'ready_for_assignment' :
				final['awaiting_assignment'] += 1

		return final

	else:

		sql = 'SELECT status FROM lead_details WHERE agent = %s'
		sql_params = [user.user_id]
		dispositions,foo = query(sql,sql_params)

		final = {

			'open_leads' : 0,
			'appointment_set' : 0,
			'dnq' : 0,
			'customer_refused' : 0,
			'owner_management_refused' : 0,
		}
		print 'Agent Disposition',dispositions
		for i in dispositions:
			i = i[0]

			if i == 'appointment_set':
				final['appointment_set'] += 1
			elif i == 'default':
				final['open_leads'] += 1
			elif i == 'dnq_out_of_area' or i == 'dnq_other_utility':
				final['dnq'] += 1
			elif i == 'customer_refused':
				final['customer_refused'] += 1
			else:
				final['open_leads'] += 1

		return final



def correspondence_routing(disposition,lead_id,c_type,referer=False):
	sql = 'SELECT `text`,`subject` FROM auto_correspondence WHERE type = %s AND status = %s'
	sql_params = [c_type,disposition]
	data,foo = query(sql,sql_params)
	if referer:
		sql = 'SELECT referer_email,referer_phone FROM lead_details WHERE lead_id = %s'
	else:
		sql = 'SELECT email,phone_number FROM lead_details WHERE lead_id = %s'
	sql_params = [lead_id,]
	contact,foo = query(sql,sql_params)
	try:
		data = data[0]
		text = data[0]
		if len(data) == 2:
			subject = data[1]
		contact = contact[0]
		email,phone_number = [i for i in contact]
	except Exception,e:
		print e
		return False

	if c_type == 'email':
		try:
			text = custom_text(text=text,disposition=disposition,lead_id=lead_id)
			if PRODUCTION and disposition == 'utility_authorization_needed':
				sendmail(to=[email,SOCAL_GAS], text=text,subject=subject)
			else:
				sendmail(to=[email], text=text,subject=subject)
			return True
		except Exception,e:
			print e
			return False
	elif c_type == 'text':
		try:
			text = custom_text(text=text,disposition=disposition,lead_id=lead_id)
			send_text(to=phone_number,body=text)
			return True
		except Exception,e:
			print e
			return False
	return False

def custom_text(text,lead_id,disposition):
	if disposition == 'new_application':

		sql = 'SELECT ld.first_name, ld.last_name, dr.notes disposition_notes, ld.home_phone, ld.phone_number, ltu.name agent_name,\
				ltu.email agent_email ,ltu.phone_number agent_number FROM lead_details ld LEFT JOIN \
		   disposition_record dr ON ld.lead_id = dr.lead_id LEFT JOIN lead_track_users ltu ON \
		   ld.agent = ltu.id WHERE ld.lead_id = %s order by dr.timestamp desc LIMIT 1'
		params = [lead_id,]

	else:
		sql = 'SELECT ld.first_name, ld.last_name, dr.notes disposition_notes, ld.home_phone, ld.phone_number, ltu.name agent_name,\
				ltu.email agent_email ,ltu.phone_number agent_number FROM lead_details ld LEFT JOIN \
		   disposition_record dr ON ld.lead_id = dr.lead_id LEFT JOIN lead_track_users ltu ON \
		   ld.agent = ltu.id WHERE ld.lead_id = %s\
		   AND dr.status = %s order by dr.timestamp desc LIMIT 1'
		params = [lead_id,disposition]

	data = lead_details(sql,params)

	if data:
		data = data[0]

	print data
	if not data['agent_name']:
		data['agent_name'] = current_user.name
	if not data['agent_number']:
		data['agent_number'] = current_user.phone_number
	if not data['agent_email']:
		data['agent_email'] = current_user.email
	for i in data:
		text = text.replace(i,unicode(data[i]))
	print text
	return text

@app.route('/charts', methods=['GET'])
@login_required
def charts():
	time_unit = request.args.get('unit')
	kpi = request.args.get('kpi')
	print kpi
	params = []
	if kpi == 'all':
		sql = 'SELECT entry_date FROM lead_details'
	else:
		params = [kpi]
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
	sql = 'SELECT DISTINCT dt.text status, ltu.name, dr.timestamp, dr.notes FROM disposition_record dr LEFT JOIN lead_track_users ltu\
																		ON ltu.id = dr.agent_id \
																		LEFT JOIN disposition_types dt\
																		ON dr.status = dt.value\
																		WHERE lead_id = %s ORDER BY dr.timestamp desc'
	disposition_record = lead_details(sql,params)

	sql = 'SELECT DISTINCT ar.action status, ltu.name, ar.notes, ar.timestamp, ar.notes \
							FROM action_record ar LEFT JOIN lead_track_users ltu ON\
															ltu.id = ar.agent_id WHERE\
															lead_id = %s ORDER BY\
															ar.timestamp desc'
	action_record = lead_details(sql,params)

	total_record = disposition_record + action_record

	total_record = sorted(total_record,reverse=True,key=lambda record: datetime.datetime.strptime(record['timestamp'],"%A, %d. %B %Y %I:%M%p"))

	return json.dumps(total_record)


def create_disposition_record(lead_id,agent_id,status,time,notes=''):
	conn = mysql.connect()
	cursor = conn.cursor()
	sql = 'INSERT IGNORE INTO disposition_record (lead_id,notes,agent_id,status,`timestamp`) VALUES(%s,%s,%s,%s,%s)'
	params = [lead_id,notes,agent_id,status,time]

	try:
		with conn:
			cursor.execute(sql,params)
			# conn.close()
			return True
	except Exception,e:
		print e
		# conn.close()
		return False




def lead_assignment_mail(user_id,lead_id):
	conn = mysql.connect()
	row = query('SELECT name,email FROM lead_track_users WHERE id = %s',[user_id,])
	print row
	name,email = row[0][0][0],row[0][0][1]
	message = message_creator(lead_id,name)

	return requests.post(
        MG_BASE_URL,
        auth=("api", MG_API_KEY),
        data={"from": "Lead Track - Highlands Energy <mailgun@mg.highlandsenergy.com>",
              "to": [email],
              "subject": "Lead Assignment",
              "text": message})


# HTML rendering for Emails.

def html_markdown(text):
	result = ''
	for i in text:
		if i == '\n':
			result += '<br>'
		result += i
	return render_template('email.html',text=result)



def message_creator(lead_id,name):
	params = [lead_id,]
	sql = 'SELECT first_name,last_name,email,zip,CONCAT(street_number," ",street_name) AS address,city,state,country,members,status FROM lead_details WHERE lead_id = %s'

	details,columns = query(sql,params)
	details = tuple(details[0])
	print details

	message = "Hello {0} , you have been assigned a new lead for Highlands Energy Project.\n\
			   The Details about the customer are as follows: ".format(name)

	print message
	info  = '''
				  Name : {0} {1} 
				  Address : {4}
				  City : {5}
				  State : {6}
				  Zip Code : {3}
				  Email : {2}
				  No. of Members in the Family: {8}
				  Disposition: {9}
			   '''.format(*details)
	return message + info

@app.route('/profile',methods=['GET'])
@login_required
def profile():
	lead_id = request.args.get('lead_id')
	# Customer
	customer_sql = 'SELECT first_name,last_name,phone_number,home_phone,email,zip,CONCAT(street_number," ",street_name) AS address,city,\
				state,apartment_number FROM lead_details WHERE lead_id = %s'
	params = [lead_id,]
	customer_info = lead_details(customer_sql,params)[0]

	# Referrer 

	referer_sql = 'SELECT referer_name,referer_email,referer_phone,referer_relation \
					FROM lead_details WHERE lead_id = %s'

	referer_info = lead_details(referer_sql,params)[0]

	# LandLord 

	landlord_sql = 'SELECT landlord_name,landlord_phone,landlord_email FROM lead_details WHERE lead_id = %s'

	landlord_info = lead_details(landlord_sql,params)[0]

	addon_sql = 'SELECT gas,electric,public_assistance,members,own,income FROM lead_details WHERE lead_id = %s'

	addon_info = lead_details(addon_sql,params)[0]
	
	dispositions = d_types('agent')

	customer_order = ['first_name','last_name','address','city','state','zip', 'email', 'phone_number' ,'home_phone']
	referer_order = ['referer_name','referer_relation','referer_phone','referer_email']
	
	landlord_order = ['landlord_name','landlord_phone','landlord_email']
	# print dispositions

	# print details
	return render_template('profile.html',customer_info=customer_info,
							customer_order=customer_order,
							landlord_info=landlord_info,landlord_order=landlord_order,
							referer_info=referer_info,referer_order=referer_order,
							addon_info=addon_info,dispositions=dispositions,
							lead_id=lead_id)

@app.route('/create_disposition',methods=['POST'])
@login_required
def create_disposition():
	params = request.form
	notes = params['notes']
	status = params['status']
	lead_id = params['lead_id']
	print notes,status,lead_id
	agent_id = current_user.user_id
	edit_method(lead_id=lead_id,field='status',value=status,notes=notes)
	return redirect('profile?lead_id='+lead_id)

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

def send_text(to,body,from_='15595127617'):
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
		return True
	return False

def check_provider(params,extras):
	gas = params['gas']
	electric = params['electric']

	if gas == 'other' and electric == 'other':
		return False
	return True

def members(params,extras):
	public_assistance = ''
	for i in range(1,11):
		q = 'public_assistance' + str(i)
		try:
			public_assistance += params[q] + '\n'
		except:
			pass
	print public_assistance
	extras['required_income'] = required_income(params)
	extras['public_assistance'] = public_assistance
	return True

def home_age(params):
	age = params['age']
	if age == 'yes':
		return True
	return False

def match_address(address):
	sql = 'SELECT street_number,street_name,city,state,lead_id,apartment_number from lead_details'
	rows = query(sql)[0]

	suspects = {}

	for row in rows:
		suspect = row[0] + row[1] + row[2] + row[3] + row[5]
		suspects[suspect] = row[4]
	
	match = difflib.get_close_matches(address,suspects.keys(),cutoff=0.95,n=1)
	print 'address',address
	if match:
		print match
		return suspects[match[0]]
	return False


def make_address(params):

	return format_address(params['street_number'] + ' ' + params['street_name']) + params['city'] + params['state'] + params['apartment_number']


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

	street_number = params['street_number']
	street_name = format_address(params['street_name'])

	print street_number,street_name
	if 'apartment_number' in params.keys():
		apartment_number = params['apartment_number']
	else:
		apartment_number = ''

	print params['apartment_number']
	if params['own'] == 'no':
		landlord_name = params['landlord_name']
		landlord_phone = params['landlord_phone']
		landlord_email = params['landlord_email']
	else:
		landlord_phone = ''
		landlord_email = ''
		landlord_name = ''
	city = params['city']
	state = params['state']
	country = 'Unites States'
	gas = params['gas']
	electric = params['electric']
	own = params['own']
	if own == 'yes':
		own = 'OWN'
	else:
		own = 'RENT'
	income = params['required_income']
	public_assistance = params['public_assistance']


	sql = 'INSERT IGNORE INTO lead_details(first_name,\
									last_name,\
									email,\
									phone_number,\
									home_phone,\
									zip,\
									members,\
									street_number,street_name,\
									apartment_number,\
									city,\
									state,\
									country,\
									landlord_name,\
									landlord_phone,landlord_email,\
									gas,electric,own,income,public_assistance) \
						 VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'

	sql_params = [first_name,last_name,email,mobile_phone,home_phone,zip_code,members,street_number,street_name,apartment_number,city,state,country,landlord_name,landlord_phone,landlord_email,gas,electric,own,income,public_assistance]

	conn = mysql.connect()

	with conn:
		cursor = conn.cursor()
		cursor.execute(sql,sql_params)
		extras['lead_id'] = cursor.lastrowid
		print 'id : ',cursor.lastrowid

	correspondence_routing(disposition='new_application',
								lead_id=extras['lead_id'],
								c_type='email')
	correspondence_routing(disposition='new_application',
								lead_id=extras['lead_id'],
								c_type='text')

		
	return True

def add_referer(params,extras):

	lead_id = params['lead_id']
	print 'lead_id', lead_id
	referer_name = params['referer_name']
	referer_email = params['referer_email']
	referer_phone_number = params['referer_phone_number']
	referer_relation = params['referer_relation']
	print referer_name

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

	correspondence_routing(disposition='new_application',
								lead_id=lead_id,
								c_type='email',referer=True)
	correspondence_routing(disposition='new_application',
								lead_id=lead_id,
								c_type='text',referer=True)

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
	if members < 9:
		required_income = member_income[members]
	else:
		difference = members - 8
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
		print 'add_referer'
		return add_referer(params,extras)
	elif step == 11:
		return False





if __name__== '__main__':
	app.run('0.0.0.0')


# Lead Detail Pivot SQL

# INSERT INTO lead_details (lead_id,first_name,last_name,zip,street_name,city,state,country,phone_number,email,members,entry_date)



# SELECT lead_id,

# MAX(CASE WHEN field_number = '19.3' THEN value END) first_name,
# MAX(CASE WHEN field_number = '19.6' THEN value END) last_name,
# MAX(CASE WHEN field_number = '1' THEN value END) zip,
# MAX(CASE WHEN field_number = '20.1' THEN value END) street_name,
# MAX(CASE WHEN field_number = '20.3' THEN value END) city,
# MAX(CASE WHEN field_number = '20.4' THEN value END) state,
# MAX(CASE WHEN field_number = '20.6' THEN value END) country,
# MAX(CASE WHEN field_number = '21' THEN value END) 
# phone_number,
# MAX(CASE WHEN field_number = '22' THEN value END) 
# email,
# MAX(CASE WHEN field_number = '2' THEN value END)
# members,
# l.date_created entry_date

# FROM wp_rg_lead_detail ld LEFT JOIN wp_rg_lead l ON l.id = ld.lead_id 
# GROUP by lead_id