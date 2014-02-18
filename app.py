#coding:utf-8
import sqlite3
import json
from datetime import date
from flask import g
from flask import Flask, render_template, request, jsonify
app = Flask(__name__)



def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('imosmobile')
        db.text_factory = str
        db.row_factory = dict_factory
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d



def createTable():
    db = get_db
    c = db.cursor()

    try:
        c.execute('''CREATE TABLE members
                 (name text, number text)''')
    except:
        pass

    try:
        c.execute('''CREATE TABLE daily
                 (name text, date text, done text, todo text, risk text)''')
    except:
        pass


    # Save (commit) the changes
    db.commit()

def getMembers():
    db = get_db()
    c = db.cursor()
    c.execute('SELECT * FROM members')
    members = c.fetchall()
    c.close()
    print members
    return members

def getDaily(name, date):

    db = get_db()
    c = db.cursor()
    c.execute('SELECT * FROM daily WHERE name=? AND date=?', (name,date))
    all = c.fetchone()
    c.close()
    return all

def getDailys( date):

    db = get_db()
    c = db.cursor()
    sql = "select t1.*,t2.alias from daily as t1 left join members as t2 on t2.name=t1.name where date=?"
    c.execute(sql, (date,))
    #c.execute('SELECT * FROM daily WHERE date=?', (date,))
    all = c.fetchall()
    print all
    c.close()
    return all

def updateDaily(name ,date, done, todo, risk):

    db = get_db()
    c = db.cursor()
    c.execute('SELECT * FROM daily WHERE name=? AND date=?', (name, date))
    if None != c.fetchone():
        c.execute('UPDATE daily SET done=?, todo=?, risk=?  WHERE name=? AND date=?', (done, todo, risk, name, date))
        db.commit()
    else:
        c.execute("INSERT INTO daily VALUES(?, ?, ?, ?, ?)", ( name, date, done, todo, risk))
        db.commit()
    c.close()

@app.route("/",  methods=['GET', 'POST'])
@app.route("/report",  methods=['GET', 'POST'])
def report():
    if request.method == 'POST':
        dt = request.form['date']
        dailys = getDailys(dt)
        ds = []
        for daily in dailys:
            d = {}
            if None != daily and len(daily) > 0:
                d['name'] = daily['alias'].decode("utf-8")
                d['done'] = daily['done'].decode("utf-8").replace("\n", "  \n")
                d['todo'] = daily['todo'].decode("utf-8").replace("\n", "  \n")
                d['risk'] = daily['risk'].decode("utf-8").replace("\n", "  \n")
                ds.append(d)

        print ds
        return jsonify(result=ds)
    else:
        return render_template('report.html', today=date.today(), members=getMembers())

@app.route("/m/<name>", methods=['GET', 'POST'])
def member(name=None):
    if request.method == 'POST':
        act =  request.form['act']
        if act == 'set':
            done = request.form['done']
            todo = request.form['todo']
            risk = request.form['risk']
            _date = request.form['date']
            print name, done, todo, risk, _date
            updateDaily(name, _date,done, todo, risk)

            return jsonify(result=done + risk)
        else:
            dt = request.form['date']
            print dt
            daily = getDaily(name, dt)
            print daily
            d = {}
            if None != daily:
                d['done'] = daily['done'].decode("utf-8")
                d['todo'] = daily['todo'].decode("utf-8")
                d['risk'] = daily['risk'].decode("utf-8")
                print d
            return jsonify(result=d)
    else:
        return render_template('index.html', today=date.today(), name=name, members=getMembers())


if __name__ == "__main__":
    app.run(debug=True)
