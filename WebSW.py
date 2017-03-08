#!/sbin/env python
# -- encoding=utf8 --

"""

"""

from flask import Flask, render_template
from flask import request, redirect
from flask.ext.bootstrap import Bootstrap
from flask.ext.script import Manager
from datacenter import DataCenter
from werkzeug import secure_filename
from logger import logger
import os


# for upload
UPLOAD_FOLDER = './nat_files/'
ALLOWED_EXTENSIONS = set(['csv'])

app = Flask(__name__)
app.config['BOOTSTRAP_SERVE_LOCAL']=True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
bootstrap = Bootstrap(app)
manager = Manager(app)
hosts=[]
dc=DataCenter()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route("/")
def index():
  return render_template('index.html')

@app.route("/refresh")
def refresh():
    dc.getMacTabA()
    dc.getArpTabA()
    return render_template('index.html')

@app.route("/arp")
def show_arp():
    return render_template('arp.html',arps=dc.arps)

@app.route("/arp/<kw>")
def show_arp_kw(kw):
    return render_template('arp.html',arps=dc.getArpKW(kw))

@app.route("/mac")
def show_mac():
    #print dc.macs
    return render_template('mac.html',macs=dc.macs)

@app.route("/mac/<kw>")
def show_mac_kw(kw):
    return render_template('mac.html',macs=dc.getMacKW(kw))

@app.route("/nat")
def show_nat():
    return render_template('nat.html',nats=dc.nats)

@app.route("/nat/<kw>")
def show_nat_kw(kw):
    return render_template('nat.html',nats=dc.getNATKW(kw))

@app.route("/initialize/<kw>")
def initialize(kw):
    if kw == 'arp':
        dc.getArpTabA()
    elif kw == 'mac':
        dc.getMacTabA()
    elif kw == 'nat':
        return redirect('/settings')
    return render_template('index.html')

@app.route("/settings")
def settings():
    return render_template('settings.html')

@app.route("/upload_nat_file", methods=['POST','GET'])
def uploadNatFile():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            fullPath = os.path.join(app.config['UPLOAD_FOLDER'],filename)
            print fullPath
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
	    app.config['CURRENT_NAT_FILE']=filename
            dc.getNATTab(fullPath)
            return redirect('/settings')

@app.route("/summary/<kw>")
def show_summary_kw(kw):
    return render_template('summary.html'
                           , macs=dc.getMacKW(kw)
                           , arps=dc.getArpKW(kw)
                           , nats=dc.getNATKW(kw))


if __name__ == '__main__':
    dc.getMacTabA()
    dc.getArpTabA()
    #dc.getNATTab()
    logger.info("dc init completed!")
    print "dc init completed!"
    manager.run()
