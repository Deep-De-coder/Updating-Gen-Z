from flask import Flask, render_template, url_for, request, redirect, flash
from flask import session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import os
import datetime
from pygooglenews import GoogleNews
from openpyxl import load_workbook


app = Flask(__name__)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = "You need to Login first"

app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Updating-Gen-Z.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    profile = db.Column(db.String, nullable=True)
    name = db.Column(db.String(200))
    about = db.Column(db.String(500), nullable=True)
    username = db.Column(db.String(200), unique=True)
    password = db.Column(db.String(200))
    mail_id = db.Column(db.String(100), unique=True)
    mobno = db.Column(db.String(20))
    blogsnumber = db.Column(db.Integer)
    expertise = db.Column(db.String(200), nullable=True)

    grammer_points = db.Column(db.Integer, nullable=True)
    history_points = db.Column(db.Integer, nullable=True)
    geography_points = db.Column(db.Integer, nullable=True)
    humanresource_points = db.Column(db.Integer, nullable=True)
    law_points = db.Column(db.Integer, nullable=True)
    psychology_points = db.Column(db.Integer, nullable=True)
    economy_points = db.Column(db.Integer, nullable=True)
    agriculture_points = db.Column(db.Integer, nullable=True)
    science_points = db.Column(db.Integer, nullable=True)
    sociology_points = db.Column(db.Integer, nullable=True)
    politics_points = db.Column(db.Integer, nullable=True)

    score = db.Column(db.Integer)


class Questions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(200), nullable=True, unique=True)
    choice1 = db.Column(db.String(200))
    choice2 = db.Column(db.String(200))
    choice3 = db.Column(db.String(200))
    choice4 = db.Column(db.String(200))
    answer = db.Column(db.String(200))
    domain = db.Column(db.String(200))


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    title = db.Column(db.String(100))
    topic = db.Column(db.String(100))
    post = db.Column(db.String(1500))
    picture = db.Column(db.String, nullable=True)
    likes = db.Column(db.Integer, default=0)
    date = db.Column(db.String(50))


class Tasks(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    task = db.Column(db.String(200))
    status = db.Column(db.String(10), default="In progress")
    date = db.Column(db.String, nullable=True)


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == "POST":
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method="sha256")
        cpassword = request.form['cpassword']
        mail_id = request.form['mail_id']
        picture = '../static/img/default_pf.png'

        user = Users.query.filter_by(username=username).first()
        if user:
            flash("User Name Already Exists, Choose another one")
            return redirect("/signup")
        user = Users.query.filter_by(mail_id=mail_id).first()
        if user:
            flash("Email Already Registered, Try logging in")
            return redirect("/login")

        if(password == cpassword):
            new_user = Users(username=username, name=name,
                             password=hashed_password, mail_id=mail_id, profile=picture)
            db.session.add(new_user)
            db.session.commit()

            flash("Sucessfully Registered!", "success")
            return redirect('/login')
        else:
            flash("Passwords don't match", "danger")
            return redirect("/signup")

    return render_template("sign-up.html")


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        logout_user()
        username = request.form.get('username')
        password = request.form.get('password')

        user = Users.query.filter_by(username=username).first()
        if not user:
            flash("No such User found, Try Signing Up First", "warning")
            return redirect("/signup")
        if user:
            if check_password_hash(user.password, password):
                login_user(user)
                return redirect("/allblogs")
            else:
                flash("Incorrect password", "danger")
                return redirect("login")
    return render_template("log-in.html")


@app.route('/logout')
def logout():
    logout_user()
    flash("Successfully Logged out!")
    return redirect('/')


@app.route('/')
def index():
    return render_template('Index.html', current_user=current_user)


@app.route('/news', methods=['GET', 'POST'])
def news():
    if request.method == "GET":
        stories = []
        gn = GoogleNews(country='India')
        top = gn.top_news()
        newsitem = top['entries']
        for item in newsitem:
            story = {
                'title': item.title,
                'link': item.link,
                'published': item.published
            }
            stories.append(story)
        return render_template('news.html', stories=stories, current_user=current_user)
    if request.method == "POST":
        query = request.form.get('query')
        stories = []
        gn = GoogleNews(country='India')
        search = gn.search(query, when='24h')
        newsitem = search['entries']
        for item in newsitem:
            story = {
                'title': item.title,
                'link': item.link,
                'published': item.published
            }
            stories.append(story)
        return render_template('news.html', stories=stories, current_user=current_user, query=query)


