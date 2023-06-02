from flask_wtf import FlaskForm
from models import Fcuser
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, EqualTo, NumberRange
from wtforms.fields import IntegerField

class RegisterForm(FlaskForm):
    userid = StringField('userid', validators=[DataRequired()])
    username = StringField('username', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired(), EqualTo('re_password')])
    re_password = PasswordField('re_password', validators=[DataRequired()])


class LoginForm(FlaskForm):
    class UserPassword(object):
        def __init__(self, message=None):
            self.message = message
        def __call__(self,form,field):
            userid = form['userid'].data
            password = field.data
            fcuser = Fcuser.query.filter_by(userid=userid).first()
            if fcuser.password != password:
                # raise ValidationError(message % d)
                raise ValueError('Wrong password')
        
    userid = StringField('userid', validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired(), UserPassword()]) 


class BuyCoinForm(FlaskForm):
    coin_quantity = IntegerField('coin_quantity', validators=[DataRequired(), NumberRange(min=1)])


class IncreaseBalanceForm(FlaskForm):
    amount_to_increase = IntegerField('입금할 금액', validators=[DataRequired(), NumberRange(min=1)])


class DecreaseBalanceForm(FlaskForm):
    amount_to_decrease = IntegerField('출금할 금액', validators=[DataRequired(), NumberRange(min=1)])