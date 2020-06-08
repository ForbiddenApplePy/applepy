#! /usr/bin/env python3

from flask import Flask, request
import os
import urllib
import re
import threading
from werkzeug.utils import secure_filename

# ----- Stylesheet and variable -------

uploads = '/srv/http/deploy_tp/'
DISALLOWED_EXT = {'php', 'html'}

style = '''
<style type="text/css">
body {
    background-color: DimGrey;
}
input {
	max-width: 500px;
	padding: 10px 20px;
	background: #f4f7f8;
	margin: 10px auto;
	padding: 20px;
	background: #f4f7f8;
	border-radius: 8px;
	font-family: 'Arial';
}
input[type=submit] {

</style>'''

html = '''<!DOCTYPE html> 
<head>
    '''+style+''' 
</head>
<font face='arial'>
<body>
    <div align=center>
        <form method = 'POST' enctype=multipart/form-data>
            hostname :<br><input type=text name=host placeholder='hostname' required><br>
            files : <br><input type=file name=file multiple=true placeholder='file' required><br>
            <input type=submit value=Lancer>
        </form>
    </div>
</font>
</body>'''

# ----- Fonctions --------

def allowed_file(filename:str):
    if '.' in filename and filename.rsplit('.',1)[1] in DISALLOWED_EXT:
        return False
        #return '.' in filename and filename.rsplit('.', 1)[1].lower() not in DISALLOWED_EXT
    else:
        return True

# ----- Script Serveur -------

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'host' not in request.form:
            return html
        if 'file' not in request.files:
            return html
        files = request.files.getlist('file')
        host_dir = secure_filename(request.form['host'])
        location = uploads + host_dir
        try:
            os.mkdir(location)
        except FileExistsError:
            pass

        for f in files:
            if f and allowed_file(f.filename):
                filename = secure_filename(f.filename)
                f.save(os.path.join(location, filename))
    return html
# launch app
if __name__ == '__main__':
    app.run()