@app.route('/addblog/<int:user_id>', methods=['POST', 'GET'])
@login_required
def addblog(user_id):
    if request.method == "POST":
        user_id = user_id
        title = request.form['title']
        domain = request.form['domain']
        date = datetime.datetime.today()
        date = date.strftime("%d %B, %Y")
        post = request.form['post']

        picture = "../static/img/default_blogpicture.jpeg"

        new_blog = Blog(user_id=user_id, title=title,
                        topic=domain, post=post, date=date, picture=picture)
        db.session.add(new_blog)
        db.session.commit()
        user = Users.query.filter_by(id=user_id).first()
        if user.blogsnumber == None:
            user.blogsnumber = 1
        else:
            user.blogsnumber = user.blogsnumber + 1
        db.session.commit()
        return redirect('/allblogs')

    return render_template('addblog.html', current_user=current_user)


@app.route('/allblogs', methods=['POST', 'GET'])
def allblogs():
    blogs = Blog.query.all()
    if blogs:
        for blog in blogs:
            user = Users.query.filter_by(id=blog.user_id).first()
            blog.user_id = user.username
            blog.likes = user.score
    return render_template('blogs.html', blogs=blogs, current_user=current_user)


@app.route('/searchblogs', methods=['POST', 'GET'])
def searchblogs():
    if request.method == "POST":
        query = request.form['query']
        search = "{0}".format(query)
        search = search+'%'

        blogs = Blog.query.filter(
            or_(Blog.title.like(search), Blog.topic.like(search), Blog.post.like(search))).all()
        if len(blogs) == 0:
            flash("No such Blog availabe!")

        for blog in blogs:
            user = Users.query.filter_by(id=blog.user_id).first()
            blog.user_id = user.username

        return render_template('blogs.html', blogs=blogs, current_user=current_user)


@app.route('/searchusers', methods=['POST', 'GET'])
def searchusers():
    if request.method == "POST":
        query = request.form['query']
        search = "{0}".format(query)
        search = search+'%'

        users = Users.query.filter(
            or_(Users.name.like(search), Users.username.like(search), Users.about.like(search))).all()
        if len(users) == 0:
            flash("No such Blog availabe!")
    else:
        users = Users.query.all()
    return render_template('search.html', current_user=current_user, users=users)


def save_excel(form_excel):
    _, f_ext = os.path.splitext(form_excel.filename)
    excel_fn = "sheet" + f_ext
    excel_path = os.path.join(app.root_path, excel_fn)
    form_excel.save(excel_path)
    return excel_fn


@app.route('/addques', methods=['POST', 'GET'])
def addques():
    if request.method == "POST":
        sheet = request.files['Excel']
        data_file = save_excel(sheet)
        # Load the entire workbook.
        wb = load_workbook(data_file, data_only=True)
        # Load one worksheet.
        ws = wb['Sheet1']
        all_rows = list(ws.rows)

        # Pull information from specific cells.
        for row in all_rows[1:10]:
            question = row[0].value
            choice1 = row[1].value
            choice2 = row[2].value
            choice3 = row[3].value
            choice4 = row[4].value
            answer = row[5].value
            domain = row[6].value

            newques = Questions(question=question, domain=domain, choice1=choice1,
                                choice2=choice2, choice3=choice3, choice4=choice4, answer=answer)
            db.session.add(newques)
        db.session.commit()
        flash('Question added!')
        return redirect('/addques')
    return render_template('admin.html', current_user=current_user)


@app.route('/submitquiz/<int:user_id>', methods=['POST', 'GET'])
@login_required
def submitquizget(user_id):
    if request.method == "GET":
        return render_template('quiz.html', q=None, current_user=current_user)


