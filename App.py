from flask import Flask, render_template, request, redirect, Response, stream_with_context
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import random as r
import time
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///patient.db'
app.config['SQLALCHEMY_BINDS']={'doctor':'sqlite:///doctor.db','appointment':'sqlite:///appointment.db','nurse':'sqlite:///nurse.db'}
db = SQLAlchemy(app)


class Patient(db.Model):
    ## ADD Patient
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(30))
    lastname = db.Column(db.String(30))
    today = db.Column(db.DateTime,default=datetime.utcnow)
    dob = db.Column(db.Date)
    gender = db.Column(db.Enum('Male', 'Female', 'Other'),default='Male')
    blood_group = db.Column(db.Text(3))
    #age = db.Column(db.Numeric(3))
    registered_date = db.Column(db.Date,default=datetime.utcnow)

    ## ADD Contact
    contact = db.Column(db.Integer,default=1000000000)
    email = db.Column(db.Text,default='example@gmail.com')
    address = db.Column(db.Text,default='example address')
    #emergency_contact = db.relationship('Person',backref('person'),lazy=True)

    ## ADD History
    medical_history = db.Column(db.Text)
    current_medications = db.Column(db.Text)
    status = db.Column(db.Enum('Alive','Dead'),default='Alive')
    insurance = db.Column(db.Enum('Yes','No'),default='No')
    disease = db.Column(db.Enum('Yes','No'),default='No')

    def __repr__(self):
        return f"{self.id}"

@app.route('/',methods=['POST','GET'])
def index():
    def generate():
        patients = Patient.query.order_by(Patient.registered_date).all()
        doctors = Doctor.query.order_by(Doctor.id).all()
        appointments = Appointment.query.order_by(Appointment.priority).all()
        yield render_template('index.html',patients = patients,doctors=doctors,appointments=appointments)
    return Response(stream_with_context(generate()), mimetype='text/html')

@app.route('/PatientEntry',methods=['POST','GET'])
def patient():
    if request.method=='POST':
        firstname = request.form['fname']
        lastname = request.form['lname']
        #dob = request.form['dob']
        gender = request.form['gender']
        blood = request.form['blood']

        new_patient = Patient(firstname=firstname,lastname=lastname,gender=gender,blood_group=blood)
        print("Patient created")
        print(new_patient.id)
        #try:
        db.session.add(new_patient)
        db.session.commit()
        print("Commited")
        return redirect('/')
        #except:
            #return "Error in Adding Data to Database"
    else:
        return render_template('PatientEntry.html')

@app.route('/PatientShow/<int:id>',methods=['POST','GET'])
def patientshow(id):
    patient = Patient.query.get_or_404(id)
    if request.method=='POST':
        return redirect('/')
    else:
        return render_template('PatientShow.html',patient=patient)



@app.route('/PatientUpdate/<int:id>',methods=['POST','GET'])
def patientupdate(id):
    patient = Patient.query.get_or_404(id)
    if request.method=='POST':
        patient.firstname = request.form['fname']
        patient.lastname = request.form['lname']
        #patient.dob = request.form['dob']
        patient.gender = request.form['gender']
        patient.blood_group = request.form['blood']

        try:
            db.session.commit()
            return redirect('/')
        except:
            return "Issue in Updating the Patient Details"
    else:
        return render_template('PatientUpdate.html',patient=patient)

@app.route('/Delete/<int:id>')
def deletePatient(id):
    patient = Patient.query.get_or_404(id)
    try:
        db.session.delete(patient)
        db.session.commit()
        return redirect('/')
    except:
        return "Problem in Deleting Data"

def blood():
    temp = r.random()
    if temp<0.35:
        return "O+"
    elif temp<0.48:
        return "O-"
    elif temp<0.78:
        return "A+"
    elif temp<0.86:
        return "A-"
    elif temp<0.88:
        return "B+"
    elif temp<0.96:
        return "B-"
    elif temp<0.99:
        return "AB+"
    else:
        return "AB-"
        
