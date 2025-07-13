import os
import uuid
import json
from datetime import datetime
from flask import Flask, request, render_template, redirect, url_for, flash, session
from werkzeug.utils import secure_filename
from flask_bootstrap import Bootstrap5
import pyrebase

from models import db, QuestionPaper
from forms import UploadPaperForm, FilterForm


# ----------------- CONFIGURATION -----------------

class Config:
    SECRET_KEY = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
    SQLALCHEMY_DATABASE_URI = "sqlite:///question-papers.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join("static", "uploads")


# ----------------- INITIALIZATION -----------------

app = Flask(__name__)
app.config.from_object(Config)
Bootstrap5(app)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Database setup
db.init_app(app)
with app.app_context():
    db.create_all()

# Firebase setup
with open("firebase_config.json") as f:
    firebase_config = json.load(f)

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()


# ----------------- ROUTES -----------------

@app.route('/')
def home():
    recent_papers = db.session.execute(
        db.select(QuestionPaper).order_by(QuestionPaper.upload_date.desc()).limit(3)
    ).scalars().all()
    return render_template("index.html", papers=recent_papers)

# admin signup route is accessible but hidden from normal users
@app.route('/admin/signup', methods=['GET', 'POST'])
def admin_signup():
    if 'admin' not in session:
        flash('You need to be logged in as admin to sign up another admin.', 'danger')
        return redirect(url_for('admin_login'))

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            auth.create_user_with_email_and_password(email, password)
            flash('Admin account created successfully. You can now log in.', 'success')
            return redirect(url_for('admin_login'))
        except Exception as e:
            try:
                error_json = e.args[1]
                error = json.loads(error_json)['error']['message']
                flash(f'Error: {error}', 'danger')
            except:
                flash(f'Unknown error: {str(e)}', 'danger')

    return render_template("admin_signup.html")


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        try:
            auth.sign_in_with_email_and_password(email, password)
            session['admin'] = email
            flash('Logged in as admin', 'success')
            return redirect(url_for('upload'))
        except Exception:
            flash('Incorrect email or password. Please try again.', 'danger')

    return render_template('admin_login.html')


@app.route('/admin/logout')
def admin_logout():
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('admin_login'))


@app.route("/upload", methods=["GET", "POST"])
def upload():
    if 'admin' not in session:
        flash('You need to be logged in as admin to upload papers.', 'danger')
        return redirect(url_for('admin_login'))

    form = UploadPaperForm()
    if form.validate_on_submit():
        pdf = form.pdf_file.data
        filename = secure_filename(pdf.filename)

        if not filename.lower().endswith('.pdf'):
            flash('Invalid file type. Please upload a PDF file.', 'danger')
            return redirect(url_for('upload'))

        unique_name = f"{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_name).replace("\\", "/")
        pdf.save(filepath)

        paper = QuestionPaper(
            subject=form.subject.data.upper(),
            filepath=filepath,
            paperyear=form.paperyear.data,
            set=form.set.data,
            type=form.type.data,
            aiml=form.aiml.data,
            cse=form.cse.data,
            ds=form.ds.data,
            it=form.it.data,
            eee=form.eee.data,
            ece=form.ece.data,
            mech=form.mech.data,
            ce=form.ce.data,
            csbs=form.csbs.data,
            year1=form.year1.data,
            year2=form.year2.data,
            year3=form.year3.data,
            year4=form.year4.data,
        )
        db.session.add(paper)
        db.session.commit()
        flash('Paper uploaded successfully!', 'success')
        return redirect(url_for("home"))

    return render_template("upload.html", form=form)


@app.route("/browse", methods=["GET", "POST"])
def browse():
    form = FilterForm(request.args)
    page = request.args.get('page', 1, type=int)
    per_page = 10

    query = QuestionPaper.query.order_by(QuestionPaper.upload_date.desc())

    if form.subject.data:
        query = query.filter(QuestionPaper.subject.ilike(f"%{form.subject.data.upper()}%"))
    if form.year.data:
        query = query.filter(QuestionPaper.paperyear == form.year.data)
    if form.branch.data:
        branch = form.branch.data.lower()
        if hasattr(QuestionPaper, branch):
            query = query.filter(getattr(QuestionPaper, branch).is_(True))

    papers = query.paginate(page=page, per_page=per_page)
    return render_template("browse.html", form=form, papers=papers)


@app.route("/about")
def about():
    return render_template("about.html")


# ----------------- RUN -----------------

if __name__ == '__main__':
    app.run(debug=True)
