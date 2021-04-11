from flask_wtf import FlaskForm
from wtforms import SubmitField, RadioField, SelectField, DecimalField, StringField, PasswordField, IntegerField, TextAreaField, HiddenField
from wtforms.validators import InputRequired, NumberRange, EqualTo, Length
from flask_wtf.file import FileField, FileRequired, FileAllowed

class productCategoryForm(FlaskForm):
    category = RadioField("Category:", default = "All")
    gender = RadioField("Gender:", choices = [("All", "All"), ("Male", "Male"), ("Female", "Female")], default = "All")    
    submit = SubmitField("Submit")

class productOrderPreferencesForm(FlaskForm):
    quantity = IntegerField("Quantity:", default = 1, validators = [InputRequired(), NumberRange(1)])
    size = SelectField("Size:", choices = [("Small", "Small"), ("Medium", "Medium"), ("Large", "Large")])
    submit = SubmitField("Add To Cart")

class customerRegistrationForm(FlaskForm):
    username1 = StringField("Username:", validators = [InputRequired()])
    password1 = PasswordField("Password:", validators = [InputRequired(), Length(8)])
    password1B = PasswordField("Confirm Password:", validators = [InputRequired(), EqualTo("password1")])
    submit1 = SubmitField("Register")

class customerLoginForm(FlaskForm):
    username1 = StringField("Username:", validators = [InputRequired()])
    password1 = PasswordField("Password:", validators = [InputRequired()])
    submit1 = SubmitField("Log In")

class adminLoginForm(FlaskForm):
    username2 = StringField("Username:", validators = [InputRequired()])
    password2 = PasswordField("Password:", validators = [InputRequired()])
    secret_code = PasswordField("Secret Admin Code:", validators = [InputRequired()])
    submit2 = SubmitField("Log In")

class reviewForm(FlaskForm):
    review = TextAreaField("", validators = [InputRequired()])
    rating = RadioField("On a scale of 1 - 5, what would you rate this product?", choices = [(0,0), (1,1), (2,2), (3,3), (4,4), (5,5)], validators = [InputRequired()])
    submit = SubmitField("Submit")

class passwordResetForm(FlaskForm):
    old_password = PasswordField("Enter Current Password:", validators = [InputRequired()])
    new_password = PasswordField("Enter New Password:", validators = [InputRequired()])
    new_password2 = PasswordField("Confirm New Password:", validators = [InputRequired(), EqualTo("new_password")])
    submit1 = SubmitField("Change Password")
     
class updateQuantityForm(FlaskForm):
    id = IntegerField("Enter the product ID", validators = [InputRequired()])
    size = SelectField("Size", validators = [InputRequired()], choices = [("Small", "Small"), ("Medium", "Medium"), ("Large", "Large")])
    quantity = IntegerField("Enter the quantity of new units")
    submit1 = SubmitField("Update")

class removeProductForm(FlaskForm):
    product_id = IntegerField("Enter the product ID", validators = [InputRequired()])
    submit2 = SubmitField("Remove")

class addProductForm(FlaskForm):
    name = StringField("Product Name:", validators = [InputRequired()])
    price = IntegerField("Price:", validators = [InputRequired()])
    description = StringField("Description:", validators = [InputRequired()])
    category = StringField("Category:", validators = [InputRequired()])
    gender = StringField("Gender:", validators = [InputRequired()])
    image = FileField("Select Your Image:", validators = [FileRequired(), FileAllowed(["png", "jpg", "jpeg"], "Only '.png' '.jpg' and '.jpeg' image formats are accepted.")])
    submit3 = SubmitField("Add Product")

class sendMessageForm(FlaskForm):
    message = TextAreaField("",validators = [InputRequired()] )
    submit2 = SubmitField("Submit")

class adminSendMessageForm(FlaskForm):
    message = TextAreaField("", validators = [InputRequired()])
    recipient = StringField("Recipient:", validators = [InputRequired()])
    submit = SubmitField("Submit")

class indexMens(FlaskForm):
    gender = HiddenField("Gender")
    category = HiddenField("Category")
    submit = SubmitField("Shop Now")

class indexWomens(FlaskForm):
    gender = HiddenField("Gender")
    category = HiddenField("Category")
    submit = SubmitField("Shop Now")