@app.route('/RandomPatient',methods=['POST','GET'])
def randomPatients():
    names=["Vikram","Bhuvan","Sachcith","Ranjith","Advaith","Jashwanth","Raguram","Rahul","Kabilan","Kishore","Naveen","Subash","Cibi","Kushal","Charan","Haldar","Paul","Prajwal","Manas","Doctor","Patient"]
    if request.method=='POST':
        no_of_patients = int(request.form['randnum'])
        for i in range(no_of_patients):
            patient = Patient()
            temp = names[r.randint(0,len(names)-1)]
            patient.firstname = temp
            patient.blood_group = blood()
            patient.contact = r.randint(6000000000,9999999999)
            patient.email = "I.am."+temp+"@gmail.com"
            db.session.add(patient)
            db.session.commit()
        return redirect('/')
    else:
        return redirect('/')

class Doctor(db.Model):
    __bind_key__ = 'doctor'
    id = db.Column(db.Integer,primary_key=True)
    status = db.Column(db.Enum('Yes','No'),default='Yes')
    firstname = db.Column(db.String(30),nullable=False)
    lastname = db.Column(db.String(30))
    gender = db.Column(db.Enum('Male','Female','Other'),default="Male")
    specialization = db.Column(db.String(30),nullable=False)
    contact = db.Column(db.Integer())
    email = db.Column(db.Text)
    #schedule = db.Column(db.Text)
    #assigned_nurses = db.Column(db.Text)
    def __repr__(self):
        return f"{self.id}"

@app.route('/DoctorEntry',methods=['POST','GET'])
def addDoctor():
    if request.method=='POST':
        firstname = request.form['fname']
        lastname = request.form['lname']
        gender = request.form['gender']
        spec = request.form['spec']
        contact = request.form['contact']
        new_doctor = Doctor(firstname=firstname,lastname=lastname,gender=gender,specialization=spec,contact=contact)
        try:
            db.session.add(new_doctor)
            db.session.commit()
            return redirect('/')
        except:
            return "Problem in adding Doctor to Database"
    else:
        return render_template('DoctorEntry.html')

@app.route('/DeleteDoctor/<int:id>')
def deleteDoctor(id):
    doctor = Doctor.query.get_or_404(id)
    try:
        db.session.delete(doctor)
        db.session.commit()
        return redirect('/')
    except:
        return "Problem Deleting Details"

@app.route('/DoctorShow/<int:id>',methods=['POST',"GET"])
def showDoctor(id):
    doctor = Doctor.query.get_or_404(id)
    if request.method=='POST':
        return redirect('/')
    else:
        return render_template('DoctorShow.html',doctor=doctor)
    
@app.route('/DoctorUpdate/<int:id>',methods=['POST','GET'])
def updateDoctor(id):
    doctor = Doctor.query.get_or_404(id)
    if request.method=="POST":
        doctor.firstname = request.form['fname']
        doctor.lastname = request.form['lname']
        doctor.gender = request.form['gen']
        doctor.specialization = request.form['spec']
        doctor.contact = request.form['con']
        doctor.email = request.form['em']
        doctor.status = request.form['stat']
        try:
            db.session.commit()
            return redirect('/')
        except:
            return "Problem in Updating Doctor"
    else:
        return render_template('DoctorUpdate.html',doctor=doctor)
    
@app.route('/RandomDoctor',methods=['POST','GET'])
def randomDoctors():
    names=["Vikram","Bhuvan","Sachcith","Ranjith","Advaith","Jashwanth","Raguram","Rahul","Kabilan","Kishore","Naveen","Subash","Cibi","Kushal","Charan","Haldar","Paul","Prajwal","Manas","Doctor","Patient"]
    special=["Cardio","Neurology","Pedio","Physio"]
    gender = ['Male','Female','Other']
    status = ['Yes','No']
    if request.method=='POST':
        no_of_patients = int(request.form['RandDoc'])
        for i in range(no_of_patients):
            doctor = Doctor()
            temp = names[r.randint(0,len(names)-1)]
            doctor.firstname = temp
            doctor.lastname = "Doctor"
            doctor.specialization = special[r.randint(0,len(special)-1)]
            doctor.contact = r.randint(6000000000,9999999999)
            doctor.email = "I.am."+temp+"@gmail.com"
            doctor.status = status[r.randint(0,1)]
            doctor.gender = gender[r.randint(0,2)]
            db.session.add(doctor)
            db.session.commit()
        return redirect('/')
    else:
        return redirect('/')

A = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 0, 'D', 1, 0, 'D', 1, 0, 'D', 1], [1, 0, 0, 1, 0, 0, 1, 0, 0, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1], [1, 0, 'D', 1, 0, 'D', 1, 0, 'D', 1], [1, 0, 0, 1, 0, 0, 1, 0, 0, 1], [1, 0, 0, 1, 0, 0, 1, 1, 1, 1], [1, 0, 0, 1, 0, 0, 1, 0, 'D', 1], [1, 0, 0, 1, 0, 0, 1, 0, 0, 1], [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]
B = A
class Custom_For_DP:
    def __init__(self,mi):
        self.gen = []
        self.mi = mi


@app.route('/DoctorSearcher',methods=['POST','GET'])
def doctorSearcher():
    length = len(A)
    width = len(A[0])
    if request.method=='POST':
        return redirect('/')
    else:
        return render_template('DoctorSearcher.html',A=A,length=length,width=width,colorthing='red',othercolorthing='white',distance=-1)
    
@app.route('/DoctorSearcherAnimate',methods=['POST','GET'])
def doctorSearcherAnimate():
    length=len(A)
    width=len(A[0])
    if request.method=='POST':
        x = int(request.form['x'])
        m = x//length if x != length*width else x//length-1
        n = x%length-1
        def searchdp(A,m,n,dep,D,dp):
            l = len(A)
            l0 = len(A[0])
            mi = l+l0
            returnClass = Custom_For_DP(mi)
            if m<0 or n<0:
                return Custom_For_DP(l+l0*2)
            if dep>=l+l0:
                return Custom_For_DP(l+l0*2)
            if dp[dep][m][n]!="N":
                returnClass.mi = dp[dep][m][n]
                return returnClass
            if A[m][n]==D:
                dp[dep][m][n] = dep
                returnClass.mi = dp[dep][m][n]
                return returnClass
            if m+1<l and n<l0:
                if A[m+1][n]==1 or A[m+1][n]==D:
                    temp = searchdp(A,m+1,n,dep+1,D,dp)
                    returnClass.gen+=temp.gen
                    returnClass.mi = min(returnClass.mi,temp.mi)
            if m<l and n+1<l0:
                if A[m][n+1]==1 or A[m][n+1]==D:
                    temp = searchdp(A,m,n+1,dep+1,D,dp)
                    returnClass.gen+=temp.gen
                    returnClass.mi = min(returnClass.mi,temp.mi)
            if m-1<l and n<l0:
                if A[m-1][n]==1 or A[m-1][n]==D:
                    temp = searchdp(A,m-1,n,dep+1,D,dp)
                    returnClass.gen+=temp.gen
                    returnClass.mi = min(returnClass.mi,temp.mi)
            if m<l and n-1<l0:
                if A[m][n-1]==1 or A[m][n-1]==D:
                    temp = searchdp(A,m,n-1,dep+1,D,dp)
                    returnClass.gen+=temp.gen
                    returnClass.mi = min(returnClass.mi,temp.mi)
            if dep==0 and returnClass.mi==l+l0:
                print(f"\n{D} not found")
                dp[m][n] = -1
                returnClass.gen.append(dp)#(render_template('DoctorSearcher.html',A=A,length=length,width=width))
                returnClass.mi = dp[dep][m][n]
                return returnClass
            dp[dep][m][n] = returnClass.mi
            returnClass.gen.append(dp)#(render_template('DoctorSearcher.html',A=A,length=length,width=width))
            returnClass.mi = dp[dep][m][n]
            return returnClass
        def generate(m=0,n=0,t=0.4):
            C = A[m][n]
            dp=[[["N"]*(len(A)) for _ in range(len(A[0]))] for j in range(len(A)+len(A[0]))]
            temp = searchdp(A,m,n,0,"D",dp)
            print(len(temp.gen))
            ma = -1
            for i in range(len(A)):
                for j in range(len(A[0])):
                    if A[i][j]==1:
                        A[i][j] = abs(m-i)+abs(n-j)
                        ma = max(ma,A[i][j])
            A[m][n]=len(A)*len(A[0])

            for i in range(ma):
                yield render_template("DoctorSearcher.html",A=A,length=length,width=width,colorthing="white",othercolorthing="red",distance=temp.mi)
                time.sleep(t)
                yield "<script>document.body.innerHTML=''</script>"
                for j in range(len(A)):
                    for k in range(len(A[0])):
                        if A[j][k]!=1 and A[j][k]!=0 and A[j][k]!="D" and not (j==m and k==n):
                            A[j][k]-=1 
            
            ma = -1
            for i in range(len(A)):
                for j in range(len(A[0])):
                    if A[i][j]==1:
                        A[i][j] = abs(m-i)+abs(n-j)
                        ma = max(ma,A[i][j])

            for i in range(len(A)):
                for j in range(len(A[0])):
                    if not (j==m and k==n) and A[i][j]!=0 and A[i][j]!="D":
                        A[i][j]=ma+1-A[i][j]
            A[m][n]=len(A)*len(A[0])
            for i in range(ma-1):
                yield render_template("DoctorSearcher.html",A=A,length=length,width=width,colorthing="red",othercolorthing="white",distance=temp.mi)
                time.sleep(t)
                yield "<script>document.body.innerHTML=''</script>"
                for j in range(len(A)):
                    for k in range(len(A[0])):
                        if A[j][k]!=1 and A[j][k]!=0 and A[j][k]!="D" and not (j==m and k==n):
                            A[j][k]-=1
            yield render_template('DoctorSearcher.html',A=A,length=length,width=width,colorthing="red",othercolorthing="white",distance=temp.mi)
            A[m][n]=C

        return Response(stream_with_context(generate(m,n,0.3)), mimetype='text/html')
    else:
        redirect('/DoctorSearcher')

