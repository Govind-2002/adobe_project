from flask import Flask, redirect, render_template,flash,request
from flask.globals import request
from flask.helpers import url_for
from flask_login import UserMixin
from flask_login import login_required, logout_user, login_user, login_manager, LoginManager, current_user
from werkzeug.security import generate_password_hash,check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from flask_mail import Mail
import json
import uuid

local_server=True
app=Flask(__name__)
app.secret_key="jaiho"


login_manager=LoginManager(app)
login_manager.login_view='login'
#app.config[]
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://root:@localhost/hospital management system"
db=SQLAlchemy(app)


@login_manager.user_loader
def load_user(user_id):     
    # Assuming user IDs are unique across both Patient and Doctor models
    patient = Patient.query.get(user_id)
    if patient:
        return patient
    else:
        return Doctor.query.get(user_id)



class Patient(UserMixin, db.Model):
    __tablename__ = 'patient'
    id = db.Column(db.String(50), primary_key=True)
    password = db.Column(db.String(1000), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    address = db.Column(db.String(60), nullable=False)
    gender = db.Column(db.String(20), nullable=False)

class Appointment(UserMixin, db.Model):
    __tablename__ = 'appointment'
    id = db.Column(db.String(100), primary_key=True)
    date = db.Column(db.Date, nullable=False)
    slot=db.Column(db.Integer, nullable=False)
    docid = db.Column(db.String(100), nullable=False)
    patid = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(15), nullable=False) 

  

class Doctor(UserMixin, db.Model):
    __tablename__ = 'doctor'
    id = db.Column(db.String(50), primary_key=True)
    gender = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(1000), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    
class MedicalHistory(db.Model):
    __tablename__ = 'medicalhistory'
    id = db.Column(db.String(100), primary_key=True)
    date = db.Column(db.Date, nullable=False)
    conditions = db.Column(db.String(100), nullable=False)
    surgeries = db.Column(db.String(100), nullable=False)
    medication = db.Column(db.String(100), nullable=False)
    pat_id = db.Column(db.String(50))



@app.route("/kuchtohai")
def kuchtohai():
    return render_template("kuchtohai.html")
    
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/patientlogin")
def patientlogin():
    return render_template("patientlogin.html")

@app.route("/basesignup")
def basesignup():
    return render_template("basesignup.html")

@app.route("/doclogin")
def doclogin():
    return render_template("doclogin.html")

@app.route("/docsignup")
def docsignup():
    return render_template("docsignup.html")

@app.route('/signup', methods=['POST','GET'])
def signup():
    if request.method=="POST":
        name=request.form.get('name')
        email=request.form.get('email')
        password=request.form.get('password')
        address=request.form.get('address')
        gender=request.form.get('gender')
        print(name, email, password)
        encapwd=generate_password_hash(password)
        emailuser=Patient.query.filter_by(id=email).first()
        if emailuser:
            flash("user already exists", "warning")
            return render_template("basesignup.html")
        
        new_patient = Patient(id=email, password=encapwd, name=name, address=address, gender=gender)
        db.session.add(new_patient)
        db.session.commit()
        flash("user added","info")
        return render_template("basepatientlogin.html")
  
        

@app.route('/login', methods=['POST','GET'])
def login():
    if request.method=="POST":
        email=request.form.get('email')
        password=request.form.get('password')
        user=Patient.query.filter_by(id=email).first()
        #print(check_password_hash(user.password,password))
        if user and check_password_hash(user.password,password):
            login_user(user)
            return render_template("kuchtohai.html")
        else:
            flash("INVALID CREDENTIAL","danger")
            return render_template("basepatientlogin.html")
        
    return render_template("basepatientlogin.html")       
  
  
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("logout successful", "warning")
    return redirect(url_for('login'))

@app.route('/doctorsignup', methods=['POST','GET'])
def doctorsignup():
    if request.method=="POST":
        name=request.form.get('name')
        email=request.form.get('email')
        password=request.form.get('password')
        gender=request.form.get('gender')
        encapwd=generate_password_hash(password)
        emailuser=Doctor.query.filter_by(id=email).first()
        if emailuser:
            flash("try with another id", "warning")
            return render_template("docsignup.html")
        
        new_patient = Doctor(id=email, password=encapwd, name=name, gender=gender)
        db.session.add(new_patient)
        db.session.commit()
        flash("user added","info")
        return render_template("doclogin.html")
@app.route('/afterdoclogin')
def afterdoclogin():
    return render_template("afterdoclogin.html")


@app.route('/doctorlogin', methods=['POST','GET'])
def doctorlogin():
    if request.method=="POST":
        email=request.form.get('email')
        password=request.form.get('password')
        user=Doctor.query.filter_by(id=email).first()
        #print(check_password_hash(user.password,password))
        if user and check_password_hash(user.password,password):
            login_user(user)
            return redirect(url_for("afterdoclogin"))
        else:
            flash("INVALID CREDENTIAL","danger")
            return render_template("doclogin.html")
        
    return render_template("doclogin.html")  

@app.route('/medical_history')
def medical_history():
    return render_template("medical_history.html")


