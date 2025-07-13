from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, BooleanField
from wtforms.fields.choices import SelectField
from wtforms.validators import DataRequired, Optional

class UploadPaperForm(FlaskForm):
    subject = StringField('Subject', validators=[DataRequired()])
    pdf_file = FileField('PDF File', validators=[DataRequired()])
    paperyear = StringField("Paper Year", validators=[DataRequired()])
    type = SelectField("Type", choices=[("GR24", "GR24"), ("GR22", "GR22"), ("GR20", "GR20"), ("GR18", "GR18")])
    set = SelectField("Set", choices=[("1", "1"), ("2", "2"), ("3", "3"), ("4", "4")])
    aiml = BooleanField('AIML')
    cse = BooleanField('CSE')
    ds = BooleanField('DS')
    it = BooleanField('IT')
    csbs = BooleanField('CSBS')
    eee = BooleanField('EEE')
    ece = BooleanField('ECE')
    mech = BooleanField('MECH')
    ce = BooleanField('CE')
    year1 = BooleanField('1st Year')
    year2 = BooleanField('2nd Year')
    year3 = BooleanField('3rd Year')
    year4 = BooleanField('4th Year')
    submit = SubmitField('Upload Paper')

class FilterForm(FlaskForm):
    subject = StringField("Subject", validators=[Optional()])
    year = SelectField("Year", choices=[
        ("", "All Years"), ("2024", "2024"), ("2023", "2023"),
        ("2022", "2022"), ("2021", "2021"), ("2020", "2020"),
        ("2019", "2019"), ("2018", "2018")
    ])
    branch = SelectField("Branch", choices=[
        ("", "All Branches"), ("CSE", "CSE"), ("AIML", "AIML"),
        ("DS", "DS"), ("IT", "IT"), ("CSBS", "CSBS"), ("ECE", "ECE"),
        ("MECH", "MECH"), ("EEE", "EEE"), ("CE", "CE")
    ])
    submit = SubmitField("Apply Filters")