@app.route('/ResetSearcher',methods=['POST','GET'])
def resetPost():
    if request.method=='POST':
        global B
        return render_template('DoctorSearcher.html',A=B,length=len(A),width=len(A[0]),colorthing="red",othercolorthing="white",distance=-1)
    else:
        return render_template('DoctorSearcher.html',A=A,length=len(A),width=len(A[0]),colorthing="red",othercolorthing="white",distance=-1)

def createMatrix(m,n):
    d = []
    for i in range(m):
        d.append([])
        for j in range(n):
            d[i].append(0)
    return d

def disp(m):
    for i in range(len(m)):
        for j in range(len(m[i])):
            print(m[i][j],end=" ")
        print()

def CreateHospital(A,m,n):
    if m<5 or n<5:
        return A
    if m<8 or n<8:
        for i in range(m):
            A[i][n//2]=1
        A = ver(A,m,n,r.random())
        A = hor(A,m,n,r.random())
        return A
    if m<=n:
        forty = (m*4)//10
        #for j in range(0,m//2+1,min(5,max(3,forty//2))):
        for j in range(0,m-1,min(5,max(3,forty//2))):
            if j!=0:
                for i in range(n):
                    A[m-j-1][i]=1
                for i in range(m):
                    A[i][n-j-1]=1
    else:
        forty = (n*4)//10
        #for j in range(0,n//2+1,min(5,max(3,forty//2))):
        for j in range(0,n-1,min(5,max(3,forty//2))):
            if j!=0:
                for i in range(m):
                    A[i][n-j-1]=1
                for i in range(n):
                    A[m-j-1][i]=1
    A = segment(A,m//2,n//2,0)
    A = CreateHospital(A,m//2+1,n//2+1)
    A = border(A,m//2+1,n//2+1)
    A = ver(A,m,n,r.random())
    A = hor(A,m,n,r.random())
    if m==len(A) and n==len(A[0]):
        A = border(A)
        return corner(A)
    return border(A)

def segment(M,m=None,n=None,v=0):
    if m==None:
        m = len(M)
    if n==None:
        n = len(M[0])

    for i in range(m+1):
        for j in range(n+1):
            M[i][j]=v
    return M

def border(M,x=None,y=None):
    if y==None:
        y = len(M)-1
    if x==None:
        x = len(M[0])-1
    #b = '\u25a2'
    for i in range(y+1):
        M[i][x]=1
        M[i][0]=1
    for i in range(x+1):
        M[y][i]=1
        M[0][i]=1
    return M

def ver(A,m=None,n=None,p=1):
    if m==None:
        m = len(A)
    if n==None:
        n = len(A[0])

    if r.random()<=p:
        for i in range(m):
            a = A[i]
            A[i] = a[n::-1]+a[n+1:]
    return A

def tra(A):
    B = createMatrix(len(A[0]),len(A))
    for i in range(len(A)):
        for j in range(len(A[i])):
            B[j][i]=A[i][j]
    return B

def hor(A,m=None,n=None,p=1):
    if m==None:
        m = len(A)
    if n==None:
        n = len(A[0])

    B = tra(A)
    B = ver(B,n,m,p)
    return tra(B)

def corner(A):
    for i in range(1,len(A)):
        for j in range(len(A[i])-1):
            if A[i-1][j]==1 and A[i-1][j+1]==1 and A[i][j+1]==1 and A[i][j]==0:
                A[i][j]="D"
    return A

@app.route('/RandomHospital',methods=['POST','GET'])
def RandHospital():
    s=request.form['size']
    global A,B
    if not s.isnumeric():
        s = len(A)
    else:
        s = int(s)
    A = CreateHospital(createMatrix(s,s),s,s)
    B = A
    return redirect('/DoctorSearcher')

class Appointment(db.Model):
    __bind_key__ = 'appointment'
    AppId = db.Column(db.Integer,primary_key=True)
    DocId = db.Column(db.Integer)
    PatId = db.Column(db.Integer)
    AppDT = db.Column(db.String(30))
    status =  db.Column(db.Enum('Active','Completed','Incomplete'),default='Incomplete',nullable=True)
    visitReason = db.Column(db.String(40))
    visitType = db.Column(db.String())
    priority = db.Column(db.Integer,default=1)

    def __repr__(self):
        return f"{self.AppId}"

@app.route('/AddAppointment',methods=['POST','GET'])
def addAppointment():
    if request.method=='POST':
        did = request.form['did']
        pid = request.form['pid']
        vreason = request.form['vreason']
        plevel = request.form['plevel']
        new_Appointment = Appointment(DocId=did,PatId=pid,visitReason=vreason,priority=plevel)
        try:
            db.session.add(new_Appointment)
            db.session.commit()
            return redirect('/')
        except:
            return "Problem in adding Doctor to Database"
    else:
        return render_template('AppointmentEntry.html')

@app.route('/AppointmentShow/<int:id>',methods=['POST','GET'])
def showAppointment(id):
    appointment = Appointment.query.get_or_404(id)
    if request.method=='POST':
        return redirect('/')
    else:
        return render_template('AppointmentShow.html',appointment=appointment)

@app.route('/AppointmentUpdate/<int:id>',methods=['POST','GET'])
def updateAppointment(id):
    appointment = Appointment.query.get_or_404(id)
    if request.method=='POST':
        appointment.DocId = request.form['did']
        appointment.PatId = request.form['pid']
        appointment.AppDT = request.form['appdetail']
        appointment.status = request.form['status']
        appointment.visitReason = request.form['vreason']
        appointment.priority = request.form['plevel']
        appointment.visitType = request.form['vtype']
        db.session.commit()
        return redirect('/')
    else:
        return render_template('AppointmentUpdate.html',appointment=appointment)

@app.route('/AppointmentDelete/<int:id>')
def deleteAppointment(id):
    appointment = Appointment.query.get_or_404(id)
    try:
        db.session.delete(appointment)
        db.session.commit()
        return redirect('/')
    except:
        return "Problem in Deleting"

@app.route('/AppointmentDeletePriority',methods=['POST','GET'])
def deletePriority():
    appointment = Appointment.query.order_by(Appointment.priority).first()
    try:
        db.session.delete(appointment)
        db.session.commit()
        return redirect('/')
    except:
        return "Problem in Deleting"
    
class Nurse(db.Model):
    __bind_key__='nurse'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(30))
    did = db.Column(db.Integer)
    status = db.Column(db.Enum('Available','Occupied'),default='Available',nullable=True)

@app.route('/ShowNurse',methods=['POST','GET'])
def showNurse():
    nurses = Nurse.query.order_by(Nurse.id).all()
    if request.method=='POST':
        name = "Nurse"
        status = "Available"
        newNurse = Nurse(name=name,status=status)
        db.session.add(newNurse)
        db.session.commit()
        return redirect('/ShowNurse')
    else:
        return render_template('ShowNurses.html',nurses=nurses)

@app.route('/Home',methods=['POST','GET'])
def Home():
    nurses = Nurse.query.order_by(Nurse.id).all()
    if request.method=='POST':
        return redirect('/')
    else:
        return redirect('/ShowNurse',nurses=nurses)

@app.route('/DeleteNurse',methods=['POST','GET'])
def deleteNurse():
    if request.method=='POST':
        nurse = Nurse.query.order_by(Nurse.id.desc()).first()
        db.session.delete(nurse)
        db.session.commit()
        print("Inside IF")
    return redirect('/ShowNurse')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)