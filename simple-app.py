from flask import Flask
from flask import render_template
from wtforms import Form, BooleanField, TextField, PasswordField, validators
from flask import request
import surveyorv3

app = Flask(__name__)

class RegistrationForm(Form):
	username = TextField('Username', [validators.Length(min=4, max=125)])
	password = PasswordField('Password', [validators.Length(min=6, max=135)])

@app.route('/login', methods=['GET', 'POST'])
def login():
	form = RegistrationForm(request.form)
	if request.method == 'POST' and form.validate():
		testlogin = surveyorv3.Login(username=form.username.data, password=form.password.data)
		formslogin = surveyorv3.Forms_API(testlogin)
		return formslogin.list_forms()
	return render_template('register.html', form=form)

@app.route('/')
def index(name='None'):
	return render_template('test.html', name=name)

app.run(debug=True, host='0.0.0.0', port=8000)
