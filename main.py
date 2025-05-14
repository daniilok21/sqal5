from flask import Flask, render_template, redirect, request, abort, url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from data import db_session
from data.jobs import Jobs
from data.users import User
from data.news import News
from forms.job import JobForm
from forms.user import RegisterForm, LoginForm
from forms.news import NewsForm
from forms.department import DepartmentForm
from data.departments import Department
from sqlalchemy import orm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', form=form, message="Пароли не совпадают")

        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', form=form, message="Пользователь уже существует")

        user = User(
            surname=form.surname.data,
            name=form.name.data,
            age=form.age.data,
            position=form.position.data,
            speciality=form.speciality.data,
            address=form.address.data,
            email=form.email.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html', message="Неправильный логин или пароль", form=form)
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/news', methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News(
            title=form.title.data,
            content=form.content.data,
            is_private=form.is_private.data,
            user=current_user
        )
        db_sess.add(news)
        db_sess.commit()
        return redirect('/')
    return render_template('news.html', form=form)


@app.route('/news/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id, News.user == current_user).first()

    if not news:
        abort(404)

    if form.validate_on_submit():
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        db_sess.commit()
        return redirect('/')
    elif request.method == 'GET':
        form.title.data = news.title
        form.content.data = news.content
        form.is_private.data = news.is_private
    return render_template('news.html', form=form)


@app.route('/news_delete/<int:id>')
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    news = db_sess.query(News).filter(News.id == id, News.user == current_user).first()

    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/')


@app.route('/add_job', methods=['GET', 'POST'])
@login_required
def add_job():
    form = JobForm()

    if form.validate_on_submit():
        db_sess = db_session.create_session()
        try:
            leader = db_sess.get(User, int(form.team_leader.data))
            if not leader:
                raise ValueError("Руководитель не найден")
            job = Jobs(
                job=form.job.data,
                team_leader=int(form.team_leader.data),
                work_size=form.work_size.data,
                collaborators=form.collaborators.data,
                is_finished=form.is_finished.data,
                who_created=current_user.id
            )
            db_sess.add(job)
            db_sess.commit()
            return redirect(url_for('index'))
        except Exception as e:
            print(e)
        db_sess.close()
    return render_template('add_job.html', form=form)


@app.route('/edit_job/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_job(id):
    db_sess = db_session.create_session()
    job = db_sess.query(Jobs).join(User).filter(Jobs.id == id).first()
    if not job or (current_user.id != job.team_leader and current_user.id != 1):
        db_sess.close()
        abort(403)
    form = JobForm()
    if form.validate_on_submit():
        try:
            if str(job.team_leader) != form.team_leader.data:
                new_leader = db_sess.get(User, int(form.team_leader.data))
                if not new_leader:
                    raise ValueError("Руководитель не найден")

            job.job = form.job.data
            job.team_leader = int(form.team_leader.data)
            job.work_size = form.work_size.data
            job.collaborators = form.collaborators.data
            job.is_finished = form.is_finished.data

            db_sess.commit()
            return redirect(url_for('index'))
        except Exception as e:
            print(e)
        db_sess.close()

    elif request.method == 'GET':
        form.job.data = job.job
        form.team_leader.data = str(job.team_leader)
        form.work_size.data = job.work_size
        form.collaborators.data = job.collaborators
        form.is_finished.data = job.is_finished

    db_sess.close()
    return render_template('add_job.html', form=form, title='Редактирование работы')


@app.route('/delete_job/<int:id>', methods=['GET', 'POST'])
@login_required
def delete_job(id):
    db_sess = db_session.create_session()
    try:
        job = db_sess.query(Jobs).join(User).filter(Jobs.id == id).first()
        if not job:
            abort(404)
        if current_user.id != job.team_leader and current_user.id != 1:
            abort(403)
        db_sess.delete(job)
        db_sess.commit()

        return redirect(url_for('index'))
    except Exception as e:
        db_sess.rollback()
        print(e)
    db_sess.close()


@app.route('/')
def index():
    db_sess = db_session.create_session()
    try:
        jobs = db_sess.query(Jobs).join(User).all()
        return render_template("jobs.html", jobs=jobs)
    except Exception as e:
        print(e)
    db_sess.close()


@app.route('/departments')
def list_departments():
    db_sess = db_session.create_session()
    try:
        departments = db_sess.query(Department).options(
            orm.joinedload(Department.chief)
        ).all()
        return render_template("departments.html",
                            departments=departments)
    except Exception as e:
        print(f"Error: {e}")
        abort(500)
    finally:
        db_sess.close()


@app.route('/add_department', methods=['GET', 'POST'])
@login_required
def add_department():
    form = DepartmentForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        try:
            chief = db_sess.get(User, form.chief_id.data)
            if not chief:
                return render_template('add_department.html',
                                       title='Добавление департамента',
                                       form=form,
                                       message="Руководитель не найден")

            department = Department(
                title=form.title.data,
                chief_id=form.chief_id.data,
                members=form.members.data,
                email=form.email.data,
                who_created=current_user.id
            )
            db_sess.add(department)
            db_sess.commit()
            return redirect(url_for('list_departments'))
        except Exception as e:
            db_sess.rollback()
            print(f"Error: {e}")
            return render_template('add_department.html',
                                   title='Добавление департамента',
                                   form=form,
                                   message="Ошибка при добавлении департамента")
        finally:
            db_sess.close()

    return render_template('add_department.html',
                           title='Добавление департамента',
                           form=form)


@app.route('/edit_department/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_department(id):
    db_sess = db_session.create_session()
    try:
        department = db_sess.get(Department, id)  # Используем новый метод get()
        if not department or (current_user.id != department.chief_id and current_user.id != 1):
            abort(403)

        form = DepartmentForm()
        if form.validate_on_submit():
            # Проверяем существует ли новый руководитель
            new_chief = db_sess.get(User, form.chief_id.data)
            if not new_chief:
                return render_template('add_department.html',
                                       title='Редактирование департамента',
                                       form=form,
                                       message="Руководитель не найден")

            department.title = form.title.data
            department.chief_id = form.chief_id.data
            department.members = form.members.data
            department.email = form.email.data
            db_sess.commit()
            return redirect(url_for('list_departments'))

        # Заполняем форму данными из БД (GET запрос)
        if request.method == 'GET':
            form.title.data = department.title
            form.chief_id.data = department.chief_id  # Используем chief_id вместо chief
            form.members.data = department.members
            form.email.data = department.email

        return render_template('add_department.html',
                               title='Редактирование департамента',
                               form=form)
    except Exception as e:
        db_sess.rollback()
        print(f"Error editing department: {e}")
        abort(500)
    finally:
        db_sess.close()


@app.route('/delete_department/<int:id>')
@login_required
def delete_department(id):
    db_sess = db_session.create_session()
    try:
        department = db_sess.query(Department).get(id)
        if not department:
            abort(404)
        db_sess.delete(department)
        db_sess.commit()
    finally:
        db_sess.close()
    return redirect('/departments')


if __name__ == '__main__':
    db_session.global_init("db/blogs.db")
    app.run(port=5000, debug = True)