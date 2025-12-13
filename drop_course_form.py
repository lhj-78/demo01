
from flask_wtf import FlaskForm
from wtforms import HiddenField, SubmitField

class DropCourseForm(FlaskForm):
    course_id = HiddenField('Course ID')
    submit = SubmitField('退选')
