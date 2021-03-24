from covid_india import states
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, session
import re
import sqlite3
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import pandas as pd
from sklearn.cluster import AgglomerativeClustering
import matplotlib.pyplot as plt

stats = states.getdata()
df = pd.DataFrame(stats)
#print(df.columns)
app = Flask(__name__)
print(df.columns)
@app.route("/")
def homepage():
  return render_template("homepage.html", df=df)

@app.route("/public_signup", methods =['GET', 'POST'])
def public_signup():
  msg = ''
  if request.method == 'POST' and 'name' in request.form and 'email' in request.form and 'age' in request.form and 'address' in request.form and 'adhaar' in request.form:
    name = request.form['name']
    email = request.form['email']
    age = request.form['age']
    address = request.form['address']
    adhaar = request.form['adhaar']
    locator = Nominatim(user_agent="myGeocoder")
    geocode = RateLimiter(locator.geocode, min_delay_seconds=1)
    l = geocode(address)
    connection = sqlite3.connect("bharan.db")
    c = connection.cursor()
    regex = "^[2-9]{1}[0-9]{3}\\s[0-9]{4}\\s[0-9]{4}$"
    p = re.compile(regex)
    if not name or not email or not age or not address or not adhaar:
      msg = 'Please fill out the form!'
    elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
      msg = 'Invalid email address!'
    elif age < '18':
      msg = 'Not an Adult!'
    elif not re.search(p, adhaar):
      msg = "Invalid Aadhaar Number"
    else:
      try:
        c.execute('insert into citizen(name, email, age, address, aadhar, longitude, latitude) values(?, ?, ?, ?, ?, ?, ?)',(name, email, int(age), address, adhaar, l.longitude, l.latitude,))
        c.execute('select uid from citizen where email = ?',[email])
        uid = c.fetchone()
        msg = 'Registered Successfully! Uid is ' + str(uid[0]) + '!'
      except Exception:
        c.execute('select uid from citizen where email = ?',[email])
        uid = c.fetchone()[0]
        msg = "Already Registered. Uid is " + str(uid[0]) + '!'
      connection.commit()
  elif request.method == 'POST':
    msg = 'Please fill out the form!'
  return render_template("public_signup.html", msg=msg)

@app.route("/hospital_add", methods =['GET', 'POST'])
def hospital_add():
  msg = ''
  if request.method == 'POST' and 'hid' in request.form and 'hname' in request.form and 'snumber' in request.form and 'bnumber' in request.form:
    hid = request.form['hid']
    hname = request.form['hname']
    snumber = request.form['snumber']
    bnumber = request.form['bnumber']
    connection = sqlite3.connect("bharan.db")
    c = connection.cursor()
    regex = "^[A-Z]{2}[0-9]{8}$"
    regex1 = "^[0-9]{10}$"
    q = re.compile(regex1)
    p = re.compile(regex)
    if not hid or not hname or not snumber or not bnumber:
      msg = 'Please fill out the form!'
    elif not re.search(q, snumber):
      msg = "Invalid Serial Number!"
    elif not re.search(p, bnumber):
      msg = "Invalid Batch Number!"
    else:
      try:
        c.execute('insert into vaccinestock(hid, hname, snumber, bnumber) values(?,?,?,?)',(hid, hname, snumber, bnumber,))
        msg = 'Vaccine Added!'
      except Exception:
        msg = "Vaccine Already Added!"
      connection.commit()
  elif request.method == 'POST':
    msg = 'Please fill out the form!'
  return render_template("hospital_add.html", msg=msg)

@app.route("/hospital_order", methods =['GET', 'POST'])
def hospital_order():
  msg = ''
  if request.method == 'POST' and 'hid' in request.form and 'hname' in request.form and 'qnumber' in request.form:
    hid = request.form['hid']
    hname = request.form['hname']
    qnumber = request.form['qnumber']
    connection = sqlite3.connect("bharan.db")
    c = connection.cursor()
    if not hid or not hname or not qnumber:
      msg = 'Please fill out the form!'
    elif qnumber <= 0:
      msg = "Invalid Quantity!"
    else:
      try:
        c.execute('insert into vaccineorder(hid, hname, qnumber) values(?,?,?)',(hid, hname, qnumber,))
        msg = 'Order Placed!'
      except Exception:
        c.execute('select qnumber from vaccineorder where hid = ?',[hid])
        q = c.fetchone()[0]
        c.execute('update vaccineorder set qnumber=? where hid=?',(str(int(q)+int(qnumber)), hid))
        msg = "Vaccine Already Added!"
      connection.commit()
  elif request.method == 'POST':
    msg = 'Please fill out the form!'
  return render_template("hospital_order.html", msg=msg)

