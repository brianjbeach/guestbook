import sys, logging, socket, subprocess, os
import flask, pymysql
from flask import Flask, request, Response, json, escape


rds_host = 'guestbook.c99wpxpbqiyd.us-east-1.rds.amazonaws.com'
name = 'guestbook'
password = 'guestbook'
db_name = 'guestbook'
application = Flask(__name__)


def get_db():
    return pymysql.connect(rds_host, user=name, passwd=password, db=db_name, connect_timeout=5)


@application.route('/', methods=['GET'])
def index():
    return flask.render_template('index.html', server=socket.gethostname())


@application.route('/sign', methods=['GET'])
def sign():
    return flask.render_template('sign.html')


@application.route('/data', methods=['GET'])
def GetData():
    db = get_db()
    try:
        cur = db.cursor()
        cur.execute('SELECT name, email, comments FROM guestbook')
        rows = []
        for row in cur:
            rows.append({'name': row[0], 'email': row[1], 'comments': row[2]})
        response = Response(json.dumps(rows), status=200, content_type='application/json')
        response.headers['Cache-Control'] = 'no-cache'
        return response
    except Exception as ex:
        logging.exception("message")
        return Response("Error", status=500)
    finally:
        db.close()


@application.route('/data', methods=['POST'])
def PostData():
    if request.json is None:
        return Response("Expect application/json request", status=415)
    else:
        db = get_db()
        try:
            cur = db.cursor()
            cur.execute('INSERT INTO guestbook (name, email, comments) VALUES (%s, %s, %s)', 
                [escape(request.json['name']), escape(request.json['email']), escape(request.json['comments'])])
            db.commit()
            response = Response("Success!", status=200)
            response.headers['Cache-Control'] = 'no-cache'
            return response
        except Exception as ex:
            logging.exception("message")
            return Response("Error", status=500)
        finally:
            db.commit()
            db.close()

@application.route('/stress', methods=['GET'])
def stress():
    def simulate_work():
        yield("<p>Working...")
        subprocess.call(['stress', '--cpu', '2', '--timeout', '10'])
        yield("Done!</p>")
    return Response(simulate_work(), status=200) 


#If the table does not exist, create it and load some sample data
def InitDB():
    try:
        db = get_db()
        cur = db.cursor()
        cur.execute("SELECT * FROM guestbook")
    except pymysql.ProgrammingError as ex:
        if ex.args[0] == 1146:
            cur.execute('CREATE TABLE `guestbook` (`id` int(4) NOT NULL auto_increment, `name` varchar(65) NOT NULL default "", `email` varchar(65) NOT NULL default "", `comments` longtext NOT NULL, PRIMARY KEY (`id`)) ENGINE=MyISAM DEFAULT CHARSET=latin1 AUTO_INCREMENT=1')
            cur.execute('INSERT INTO guestbook (name, email, comments) VALUES (%s, %s, %s)', ["Barry Allen", "flash@dccomics.com", "Feel the speed force!"])
            cur.execute('INSERT INTO guestbook (name, email, comments) VALUES (%s, %s, %s)', ["Peter Parker", "spiderman@marvel.com", "With great power comes great responsibility!"])
            cur.execute('INSERT INTO guestbook (name, email, comments) VALUES (%s, %s, %s)', ["Clark Kent", "superman@dccomics.com", "Up, up, and away!"])
            db.commit()
    finally:
        db.close()


InitDB()
if __name__ == "__main__":
    application.run(host="0.0.0.0", port=80, debug=True) 



