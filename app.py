from datetime import datetime
import os
import uuid
from werkzeug.utils import secure_filename
from flask import Flask, request, render_template, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, BooleanField
from wtforms.fields.choices import SelectField
from wtforms.validators import DataRequired, Optional
import json
import pyrebase

with open("firebase_config.json") as f:
    firebase_config = json.load(f)

firebase = pyrebase.initialize_app(firebase_config)
auth = firebase.auth()

UPLOAD_FOLDER = 'static/uploads'  # path to saved pdfs
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
Bootstrap5(app)

class Base(DeclarativeBase):
  pass

db = SQLAlchemy(model_class=Base)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///question-papers.db"
db.init_app(app)

class QuestionPaper(db.Model):
    id: Mapped[int] = mapped_column(primary_key=True, nullable=False)
    subject: Mapped[str] = mapped_column(nullable=False)
    aiml: Mapped[bool] = mapped_column(default=False)
    cse: Mapped[bool] = mapped_column(default=False)
    ds: Mapped[bool] = mapped_column(default=False)
    it: Mapped[bool] = mapped_column(default=False)
    csbs: Mapped[bool] = mapped_column(default=False)
    eee: Mapped[bool] = mapped_column(default=False)
    ece: Mapped[bool] = mapped_column(default=False)
    mech: Mapped[bool] = mapped_column(default=False)
    ce: Mapped[bool] = mapped_column(default=False)
    year1: Mapped[bool] = mapped_column(default=False)
    year2: Mapped[bool] = mapped_column(default=False)
    year3: Mapped[bool] = mapped_column(default=False)
    year4: Mapped[bool] = mapped_column(default=False)
    paperyear: Mapped[str] = mapped_column(nullable=False)
    set: Mapped[int] = mapped_column(nullable=False)
    type: Mapped[str] = mapped_column(nullable=False)
    upload_date: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    filepath: Mapped[str] = mapped_column(nullable=False)


class UploadPaperForm(FlaskForm):
    subject = StringField('Subject', validators=[DataRequired()])
    pdf_file = FileField('PDF File', validators=[DataRequired()])

    paperyear = StringField("Paper Year", validators=[DataRequired()])
    type = SelectField("Type", choices=[
        ("GR24", "GR24"),
        ("GR22", "GR22"),
        ("GR20", "GR20"),
        ("GR18", "GR18")
    ], validators=[DataRequired()])
    set = SelectField("Set", choices=[
        ("1", "1"),
        ("2", "2"),
        ("3", "3"),
        ("4", "4")
    ], validators=[DataRequired()])
    # Department checkboxes
    aiml = BooleanField('AIML')
    cse = BooleanField('CSE')
    ds = BooleanField('DS')
    it = BooleanField('IT')
    csbs = BooleanField('CSBS')
    eee = BooleanField('EEE')
    ece = BooleanField('ECE')
    mech = BooleanField('MECH')
    ce = BooleanField('CE')

    # Year checkboxes
    year1 = BooleanField('1st Year')
    year2 = BooleanField('2nd Year')
    year3 = BooleanField('3rd Year')
    year4 = BooleanField('4th Year')

    submit = SubmitField('Upload Paper')

class FilterForm(FlaskForm):
    subject = StringField(label="Subject", validators=[Optional()])
    year = SelectField('Year', choices=[
        ("", "All Years"),
        ("2024", "2024"),
        ("2023", "2023"),
        ("2022", "2022"),
        ("2021", "2021"),
        ("2020", "2020"),
        ("2019", "2019"),
        ("2018", "2018"),
    ], validators=[Optional()])
    branch = SelectField('Branch', choices=[
        ("", "All Branches"),
        ("CSE", "CSE"),
        ("AIML", "AIML"),
        ("DS", "DS"),
        ("IT", "IT"),
        ("CSBS", "CSBS"),
        ("ECE", "ECE"),
        ("MECH", "MECH"),
        ("EEE", "EEE"),
        ("CE", "CE"),
    ], validators=[Optional()])
    submit = SubmitField('Apply Filters')
with app.app_context():
    db.create_all()
@app.route('/')
def home():  # put application's code here
    recent_papers = db.session.execute(db.select(QuestionPaper).order_by(QuestionPaper.upload_date.desc()).limit(3)).scalars().all()
    return render_template("index.html", papers=recent_papers)


# @app.route('/admin/signup', methods=['GET', 'POST'])
# def admin_signup():
#     if request.method == 'POST':
#         email = request.form['email']
#         password = request.form['password']
#
#         try:
#             user = auth.create_user(email=email, password=password)
#             flash('Admin account created successfully. You can now log in.', 'success')
#             return redirect(url_for('admin_login'))
#         except Exception as e:
#             flash(f'Error: {str(e)}', 'danger')
#
#     return redirect(url_for("upload"))

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            # Authenticate using Pyrebase
            user = auth.sign_in_with_email_and_password(email, password)
            session['admin'] = email  # Store admin session
            flash('Logged in as admin', 'success')
            return redirect(url_for('upload'))

        except Exception as e:
            flash('Incorrect email or password. Please try again.', 'danger')

    return render_template('admin_login.html')


@app.route('/admin/logout')
def admin_logout():
    # Clear the session to log the user out
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
        original_filename = secure_filename(pdf.filename)

        # Check if the uploaded file is a PDF
        if not original_filename.lower().endswith('.pdf'):
            flash('Invalid file type. Please upload a PDF file.', 'danger')
            return redirect(url_for('upload'))

        # Generate a unique filename with timestamp or UUID
        unique_suffix = datetime.utcnow().strftime("%Y%m%d%H%M%S") + "_" + str(uuid.uuid4())[:8]
        filename = f"{unique_suffix}_{original_filename}"

        filepath = os.path.join(UPLOAD_FOLDER, filename).replace("\\", "/")
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
    page = request.args.get('page', 1, type=int)  # Get the current page number, default to 1
    per_page = 10  # You can adjust the number of papers per page

    papers_query = QuestionPaper.query.order_by(QuestionPaper.upload_date.desc())

    if form.subject.data:
        papers_query = papers_query.filter(QuestionPaper.subject.ilike(f"%{form.subject.data.upper()}%"))
    if form.year.data:
        papers_query = papers_query.filter(QuestionPaper.paperyear == form.year.data)
    if form.branch.data:
        branch_filter = form.branch.data.lower()
        if hasattr(QuestionPaper, branch_filter):
            papers_query = papers_query.filter(getattr(QuestionPaper, branch_filter).is_(True))

    papers = papers_query.paginate(page=page, per_page=per_page)  # Paginate the results

    return render_template("browse.html", form=form, papers=papers)
@app.route("/about")
def about():
    return render_template("about.html")

if __name__ == '__main__':
    app.run(debug=True)
