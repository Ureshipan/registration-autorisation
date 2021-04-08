from flask import Flask, request, render_template, make_response, session
from flask_login import LoginManager, login_user
from werkzeug.utils import redirect

import datetime
from data import db_session
from data.jobs import Jobs
from data.users import User
from data.login_form import LoginForm

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)

app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(
    days=365
)

@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)

@app.route('/')
@app.route('/index')
def journal():
    jobs = []
    session = db_session.create_session()
    for i in session.query(Jobs).all():
        jobs.append((i.job,
                     name(session, i.team_leader),
                     surname(session, i.team_leader),
                     i.work_size,
                     i.collaborators,
                     i.is_finished))
    session.close()
    params = {}
    print(jobs)
    params["title"] = "Журнал работ"
    #params["static_css"] = url_for('static', filename="css/")
    #params["static_img"] = url_for('static', filename="img/")
    params["jobs"] = jobs
    return render_template("jobs.html", **params)


def name(session, idd):
    for i in session.query(User).filter(User.id == idd):
        return i.name
    
def surname(session, idd):
    for i in session.query(User).filter(User.id == idd):
        return i.surname

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("http://127.0.0.1:5000/")
        return render_template('login.html',
                                   message="Неправильный логин или пароль",
                                   form=form)
    return render_template('login.html', title='Авторизация', form=form)

def main():
    db_session.global_init("db/blogs.db")
    app.run()


if __name__ == '__main__':
    main()
