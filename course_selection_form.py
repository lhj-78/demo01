
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import DataRequired
from models import Course

class CourseSelectionForm(FlaskForm):
    course = SelectField('选择课程', coerce=int, validators=[DataRequired()])
    submit = SubmitField('添加课程')

    def __init__(self, *args, **kwargs):
        super(CourseSelectionForm, self).__init__(*args, **kwargs)
        self.course.choices = [(c.id, f"{c.course_name} ({c.course_code})") for c in Course.query.order_by('course_name').all()]
