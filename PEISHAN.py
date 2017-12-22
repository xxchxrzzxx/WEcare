from flask import Flask, render_template, request, flash, redirect, url_for,session
from wtforms import Form, StringField, SelectField, IntegerField, DateTimeField, RadioField, validators, PasswordField, FileField, TextField
from wtforms.fields.html5 import EmailField
from flask_wtf.file import FileField,FileAllowed
#PS
from Doctor import Doctor
from Instructor import Instructor
from Register import Register
from Login import Login

#----start----
import firebase_admin
from firebase_admin import credentials, db
cred = credentials.Certificate('cred/booking-b814e-firebase-adminsdk-j8prf-51aedf5eb9.json')
default_app = firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://booking-b814e.firebaseio.com/'
})
root = db.reference()
#----end-----

app = Flask(__name__)

#-----------------------------------------------------------------------------------------------------------------------------------
#Indicate what's needed for that form; for radio field
class RequiredIf(object):
    def __init__(self, *args, **kwargs):
        self.conditions = kwargs

    def __call__(self, form, field):
        for name, data in self.conditions.items():
            if name not in form._fields:
                validators.Optional()(field)
            else:
                condition_field = form._fields.get(name)
                if condition_field.data == data:
                    validators.DataRequired().__call__(form, field)
                else:
                    validators.Optional().__call__(form, field)
# -----------------------------------------------------------------------------------------------------------------------------------
class LoginForm(Form):
    accountType = RadioField('Account Type', [validators.DataRequired()],
                             choices=[('iuser', 'User'), ('idoctor', 'Doctor'),
                                      ('iinstructor', 'Instructor')], default="iuser")
    username = StringField('Username', [validators.DataRequired('Invalid Username')])
    password = PasswordField('Password', [validators.DataRequired('Invalid Password')])


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    #get username / password
    username = form.username.data
    password = form.password.data
    accounts = root.child('accounts').get()
    list = []
    for accountid in accounts:

        eachaccount = accounts[accountid]

        if eachaccount['account type'] == 'iuser' or eachaccount['account type'] == 'idoctor' or eachaccount[
            'account type'] == 'iinstructor':
            account = Login(eachaccount['account type'], eachaccount['username'], eachaccount['password'])
            account.set_registerid(accountid)
            list.append(account)
#---------------------------------------------------------
#--------------------------------------------------------
    if request.method == 'POST' and form.validate():
        username_list = []
        password_list = []
        while True:
            for result in list:
                username_list.append(result.get_username())
                password_list.append(result.get_password())
            print(username_list)
            print(password_list)
            break
        if username in username_list and password in password_list:
            if username_list.index(username) == password_list.index(password):
                session['logged_in'] = True
                return redirect(url_for('view_Booking_Page'))

        else:
            error = 'Invalid login'
            flash(error,'danger')
            return render_template('login.html',form=form)


        # print("Username:",account.get_username())
        # print("Password:",account.get_password())
        # if username == account.get_username() and password == account.get_password():
        #     session['logged_in'] = True
        #     return redirect(url_for('view_Booking_Page'))
        # else:
        #     error = 'Invalid login'
        #     flash(error,'danger')
        #     return render_template('login.html',form=form)
    return render_template('login.html', form=form)
#------------------------------------------------------------
#----------------------------------------------------
@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))
#-----------------------------------------------------------------------------------------------------------------
class signup(Form):
    accountType = RadioField('Account Type', [validators.DataRequired()],
                          choices=[('iuser', 'User'), ('idoctor', 'Doctor'),
                                   ('iinstructor', 'Instructor')], default="iuser")
    username = StringField('Username', [validators.DataRequired('Please enter your username')])
    password = PasswordField('Password', [validators.DataRequired('Password is required.'),validators.Length(min=6)])


@app.route('/signup',methods=["GET","POST"])
def register():
    form = signup(request.form)
    if request.method == 'POST' and form.validate():
        if form.accountType.data == "iuser" or form.accountType.data == "idoctor" or form.accountType.data == "iinstructor":
            accountType = form.accountType.data
            username = form.username.data
            password = form.password.data


            user = Register(accountType,username,password)

            user_db = root.child('accounts')
            user_db.push({
                'account type':user.get_accountType(),
                'username': user.get_username(),
                'password':user.get_password(),
            })

            # flash("Hello"+user.get_username(),"success")

        return redirect(url_for('login'))
    return render_template('register.html', form=form)

























































































