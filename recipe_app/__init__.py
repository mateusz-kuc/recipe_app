from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager


app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login' #Jeżeli nie jesteż zalogowany to wyrzuci cie do strony logowania
login_manager.login_message_category = 'info' # customizacjia defaultowej wiadomości jeżeli nie jesteś zalogowany

from recipe_app import routes
