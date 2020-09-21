#---PYTHON Libraries for import--------------------------------------
from flask import Flask, render_template, session, request, redirect, url_for, flash, jsonify
#from flask_mail import Mail, Message #to send an email
#from flask_cors import CORS #avoid cross domain scripting errors
from datetime import datetime
from interfaces.databaseinterface import DatabaseInterface
import interfaces.helpers

#---SETTINGS for the Flask Web Application
#------------------------------------------------------------------
DEBUG = True #sets the level of logging to high
SECRET_KEY = 'my random key can be anything' #this random sequence is required to encrypt Sessions
app = Flask(__name__) #Creates a handle for the Flask Web Server
#CORS(app) #enables cross domain scripting protection
#mail = Mail(app) #creates the smtp server using the Flask web server
app.config.from_object(__name__) #Set app configuration using above SETTINGS
#database = DatabaseHelper('/home/nielbrad/mysite/test.sqlite') #PYTHON ANYWHERE
database = DatabaseHelper('test.sqlite')
database.set_log(app.logger) #set the logger inside the database


#---HTTP REQUESTS / RESPONSES HANDLERS------------------------------------------------------
#Login page
@app.route('/', methods=['GET','POST'])
def login():
    if 'userid' in session:
        return redirect('./home') #no form data is carried across using 'dot/'
    if request.method == "POST":  #if form data has been sent
        email = request.form['email']   #get the form field with the name 
        password = request.form['password']
        userdetails = database.ViewQuery("SELECT * FROM users WHERE email=? AND password=?",(email,password))
        if userdetails:
            row = userdetails[0] #userdetails is a list of dictionaries
            update_access(row['userid']) #calls my custom helper function
            session['userid'] = row['userid']
            session['username'] = row['username']
            session['permission'] = row['permission']
            return redirect('./home')
        else:
            flash("Sorry no user found, password or email incorrect")
    return render_template('login.html')

#homepage is shown once user is logged in
@app.route('/home', methods=['GET','POST'])
def home():
    if 'userid' not in session: #userid hasnt logged in
        return redirect('./')   #need to use the dot to avoid redirecting data
    data=None
    return render_template('home.html', data=data)

# admin page only available to admin - allows admin to update or delete
@app.route('/admin', methods=['GET','POST'])
def admin():
    userdetails = database.ViewQuery('SELECT * FROM users')
    if 'permission' in session: #check to see if session cookie contains the permission level
        if session['permission'] != 'admin':
            return redirect('./')
    else:
        return redirect('/') #user has not logged in
    if request.method == 'POST':
        userids = request.form.getlist('delete') #getlist e.g checkboxes
        for userid in userids:
            if int(userid) > 1:
                database.ModifyQuery('DELETE FROM users WHERE userid = ?',(int(userid),))
        return redirect('./admin')
    return render_template('admin.html', data=userdetails)

# register a new user - Activity for students - create a register page
# When registering, check if user already exists
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == "POST":
        password = request.form['password']
        passwordconfirm = request.form['passwordconfirm']
        if password != passwordconfirm:
            flash("Your passwords do not match")
            return render_template('register.html')
        username = request.form['username']
        #gender = request.form['gender'] #not in database yet, uses drop down list
        location = request.form['location']
        email = request.form['email']
        results = database.ViewQuery('SELECT * FROM users WHERE email = ? OR username =?',(email, username))
        if results:
            flash("Your email or username is already in use.")
            return render_template('register.html')
        database.ModifyQuery('INSERT INTO users (username, password, email, location) VALUES (?,?,?,?)',(username, password, email, location))
        return redirect('./')
    return render_template('register.html')

# Activity for students
# update a current user - activity for students - uses GET to pass a value to a URL
# inside admin page use <a href="{{ url_for('updateuser',userid=row['userid']) }}">Update</a> 
@app.route('/updateuser', methods=['GET','POST'])
def updateuser():
    if request.method == "GET":
        userid = request.values.get('userid')
        #Get the user based on userid and send data to registration page
    return render_template('register.html')

@app.route('/logoff')
def logoff():
    session.clear()
    return redirect('./')

#-----------------------------------------------------------------------#










#---ADVANCED EXAMPLES FOR YEAR 12s-------------------------------------#
#Sample Pages
@app.route('/json', methods=['GET','POST'])
def jsontest():
    if 'userid' not in session: #userid hasnt logged in
        return redirect('./')   #need to use the dot to avoid redirecting data
    data=None
    return render_template('json.html', data=data)

#Bootstrap demo
@app.route('/bootstrap', methods=['GET','POST'])
def bootstrap():
    if 'userid' not in session: #userid hasnt logged in
        return redirect('./')   #need to use the dot to avoid redirecting data
    data=None
    return render_template('bootstrap.html', data=data)

#Turtle demo
@app.route('/turtle', methods=['GET','POST'])
def turtle():
    if 'userid' not in session: #userid hasnt logged in
        return redirect('./')   #need to use the dot to avoid redirecting data
    if request.method == "POST":
        pass
    return render_template('turtle.html')

#---JSON REQUEST EXAMPLES HANDLERS------------------------------------------------#
@app.route('/trighandler', methods=['GET','POST'])
def trighandler():
    c = None
    if request.method == 'POST':
        a = float(request.form.get('sideA'))
        b = float(request.form.get('sideB'))
        c = math.sqrt(a*a + b*b)
    return jsonify({"hypotenuse":c}) #return a python dictionary as JSON - it gets turned into an javascript object in javascript e.g result.hypotenuse 

# JSON handler is continually called to get a list of the recent users
@app.route('/getactiveusers', methods=['GET','POST'])
def getactiveusers():
    if 'userid' in session:
        update_access(session['userid']) #calls my custom helper function
    fmt = "%d/%m/%Y %H:%M:%S"
    users = database.ViewQuery("SELECT username, lastaccess from users")
    activeusers = [] #blank list
    for user in users:
        td = datetime.now() - datetime.strptime(user['lastaccess'],fmt)
        if td.seconds < 120:
            activeusers.append(user['username']) #makes a list of names
    return jsonify({'activeusers':activeusers}) #list of users

# updates the users lastaccess in database
def update_access(userid):
    fmt = "%d/%m/%Y %H:%M:%S"
    datenow = datetime.now().strftime(fmt)
    database.ModifyQuery("UPDATE users SET lastaccess = ?, active = 1 where userid = ?",(datenow, userid))
    return
#------------------------------------------------------------------#

#main method called web server application
if __name__ == '__main__':
    #app.run() #PYTHON ANYTWHERE
    app.run(host='0.0.0.0', port=5000) #runs a local server on port 5000
