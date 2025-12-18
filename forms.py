from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

class EventForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    start_time = DateTimeField("Start Time (YYYY-MM-DD HH:MM)", validators=[DataRequired()])
    end_time = DateTimeField("End Time (YYYY-MM-DD HH:MM)", validators=[DataRequired()])
    description = TextAreaField("Description")
    submit = SubmitField("Save")

class ResourceForm(FlaskForm):
    name = StringField("Resource Name", validators=[DataRequired()])
    type = StringField("Resource Type", validators=[DataRequired()])
    submit = SubmitField("Save")