# View Booking Page  AKA VIEW_ALL_PUBLICATIONS.html
@app.route('/view_Booking_Page')
def view_Booking_Page():
    bookings = root.child('bookings').get()
    list = [] #store booking objects
    for typeid in bookings:

        eachbooking = bookings[typeid]

        if eachbooking['type'] == 'idoctor':
            doctor = Doctor(eachbooking['name'],eachbooking['age'],
                            eachbooking['phoneNumber'],eachbooking['email'],
                            eachbooking['startingDateAndTime'],eachbooking['type'],
                            eachbooking['specialization1'])
            doctor.set_typeid(typeid)
            print(doctor.get_typeid())
            list.append(doctor)
        elif eachbooking['type'] == 'iinstructor':
            instructor = Instructor(eachbooking['name'],eachbooking['age'],
                            eachbooking['phoneNumber'],eachbooking['email'],
                            eachbooking['startingDateAndTime'],eachbooking['type'],
                            eachbooking['specialization2'])
            instructor.set_typeid(typeid)
            print(instructor.get_typeid())
            list.append(instructor)
        else:
            flash("You have no appointments.")
    return render_template('viewBookingPage.html',bookings = list)


class bookingPage(Form):#aka class PublicationForm(Form)
    type = RadioField('Choose type  ',[validators.DataRequired("Please choose one")],choices=[('idoctor','Doctor'),('iinstructor','Instructor')],default="idoctor")
    name = StringField("Name (Mr/Ms/Madam) ",[validators.Length(min=1,max=150),validators.DataRequired("Please enter your name")],default="Bojack Horseman")
    age = IntegerField("Age ",[validators.DataRequired("Please enter your age")],default=54)
    phoneNumber = StringField("Number ",[validators.DataRequired("Please enter your contact number"),validators.length(min=8,max=8)],default="81345678") #kiv,will validate to sg number format
    email = EmailField("Email ", [validators.DataRequired("Please enter your email"), validators.Email()],default="BoforGoJack@gmail.com")
    specialization1 = SelectField("Specialization(Doctors) ",[RequiredIf(type="idoctor")],choices=[("","Please Select:"),
                                                                                                   ("Anesthesiologist","Anesthesiologist"),
                                                                                                   ('Allergist',"Allergist"),
                                                                                                   ("Audiologist","Audiologist"),
                                                                                                   ('Cardiologist','Cardiologist'),
                                                                                                   ('Dentist','Dentist')],
                                                                                                    default="")
    specialization2 =SelectField("Specialization(Instructors) ",[RequiredIf(type="iinstructor")],choices=[("","Please Select:"),
                                                                                                          ("Yoga","Yoga"),
                                                                                                          ("Zumba","Zumba"),
                                                                                                          ("Kardio","Kardio"),
                                                                                                          ("Kickbox","Kickbox"),
                                                                                                          ("Dance","Dance")],
                                                                                                           default="")
    # startingDateAndTime = DateTimeField("Starting Date & Time ",[validators.DataRequired()], format='%Y-%m-%d %H:%M:%S')
    startingDateAndTime = StringField("Starting Date & Time ", [validators.DataRequired()])
    #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #credit card page
    cardType = RadioField('Payment Details  ',[validators.DataRequired("Please enter your card type")],choices=[('ivisa','Visa'),('imastercard','Master Card'),('iamericanexpress','American Express')],default="ivisa")
    cardName = StringField("Card Name ",[validators.Length(min=1,max=150),validators.DataRequired("Please enter your card name")])
    cardNumber = StringField("Card Number ",[validators.DataRequired("Please enter your card number"),validators.length(min=16,max=16)])
    expirationMonth = SelectField("Expiration Date ",[validators.DataRequired("Please enter the expiry month")],choices=[("","Please Select:"),
                                                                                       ("January","January"),
                                                                                       ("February", "Febuary"),
                                                                                       ("March", "March"),
                                                                                       ("April", "April"),
                                                                                       ("May","May"),
                                                                                       ("June","June"),
                                                                                       ("July","July"),
                                                                                       ("August","August"),
                                                                                       ("September","September"),
                                                                                       ("October","October"),
                                                                                       ("November","November"),
                                                                                       ("December","December")],
                                                                                        default="")
    expirationYear = SelectField("Expiration Year ",[validators.DataRequired("Please enter the expiry year")],choices=[("","Please Select:"),
                                                                                       ("2017","2017"),
                                                                                       ("2018", "2018"),
                                                                                       ("2019", "2019"),
                                                                                       ("2020", "2020"),
                                                                                       ("2021","2021"),
                                                                                       ("2022","2022"),
                                                                                       ("2023","2023")],
                                                                                        default="")
    cvcode = StringField("Card CV ",[validators.DataRequired("Please enter your CV code"),validators.length(min=3,max=3)])


