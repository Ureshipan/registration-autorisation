from flask import Flask, request, render_template, make_response, session
from flask_login import LoginManager, login_user
from werkzeug.utils import redirect

import datetime
from data import db_session
from data.jobs import Jobs
from data.users import User
from data.login_form import LoginForm
from data.register import RegisterForm

app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)

app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

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

@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            surname=form.surname.data,
            age=form.age.data,
            position=form.position.data,
            speciality=form.speciality.data,
            address=form.address.data,

        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)
    
    return render_template('register.html', title='Регистрация', form=form)

def main():
    db_session.global_init("db/blogs.db")
    app.run()


if __name__ == '__main__':
    main()
#/register
