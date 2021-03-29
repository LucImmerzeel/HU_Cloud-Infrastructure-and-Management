from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from flask import render_template, flash, redirect, render_template_string, request
from .mongodb import from_db, all_from_db, to_db, update_db
from flask_login import LoginManager, current_user
import pymongo
from datetime import datetime


class AddRecord(FlaskForm):
    FQDN = StringField('FQDN')
    IP = StringField('IP')
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Add Record')


def config_form():
    existingdata = from_db("userdb", "users", {"_id": str(current_user.id)})
    # form = LoginForm()
    # if form.validate_on_submit():
    #     flash('Login requested for user {}, remember_me={}'.format(
    #         form.username.data, form.remember_me.data))
    #     return redirect('/')
    try:
        token = existingdata["token"]
    except:
        token = ""

    try:
        apikey = existingdata["apikey"]
    except:
        apikey = ""

    return f""" <h1>Settings</h1>
                <img src="{existingdata["picture_location"]}" alt="Profile Picture"><br>
                <p><b>UserId</b><br>{existingdata["_id"]}</p>
                <p><b>Name</b><br>{existingdata["name"]}</p>
                <p><b>Email</b><br>{existingdata["email"]}</p>
                <p>
                    <b>Token</b><br>
                    <input type="text" id="token" name="token" value="{token}">
                    <button onclick="document.location='generate_new_token'">Generate New</button><br>
                </p>
                <p>
                    <b>API key</b><br>
                    <input type="password" id="apikey" name="apikey" value="{apikey}">
                    <button onclick="document.location='generate_new_key'">Generate New</button><br>
                    <input type="checkbox" onclick="showApiKey()">Show Key
                    
                </p>
                <a class="button" href="/portal">Back</a>
                """ + """
                <script>
                    function showApiKey() {
                      var x = document.getElementById("apikey");
                      if (x.type === "password") {
                        x.type = "text";
                      } else {
                        x.type = "password";
                      }
                    }
                </script>"""


def config_ddns():
    from bson.objectid import ObjectId
    form = AddRecord()
    existingdata = from_db("userdb", "users", {"_id": str(current_user.id)})
    # form = LoginForm()
    # if form.validate_on_submit():
    #     flash('Login requested for user {}, remember_me={}'.format(
    #         form.username.data, form.remember_me.data))
    #     return redirect('/')
    if request.method == 'POST':
        record_id = str(to_db("userdb", "records",
                          {"FQDN": form.FQDN.data, "IP": form.IP.data,
                           "date_time": str(datetime.now().strftime("%d/%m/%Y %H:%M:%S"))}).inserted_id)
        try:
            update_db("userdb", "users", {"_id": str(current_user.id)}, {"$push": {"records": record_id}})
        except:  # expect that no records exist
            update_db("userdb", "users", {"_id": str(current_user.id)}, {"$set": {"records": [record_id]}})

    existingrecords = ""
    record_ids = None
    records = []
    try:
        record_ids = from_db("userdb", "users", {"_id": str(current_user.id)})["records"]
        if type(record_ids) is str:
            records.append(from_db("userdb", "records", {"_id": ObjectId(record_ids)}))
        else:
            for record_id in record_ids:
                records.append(from_db("userdb", "records", {"_id": ObjectId(record_id)}))
    except:
        pass

    if records is not None:
        for record in records:
            existingrecords += f""" <tr>
                                        <td>{record["FQDN"] if "FQDN" in record else ""}</td>
                                        <td>{record["IP"] if "IP" in record else ""}</td>
                                        <td>{record["date_time"] if "date_time" in record else ""}</td>
                                        <td><a class="button" href="/api/v1.0/delete?_id={record["_id"]}">Delete</a></td>
                                    </tr>"""

    return render_template_string(f""" <h1>DNS Records</h1>
                <p><b>UserId</b><br>{existingdata["_id"]}</p>
                <p><b>Name</b><br>{existingdata["name"]}</p>
                <p><b>Email</b><br>{existingdata["email"]}</p>
                <p>
                    <b>Existing DNS records</b><br>
                    <form action="" method="POST" novalidate>
                        <table>
                            <tr>
                                <th>FQDN</th>
                                <th>IP</th>
                                <th>Last Update</th>
                                <th>Edit</th>
                            </tr>
                            {existingrecords}
                            <tr>
                                <td>{form.FQDN(size=32)}</td>
                                <td>{form.IP(size=32)}</td>
                                <td></td>
                                <td>{form.submit()}</td>
                            </tr>
                        </table>
                    </form>
                </p>
                <a class="button" href="/portal">Back</a>
                """ + """
                <script>
                    
                </script>""", title='Add Record', form=form)