@app.route('/bookingPage',methods=["GET","POST"]) #@app.route('/newpublication')
def bookingpage():
    form = bookingPage(request.form)
    if request.method == 'POST' and form.validate():
        if form.type.data == "idoctor":
            name = form.name.data
            age = form.age.data
            phoneNumber = form.phoneNumber.data
            email = form.email.data
            specialization1 = form.specialization1.data
            startingDateAndTime = form.startingDateAndTime.data
            type = form.type.data

            doctor = Doctor(name,age,phoneNumber,email,startingDateAndTime,type,specialization1)

            book_db = root.child('bookings')

            book_db.push({
                'name': doctor.get_name(),
                'age': doctor.get_age(),
                'phoneNumber': doctor.get_phoneNumber(),
                'email': doctor.get_email(),
                'startingDateAndTime': doctor.get_startingDateAndTime(),
                'type': doctor.get_type(),
                'specialization1': doctor.get_specialization1(),
            })
            flash("Your appointment is registered.", 'success')

        elif form.type.data == "iinstructor":
            name = form.name.data
            age = form.age.data
            phoneNumber = form.phoneNumber.data
            email = form.email.data
            specialization2 = form.specialization2.data
            startingDateAndTime = form.startingDateAndTime.data
            type = form.type.data

            instructor = Instructor(name,age,phoneNumber,email,startingDateAndTime,type,specialization2)

            book_db = root.child('bookings')
            book_db.push({
                'name' : instructor.get_name(),
                'age' : instructor.get_age(),
                'phoneNumber' : instructor.get_phoneNumber(),
                'email' : instructor.get_email(),
                'startingDateAndTime' : instructor.get_startingDateAndTime(),
                'type' : instructor.get_type(),
                'specialization2' : instructor.get_specialization2()
            })

            flash('Your appointment is registered.', 'success')

        return redirect(url_for('view_Booking_Page'))
        # return render_template('view_Booking_Page.html',form=form)
    return render_template('BookingPage.html', form=form)


#update/ change date and time aka update_publications
@app.route('/update/<string:id>/',methods=['GET','POST'])
def update_bookings(id):
    form = bookingPage(request.form)
    if request.method == 'POST' and form.validate():
        if form.type.data == "idoctor":
            name = form.name.data
            age = form.age.data
            phoneNumber = form.phoneNumber.data
            email = form.email.data
            specialization1 = form.specialization1.data
            startingDateAndTime = form.startingDateAndTime.data
            type = form.type.data

            doctor = Doctor(name,age,phoneNumber,email,startingDateAndTime,type,specialization1)

            book_db = root.child('bookings/'+id)

            book_db.set({
                'name': doctor.get_name(),
                'age': doctor.get_age(),
                'phoneNumber': doctor.get_phoneNumber(),
                'email': doctor.get_email(),
                'startingDateAndTime': doctor.get_startingDateAndTime(),
                'type': doctor.get_type(),
                'specialization1': doctor.get_specialization1(),
            })

            flash("Your appointment has been rescheduled", 'success')

        elif form.type.data == "iinstructor":
            name = form.name.data
            age = form.age.data
            phoneNumber = form.phoneNumber.data
            email = form.email.data
            specialization2 = form.specialization2.data
            startingDateAndTime = form.startingDateAndTime.data
            type = form.type.data

            instructor = Instructor(name,age,phoneNumber,email,startingDateAndTime,type,specialization2)

            book_db = root.child('bookings/'+id)

            book_db.set({
                'name' : instructor.get_name(),
                'age' : instructor.get_age(),
                'phoneNumber' : instructor.get_phoneNumber(),
                'email' : instructor.get_email(),
                'startingDateAndTime' : instructor.get_startingDateAndTime(),
                'type' : instructor.get_type(),
                'specialization2' : instructor.get_specialization2(),
            })

            flash('Your appointment has been rescheduled.', 'success')

        return redirect(url_for('view_Booking_Page'))
    else:
        url = 'bookings/' + id
        eachbook = root.child(url).get()

        if eachbook['type'] == 'idoctor':
            doctor = Doctor(eachbook['name'],eachbook['age'],
                            eachbook['phoneNumber'],eachbook['email'],
                            eachbook['startingDateAndTime'],eachbook['type'],
                            eachbook['specialization1'])
            doctor.set_typeid(id)
            form.name.data = doctor.get_name()
            form.age.data = doctor.get_age()
            form.phoneNumber.data = doctor.get_phoneNumber()
            form.email.data = doctor.get_email()
            form.specialization1.data = doctor.get_specialization1()
            form.startingDateAndTime.data = doctor.get_startingDateAndTime()
            form.type.data = doctor.get_type()

        else:
            instructor = Instructor(eachbook['name'], eachbook['age'],
                                    eachbook['phoneNumber'], eachbook['email'],
                                    eachbook['startingDateAndTime'], eachbook['type'],
                                    eachbook['specialization2'])
            instructor.set_typeid(id)
            form.name.data = instructor.get_name()
            form.age.data = instructor.get_age()
            form.phoneNumber.data = instructor.get_phoneNumber()
            form.email.data = instructor.get_email()
            form.specialization2.data = instructor.get_specialization2()
            form.startingDateAndTime.data = instructor.get_startingDateAndTime()
            form.type.data = instructor.get_type()
        return render_template('updateBookingPage.html',form=form)
    # return redirect(url_for("view_Booking_Page"))
#cancel appointment
@app.route('/delete_bookings/<string:id>',methods = ['POST'])
def delete_booking(id):
    book_db = root.child('bookings/'+id)
    book_db.delete()
    flash('Appoinment Cancelled','success')

    return redirect(url_for('view_Booking_Page'))

if __name__ == '__main__':
    app.secret_key = "helloworld"
    app.run()