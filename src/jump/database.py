import re
from datetime import datetime
from storm.locals import *

db=create_database("sqlite://./jump.sqlite")
store=Store(db)

class User(object):
	__storm_table__="user"
	user_id=Int(primary=True)
	username=Unicode()
	password=Unicode()
	created=DateTime()
	modified=DateTime()

	def __init__(self, **kwargs):
		for k,v in kwargs.items():
			setattr(self, k, v)
		self.created=datetime.utcnow()
		self.modified=datetime.utcnow()

	def __setattr__(self, k, v):
		super(User, self).__setattr__(k, v)
		super(User, self).__setattr__("modified", datetime.utcnow())

	@staticmethod
	def validateUsername(username):
		return re.match(ur"^[A-Za-z0-9`_\[\]{}|-]", username)