@app.route("/hospital_remove", methods =['GET', 'POST'])
def hospital_remove():
  msg = ''
  if request.method == 'POST' and 'hid' in request.form and 'hname' in request.form and 'snumber' in request.form and 'bnumber' in request.form:
    hid = request.form['hid']
    hname = request.form['hname']
    snumber = request.form['snumber']
    bnumber = request.form['bnumber']
    connection = sqlite3.connect("bharan.db")
    c = connection.cursor()
    regex = "^[A-Z]{2}[0-9]{8}$"
    regex1 = "^[0-9]{10}$"
    q = re.compile(regex1)
    p = re.compile(regex)
    if not hid or not hname or not snumber or not bnumber:
      msg = 'Please fill out the form!'
    elif not re.search(q, snumber):
      msg = "Invalid Serial Number!"
    elif not re.search(p, bnumber):
      msg = "Invalid Batch Number!"
    else:
      try:
        c.execute('delete from vaccinestock where snumber=(?)',[snumber])
        c.execute('insert into vaccineused(hid, hname, snumber, bnumber) values(?,?,?,?)',(hid, hname, snumber, bnumber,))
        msg = 'Vaccine Used!'
      except Exception:
        msg = "Vaccine Already Used!"
      connection.commit()
  elif request.method == 'POST':
    msg = 'Please fill out the form!'
  return render_template("hospital_remove.html", msg=msg)

@app.route("/hospital_done", methods =['GET', 'POST'])
def hospital_done():
  msg = ''
  if request.method == 'POST' and 'uid' in request.form:
    uid = request.form['hid']
    connection = sqlite3.connect("bharan.db")
    c = connection.cursor()
    regex = "^[0-9]+$"
    p = re.compile(regex)
    if not uid:
      msg = 'Please fill out the form!'
    elif not re.search(p, uid):
      msg = "Invalid User Number!"
    else:
      try:
        c.execute("select uid from citizen where uid = ?",[uid])
        row = c.fetchone()
        c.execute("insert into citizenvaccinated values(?,?,?,?,?,?)",(row['uid'], row['name'], row['email'], row['age'], row['address'], row['aadhar']))
        msg = 'Vaccine Used!'
      except Exception:
        msg = "Vaccine Already Used!"
      connection.commit()
  elif request.method == 'POST':
    msg = 'Please fill out the form!'
  return render_template("hospital_done.html", msg=msg)

@app.route("/hospital")
def hospital():
  return render_template("hospitals.html")

@app.route("/manufacture")
def manufacture():
  return render_template("manufacture.html")

@app.route("/manufacture_add", methods =['GET', 'POST'])
def manufacture_add():
  msg=""
  if request.method == 'POST' and 'mid' in request.form and 'snumber' in request.form and 'bnumber' in request.form:
    mid=request.form['mid']
    snumber= request.form['snumber']
    bnumber= request.form['bnumber']
    connection = sqlite3.connect("bharan.db")
    c= connection.cursor()
    regex = "^[A-Z]{2}[0-9]{8}$"
    regex1 = "^[0-9]{10}$"
    q = re.compile(regex1)
    p = re.compile(regex)
    if not mid or not snumber or not bnumber:
      msg = 'Please fill out the form!'
    elif not re.search(q, snumber):
      msg = "Invalid Serial Number!"
    elif not re.search(p, bnumber):
      msg = "Invalid Batch Number!"
    else:
      try:
        c.execute('insert into vaccineproduce(mid, snumber, bnumber) values(?,?,?)',(mid, snumber, bnumber,))
        msg = 'Vaccine Added!'
      except Exception:
        msg = "Vaccine Already Added!"
      connection.commit()
  elif request.method == 'POST':
    msg = 'Please fill out the form!'
  return render_template("manufacture_add.html", msg=msg)