@app.route('/submitquiz/<int:user_id>/<domain>', methods=['POST', 'GET'])
@login_required
def submitquiz(user_id, domain):
    qlist = Questions.query.filter_by(domain=domain).order_by(
        Questions.id.desc()).limit(5).all()

    # random_question_list = random.sample(qlist, 5)
    question_list = qlist
    if request.method == "GET":
        return render_template('quiz.html', q=1, question_list=question_list, current_user=current_user, domain=domain)

    if request.method == "POST":
        count = 0
        selected_options = []
        for question in question_list:

            question.id = str(question.id)

            selected_option = request.form[question.id]
            selected_options.append(selected_option)

            correct_option = question.answer

            if selected_option == correct_option:
                count = count+1

        user = Users.query.filter_by(id=user_id).first()

        if domain == "politics":
            if user.politics_points == None:
                user.politics_points = 0
            user.politics_points = user.politics_points + count
            db.session.commit()

        elif domain == "grammer":
            if user.grammer_points == None:
                user.grammer_points = 0
            user.grammer_points = user.grammer_points + count
            db.session.commit()

        elif domain == "geography":
            if user.geography_points == None:
                user.geography_points = 0
            user.geography_points = user.geography_points + count
            db.session.commit()

        elif domain == "history":
            if user.history_points == None:
                user.history_points = 0
            user.history_points = user.history_points + count
            db.session.commit()

        elif domain == "psychology":
            if user.psychology_points == None:
                user.psychology_points = 0
            user.psychology_points = user.psychology_points+count
            db.session.commit()

        elif domain == "agriculture":
            if user.agriculture_points == None:
                user.agriculture_points = 0
            user.agriculture_points = user.agriculture_points+count
            db.session.commit()

        elif domain == "law":
            if user.law_points == None:
                user.law_points = 0
            user.law_points = user.law_points + count
            db.session.commit()

        elif domain == "sociology":
            if user.sociology_points == None:
                user.sociology_points = 0
            user.sociology_points = user.sociology_points+count
            db.session.commit()

        elif domain == "economy":
            if user.economy_points == None:
                user.economy_points = 0
            user.economy_points = user.economy_points + count
            db.session.commit()

        elif domain == "humanresource":
            if user.humanresource_points == None:
                user.humanresource_points = 0
            user.humanresource_points = user.humanresource_points + count
            db.session.commit()

        elif domain == "science":
            if user.science_points == None:
                user.science_points = 0
            user.science_points = user.science_points + count
            db.session.commit()
        else:
            pass

        if user.score == None:
            user.score = 0

        current_quiz_score = count
        user.score = user.score + count
        db.session.commit()

        return render_template("show-quiz-score.html", question_list=question_list, selected_options=selected_options, current_user=current_user, current_quiz_score=current_quiz_score)


@app.route('/todolist/<int:user_id>', methods=['POST', 'GET'])
@login_required
def todolist(user_id):
    show = None
    if request.method == "POST":
        task = request.form.get('task')
        deadline = request.form.get('date')
        new_task = Tasks(user_id=user_id, task=task, date=deadline)
        db.session.add(new_task)
        db.session.commit()
        flash('TASK ADDED')
    return render_template('To-do.html', current_user=current_user, show=None)


@app.route('/showtodolist/<int:user_id>', methods=['POST', 'GET'])
@login_required
def showtodolist(user_id):
    user = Users.query.filter_by(id=user_id).first()
    tasklist = Tasks.query.filter_by(user_id=user_id).all()
    return render_template('To-do.html', tasklist=tasklist, current_user=current_user, show=1)


@app.route('/deletetask/<int:user_id>/<int:task_id>', methods=['POST'])
@login_required
def deletetask(user_id, task_id):
    task = Tasks.query.filter_by(id=task_id, user_id=user_id).first()
    db.session.delete(task)
    db.session.commit()
    return redirect(f'/showtodolist/{user_id}')


@app.route('/finishtask/<int:user_id>/<int:task_id>', methods=['POST'])
@login_required
def finishtask(user_id, task_id):
    task = Tasks.query.filter_by(id=task_id, user_id=user_id).first()
    task.status = "Finished"
    db.session.commit()
    return redirect(f'/showtodolist/{user_id}')


@app.route('/userprofile/<int:user_id>', methods=['POST', 'GET'])
@login_required
def userprofile(user_id):
    user = Users.query.filter_by(id=user_id).first()
    blogs = Blog.query.filter_by(user_id=user_id).all()
    if request.method == 'POST':
        user.name = request.form['name']
        user.username = request.form['username']
        user.mail_id = request.form['mail_id']
        user.mobno = request.form['mobno']
        user.expertise = request.form['expertise']

        db.session.commit()
    return render_template('profile.html', user=user, current_user=current_user, blogs=blogs)


@app.route('/aboutus')
def aboutus():
    return render_template('aboutus.html', current_user=current_user)


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
