import base64
import binascii
import functools
import json
from datetime import date

import sdu_bkjws
from flask import Flask, request, make_response

import make_ics

app = Flask(__name__)


def parserAuth(fn):
    @functools.wraps(fn)
    def wrapper():
        try:
            auth = request.args.get('auth', None)
            if auth:
                auth = auth.replace('@', '=')
                auth = base64.b64decode(auth).decode()
            else:
                return 'This page does not exist', 404
        except binascii.Error:
            return make_response('error'), 404
        try:
            auth = json.loads(auth)
        except json.JSONDecodeError:
            return make_response('error'), 404
        try:
            print(auth)
            username = auth['username']
            password = auth['password']
            s = sdu_bkjws.SduBkjws(username, password)
            return fn(s)
        except Exception as e:
            resp = make_response(
                json.dumps({'error': str(e)}))
            return resp, 401

    return wrapper


@app.route('/login')
@parserAuth
def login(s: sdu_bkjws.SduBkjws):
    return json.dumps(s.detail)


@app.route('/exam-result')
@parserAuth
def examResult(s: sdu_bkjws.SduBkjws):
    result = s.get_fail_score() + s.get_now_score() + s.get_past_score()
    return json.dumps(result, ensure_ascii=False,
                      sort_keys=True)


@app.route('/curriculum')
@parserAuth
def manyUser(s: sdu_bkjws.SduBkjws):
    x = make_ics.from_lesson_to_ics(s.get_lesson())
    resp = make_response(x)
    resp.headers['Content-Type'] = "text/calendar;charset=UTF-8"
    return resp


@app.route('/calendar/<auth>')
def calendar(auth):
    try:
        if auth:
            auth = base64.b64decode(auth).decode()
        else:
            return 'you need query', 404
    except binascii.Error:
        return make_response('error'), 404
    try:
        auth = json.loads(auth)
    except json.JSONDecodeError:
        return make_response('error'), 404
    try:
        print(auth)
        username = auth['username']
        password = auth['password']
        s = sdu_bkjws.SduBkjws(username, password)
        exam = request.args.get('exam', False) == 'true'
        curriculum = request.args.get('curriculum', False) == 'true'
        if not (exam or curriculum):
            return make_response('error'), 404
        query = {'exam': exam, 'curriculum': curriculum}
        r = make_ics.calendar(s, query)
        r = make_response(r)
        print(request.user_agent)
        if request.user_agent.string.find('Mozilla') != -1:
            # return send_file('./openInSafari.html')
            r.headers['Content-Type'] = "text/plain;charset=UTF-8"
        else:
            r.headers['Content-Type'] = "text/calendar;charset=UTF-8"
        return r, 200
    except Exception as e:
        resp = make_response(
            json.dumps({'error': str(e)}))
        return resp, 401


@app.route('/exam-arrangement')
@parserAuth
def exam(s: sdu_bkjws.SduBkjws):
    today = date.today()
    if today.month <= 2:
        xq = 1
        year = today.year - 1
    elif 2 < today.month < 8:
        xq = 2
        year = today.year - 1
    else:
        xq = 1
        year = today.year
    xnxq = '{}-{}-{}'.format(year, year + 1, xq)
    e = s.get_exam_time(xnxq)
    ics = make_ics.from_exam_to_ics(e)
    resp = make_response(ics)
    resp.headers['Content-Type'] = "text/calendar;charset=UTF-8"
    return resp


@app.errorhandler(404)
def page_not_found(error):
    return 'This page does not exist', 404


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=800)