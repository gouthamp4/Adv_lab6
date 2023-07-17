from flask import Flask, render_template, url_for, session, flash
from flask_wtf import FlaskForm
from werkzeug.utils import redirect
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired
import sqlite3

app = Flask(__name__, template_folder='viewtemplates')
app.config["SECRET_KEY"] = "secret-key"
warnings = []
DB = "password_check.db"

with sqlite3.connect(DB) as connection:
    cursor = connection.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS users (userId INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)"
    )


class PasswordCheckerForm(FlaskForm):
    field_user = StringField(validators=[InputRequired()])
    field_password = PasswordField(validators=[InputRequired()])
    validate = SubmitField("Validate")


def passwordValidate(password):
    del warnings[:]
    if not any(x.isupper() for x in password):
        warnings.append('Password missing Uppercase.')
    if not (password[-1].isdigit()):
        warnings.append('Password Should end with Number.')
    if len(password) < 8:
        warnings.append('password must be min 8 characters.')
    return warnings


@app.route('/')
def home():
    session['failed_attempts'] = 0
    return render_template('home-page.html')


@app.route('/report')
def appReport():
    return render_template('report.html', warnings=warnings)


@app.route('/password-check', methods=['GET', 'POST'])
def passwordSecCheck():
    passwordCheckerForm = PasswordCheckerForm()
    failed_attempts = session.get('failed_attempts')
    if passwordCheckerForm.validate_on_submit():
        session['failed_attempts'] += 1
        if len(passwordValidate(passwordCheckerForm.field_password.data)) > 0:
            if failed_attempts > 2:
                flash('Too Many attempts, Attempts %d of 5' % failed_attempts, 'error')
            return redirect(url_for("appReport"))
        failed_attempts = 0
        with sqlite3.connect(DB) as connection:
            cursor = connection.cursor()
            cursor.execute(
                "INSERT INTO users (username, password) VALUES (?, ?)",
                (passwordCheckerForm.field_user.data, passwordCheckerForm.field_password.data),
            )
        return render_template("success.html", userData= passwordCheckerForm.field_user.data)
    return render_template('password-check.html', form=passwordCheckerForm)


if __name__ == "__main__":
    app.run(debug=True)