@app.route('/viewmedhistorypatient')
def viewmedhistorypatient():
    user_id = current_user.id  # Example user ID, replace with actual user ID
    medical_history = MedicalHistory.query.filter_by(pat_id=user_id).all()

    return render_template("viewmedhistorypatient.html", medical_history=medical_history)





a=30
@app.route('/submit_medical_history', methods=['POST'])
def submit_medical_history():
    if request.method == 'POST':
        #id = request.form['id']  # Assuming 'id' is the name of the input field in the form
        date = request.form['date']
        conditions = request.form['conditions']
        surgeries = request.form['surgeries']
        medication = request.form['medication']
        uid=uuid.uuid4()
       
        new_medical_history = MedicalHistory(id=uid, date=date, conditions=conditions, surgeries=surgeries, medication=medication, pat_id=current_user.id)
        
        
        db.session.add(new_medical_history)
        
        db.session.commit()
        
        return redirect("/viewmedhistorypatient")

    


@app.route("/test")
def patient():
    try:
        a=Patient.query.all()
        print(a)
        return 'my database connected'
    except Exception as e:
       return f'not connected {e}'
   
@app.route("/getappointment", methods=['POST'])
@login_required
def getappointment():
    if request.method == 'POST':
        docid = request.form['docid']
        date = request.form['date']
        appointmentm=request.form['appointment']
        appointmentm=Appointment.query.filter_by(id=appointmentm).first()
        totalslot=[i for i in range(1,17)]
        appointments = Appointment.query.filter_by(docid=docid, date=date).all()
        booked_slot= [appointment.slot for appointment in appointments]
        slots_avail=[x for x in totalslot if x not in booked_slot]
        print(slots_avail)
        slot_times = {
                1: "9:00 AM - 9:30 AM",
                2: "9:30 AM - 10:00 AM",
                3: "10:00 AM - 10:30 AM",
                4: "10:30 AM - 11:00 AM",
                5: "11:00 AM - 11:30 AM",
                6: "11:30 AM - 12:00 PM",
    # Break from 12:00 PM to 3:00 PM
                7: "3:00 PM - 3:30 PM",
                8: "3:30 PM - 4:00 PM",
                9: "4:00 PM - 4:30 PM",
                10: "4:30 PM - 5:00 PM",
                11: "5:00 PM - 5:30 PM",
                12: "5:30 PM - 6:00 PM",
                13: "6:00 PM - 6:30 PM",
                14: "6:30 PM - 7:00 PM",
                15: "7:00 PM - 7:30 PM",
                16: "7:30 PM - 8:00 PM",
    # Add more slot times as needed
                 }

        if appointmentm:
            print("sending ",appointmentm)
            return render_template("slots.html", slots_avail=slots_avail, date=date, docid=docid, slot_times=slot_times, appointmentm=appointmentm)

        return render_template("slots.html", slots_avail=slots_avail, date=date, docid=docid, slot_times=slot_times)

@app.route("/submitappointment", methods=['POST'])
@login_required
def submitappointment():
    print("stage1")
    if request.method == 'POST':
        print("stage2")
        slot = request.form['slot']
        docid = request.form['docid']
        date = request.form['date']
        aptid=request.form['appointmentm']
        apt = Appointment.query.filter_by(id=aptid).first()
        print(apt)
        if apt:   
            print("stage3")
            apt.date=date
            apt.slot=slot
            apt.docid=docid
            apt.patid=current_user.id
            apt.status="Not Done"
            db.session.commit()
            return redirect("/viewappointment")
        else:   
           uid=uuid.uuid4()
           print("stage unknown")
           new_medical_history = Appointment(id=uid, date=date, slot=slot, docid=docid, patid=current_user.id, status="Not Done")
        
        
           db.session.add(new_medical_history)
        
           db.session.commit()
           return redirect("/viewappointment")
    print("failed")
    
    
@app.route('/viewappointment')
@login_required

def viewappointment():
    user_id = current_user.id  # Example user ID, replace with actual user ID
    appt = Appointment.query.filter_by(patid=user_id).all()

    return render_template("viewappointment.html", appt=appt)



@app.route("/appointment")
@login_required
def appointment():
    return render_template("appointment.html")

@app.route('/update_appointment/<string:appointment_id>', methods=['get'])
def update_appointment(appointment_id):
    # Get the appointment with the specified ID from the database
        appointment = Appointment.query.get_or_404(appointment_id)
        
    # Render the update form (you can replace 'update_appointment.html' with your actual template)
        return render_template('appointment.html', appointment=appointment)




@app.route('/delete_appointment/<string:appointment_id>', methods=['POST'])
def delete_appointment(appointment_id):
    # Get the appointment with the specified ID from the database
    appointment = Appointment.query.filter_by(id=appointment_id).first()

    # Delete the appointment from the database
    db.session.delete(appointment)
    db.session.commit()
    return redirect("/viewappointment")

@app.route('/docviewappointment')

def docviewappointment():
    user_id = current_user.id  # Example user ID, replace with actual user ID
    appt = Appointment.query.filter_by(docid=user_id).all()

    return render_template("docviewappointment.html", appt=appt)


app.run(debug=True)
