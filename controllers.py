import requests
from main import mysql

def sendmail(agent_id,lead_id):
	lead = query('SELECT * FROM lead_details WHERE lead_id = %s',lead_id)


class User(object):
	"""docstring for User"""
	def __init__(self):
		pass
	def get(self,email):
		try:
			conn = mysql.connect()
			cursor = conn.cursor()
			cursor.execute('SELECT id,email,access,authenticated,name FROM lead_track_users WHERE email = %s',[email,])
			user = cursor.fetchone()
			conn.close()
			self.email = user[1]
			self.user_id = user[0]
			self.authenticated = user[3]
			self.access = user[2]
			self.name = user[4]
			return True

		except:
			return False

	def is_active(self):
		return True

	def get_id(self):
		return self.user_id

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
				print save_sql
				cursor.execute(save_sql,params)
				conn.close()
			return True

		except Exception,e:
			print e
			return False