@app.route("/manufacture_get", methods =['GET', 'POST'])
def manufacture_get():
  msg=""
  if request.method == 'POST' and 'mid' in request.form:
    mid = request.form['mid']
    connection = sqlite3.connect("bharan.db")
    c = connection.cursor()
    regex = "^[0-9]+$"
    p = re.compile(regex)
    if not mid:
      msg = 'Please fill out the form!'
    elif not re.search(p, mid):
      msg = "Invalid User Number!"
    else:
      c.execute("select * from vaccineorder")
      rows = c.fetchall()
      msg = 'Here are your orders!'
      connection.commit()
  elif request.method == 'POST':
    msg = 'Please fill out the form!'
  return render_template("manufacture_get.html", rows=rows, msg=msg)

@app.route("/admin", methods=['GET', 'POST'])
def admin():
  msg = ""
  if request.method == 'POST' and 'ap' in request.form:
    ap= request.form['ap']
    password="pass@123"
    if not ap:
      msg="Enter Password!"
    elif ap != password:
      msg="Invalid Password"
      return render_template("admin.html", msg=msg)
    else:
      return redirect("/admin_view")
  elif request.method == 'POST':
    msg = "Enter Password!"
    return render_template("admin.html", msg=msg)
  else:
    return render_template("admin.html")

@app.route("/admin_view")
def admin_view():
  return render_template("admin_view.html")

@app.route("/citizen")
def citizen():
  return render_template("citizen.html")

@app.route("/vaccine")
def vaccine():
  return render_template("vaccine.html")

@app.route("/vaccined")
def vaccined():
  connection = sqlite3.connect("bharan.db")
  c = connection.cursor()
  c.execute("select * from citizenvaccinated")
  rows = c.fetchall()
  connection.commit()
  return render_template("vaccined.html", rows=rows)

@app.route("/left")
def left():
  connection = sqlite3.connect("bharan.db")
  c = connection.cursor()
  c.execute("select * from citizen")
  rows = c.fetchall()
  connection.commit()
  return render_template("left.html", rows=rows)

@app.route("/order")
def order():
  connection = sqlite3.connect("bharan.db")
  c = connection.cursor()
  c.execute("select * from vaccineorder")
  rows = c.fetchall()
  connection.commit()
  return render_template("order.html", rows=rows)

@app.route("/produce")
def produce():
  connection = sqlite3.connect("bharan.db")
  c = connection.cursor()
  c.execute("select * from vaccineproduce")
  rows = c.fetchall()
  connection.commit()
  return render_template("produce.html", rows=rows)

@app.route("/stock")
def stock():
  connection = sqlite3.connect("bharan.db")
  c = connection.cursor()
  c.execute("select * from vaccinestock")
  rows = c.fetchall()
  connection.commit()
  return render_template("stock.html", rows=rows)

@app.route("/used")
def used():
  connection = sqlite3.connect("bharan.db")
  c = connection.cursor()
  c.execute("select * from vaccineused")
  rows = c.fetchall()
  connection.commit()
  return render_template("used.html", rows=rows)

@app.route("/vaccination_center")
def vaccination_center():
  connection = sqlite3.connect("bharan.db")
  c = connection.cursor()
  c.execute("select * from citizen")
  rows = c.fetchall()
  df = pd.DataFrame(rows, columns=['uid', 'name', 'email', 'age', 'address', 'aadhar', 'longitude', 'latitude'])
  x = df[['longitude', 'latitude']]
  print(x)
  cluster = AgglomerativeClustering().fit(x)
  print(cluster.labels_)
  df['cluster'] = cluster.labels_
  a = df.groupby('cluster').mean()
  #print(cluster.cluster_centers_)
  plt.figure(figsize =(6, 6))
  plt.scatter(x['latitude'], x['longitude'], c = cluster.fit_predict(x), cmap ='rainbow')
  plt.scatter(a['latitude'], a['longitude'], color='y')
  #plt.legend()
  plt.savefig('D:/se_website/static/plot.png')
  return render_template("vaccination_center.html", a=a, img="plot.png")

if __name__ == "__main__":
  app.run(debug=True)