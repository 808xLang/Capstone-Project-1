from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, TextAreaField, SelectField
from wtforms.validators import DataRequired, Email, Length


class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class LoginForm(FlaskForm):
    """Login form."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class SearchForm(FlaskForm):
    """Genre"""

    genre = SelectField('Genre',
                         choices=[ ('Drama', "Drama"), ('Comedy', "Comedy"),
                                   ('Fantasy', 'Fantasy'), ('Action', 'Action'), 
                                   ('Shounen', 'Shounen'), ('Isekai', 'Isekai')])
    