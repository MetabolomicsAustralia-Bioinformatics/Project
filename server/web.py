from flask import request
from flask import Flask
from flask import render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import scoped_session, sessionmaker, Query
from flask import Flask,redirect,url_for  
import json
import time
from collections import defaultdict
from datetime import datetime

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:MINCSY417@localhost:3306/projectdb'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
db.Model.metadata.reflect(db.engine)
class Info(db.Model):
    
    __table__ = db.Model.metadata.tables['spl_info']

class Detail(db.Model):
    __table__ = db.Model.metadata.tables['spl_dtl']

@app.route('/',methods=['POST', 'GET'])
def home():
    instrumentsName = db.session.query(Info.instrument).distinct().all()
    '''
    #check
    names = db.session.query(Info.name).all()
    Info_table = db.session.query(Info).all()
    InforowCount = db.session.query(Info).count()
    Detail_table = db.session.query(Detail).all()
    DetailrowCount = db.session.query(Detail).count()
    '''
    
    instruments = []
    for i in instrumentsName:
        instruments.append(i[0])

    '''
    mzmlNames = []
    for i in names:
        mzmlNames.append(i[0])

    instrument_name={}    
    for index in range(InforowCount):
        key=Info_table[index].instrument
        value=Info_table[index].name
        if key not in instrument_name:
            instrument_name[key]=[value]
        else:
            instrument_name[key].append(value)

    name_target={}
    nameTarget_data={}    
    for index in range(DetailrowCount):
        data=Detail_table[index].data
        data1=str(data['RTs'])
        
        data2=str(data['ints'])
        data = data1+',,'+data2
        
        key=str(Detail_table[index].name)+str(Detail_table[index].EIC)
        nameTarget_data[key]=data
        
        if Detail_table[index].name not in name_target:  
            name_target[Detail_table[index].name]=[str(Detail_table[index].EIC)]
        else:
            name_target[Detail_table[index].name].append(str(Detail_table[index].EIC))
            
    instrument_name=json.dumps(instrument_name)
    name_target=json.dumps(name_target)     
    nameTarget_data=json.dumps(nameTarget_data)
    '''
    if request.method == 'POST':
        sttime = request.form['starttime']
        ettime = request.form['endtime']
        inst = request.form['instrument']
        #sttime = datetime.strptime(sttime, "%Y-%m-%d %H:%M")
        
        info_instrument = db.session.query(Info).filter_by(instrument=inst).filter(Info.actualstarttime > sttime,Info.actualendtime<ettime).all()
        samples = {}
        samples1 = {}
        for i in info_instrument:
            sample = db.session.query(Detail).filter_by(name = i.name).all()
            samples[i.name] = sample
            nameTar={}       
            for j in sample:                
                data=j.data
                data1=str(data['RTs'])
                data1 = data1[1:len(data1)-1]
                data2=str(data['ints'])
                data2 = data2[1:len(data2)-1]
                data = data1+',,'+data2        
                key=str(j.EIC)
                nameTar[key]=data
            samples1[str(i.name)] = nameTar
        samples1 = json.dumps(samples1)
        return render_template("homePage.html",instruments=instruments,info_instrument = info_instrument,samples = samples, samples1 = samples1)
    return render_template("homePage.html",instruments=instruments)


@app.route('/summary', methods=['POST', 'GET'])
def summary():
    # get the count of instruments [instrument1, 2, 3..]
    info_instruments = db.session.query(Info.instrument).distinct().all()
    instruments = []
    for i in info_instruments:
        instruments.append(i[0])
    sorted(instruments)
    smry_instruments = defaultdict(dict)
    for j in instruments:
        info_instrument = db.session.query(Info).filter_by(instrument=j).all()
        count_sample = len(info_instrument)

        data = []
        total_length = 0
        for i in info_instrument:
            st = i.actualstarttime
            et = i.actualendtime
            length = i.length
            total_length += length
            #starttime = datetime.strptime(st, "%Y-%m-%d %H:%M:%S.%f")
            #endtime = datetime.strptime(et, "%Y-%m-%d %H:%M:%S.%f")
            st = int(time.mktime(st.timetuple()) * 1000 + st.microsecond / 1000)
            et = int(time.mktime(et.timetuple()) * 1000 + et.microsecond / 1000)

            data.append([st, 1])
            data.append([et, 0])
        ct = datetime.now()
        ct = int(time.mktime(ct.timetuple()) * 1000 + ct.microsecond / 1000)

        ft = db.session.query(Info).first().actualstarttime
        #first_time = datetime.strptime(ft, "%Y-%m-%d %H:%M:%S.%f")
        ft = int(time.mktime(ft.timetuple()) * 1000 + ft.microsecond / 1000)

        total = ct - ft
        ratio = round(total_length * 1000 / total * 100, 2)
        rest_ratio = 100 - ratio
        smry_instruments[j]['count'] = count_sample
        smry_instruments[j]['hours'] = round(total/3600000,2)
        smry_instruments[j]['ratio'] = ratio
        smry_instruments[j]['rest_ratio'] = rest_ratio
        smry_instruments[j]['data'] = data
        # smry_insruments = json.dumps(smry_instruments)
    return render_template("summary.html", smry_instruments = smry_instruments, instruments = instruments)



if __name__ == '__main__':
    app.debug = True
    app.run()
   
