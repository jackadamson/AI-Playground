from gevent import monkey
monkey.patch_all()
from aiplayground.app import app as application
