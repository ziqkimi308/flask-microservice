from flask import Flask
from app.database import init_db
import os
from app.routes import bp

def create_app(test_config=None):
	"""
	- Create an instance of flask.
	"""

	app = Flask(__name__)

	"""
	- SQLAlchemy is an ORM.
	- Attach postgresql db to flask instance.
	"""

	app.config["SQLALCHEMY_DATABASE_URI"] = (
		"postgresql://%(user)s:%(password)s@%(host)s:%(port)s/%(name)s" % {
			"user":     os.getenv("DB_USER", "devops"),
			"password": os.getenv("DB_PASSWORD", "devopspass"),
			"host":     os.getenv("DB_HOST", "localhost"),
			"port":     os.getenv("DB_PORT", "5432"),
			"name":     os.getenv("DB_NAME", "microservice"),
		}
	)
	app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

	# Override with test config if provided
	if test_config:
		app.config.update(test_config)

	init_db(app)

	"""
	- Attach the routes blueprint to flask instance.
	"""

	app.register_blueprint(bp)

	return app
