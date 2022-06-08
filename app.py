# coding: utf-8

import logging
import configparser
import os
import signal
import sys
import time
from threading import Lock

# you need to install these extra packages
import psutil   # psutil
from flask import Flask, request, render_template, session, redirect    # Flask
from flask_socketio import SocketIO     # Flask-SocketIO
import geventwebsocket  # gevent-websocket

VER = '1.0.0-beta2'


def readConfig():
    try:
        global IP, PORT, ENABLE_AUTH, USR, PSW
        config = configparser.ConfigParser()
        config.read('html_monitor/config.ini')
        IP = config.get('Network', 'ip')
        PORT = config.getint('Network', 'port')
        ENABLE_AUTH = config.getboolean('Security', 'enable-auth')
        USR = config.get('Security', 'username')
        PSW = config.get('Security', 'password')
    except KeyError:
        resetConfig()


def resetConfig():
    print('Writing file...')
    if not os.path.exists('html_monitor'):
        os.mkdir('html_monitor')
    if not os.path.exists('html_monitor/templates'):
        os.mkdir('html_monitor/templates')
        indexPage = open('html_monitor/templates/index.html', 'w')
        indexPage.write('<!DOCTYPE html>\n<html lang="en">\n<head>\n    <meta charset="UTF-8">\n    <meta '
                        'name="viewport" content="width=device-width, initial-scale=1.0">\n    <meta '
                        'http-equiv="X-UA-Compatible" content="ie=edge">\n    <title>HTMLMonitor</title>\n    <link '
                        'rel="stylesheet" href="{{ url_for(\'static\', filename=\'style.css\') }}">\n    <link '
                        'rel="shortcut icon" href="{{ url_for(\'static\', filename=\'favicon.ico\') }}">\n    <script '
                        'type="text/javascript" src="{{ url_for(\'static\', filename=\'jquery.min.js\') '
                        '}}"></script>\n    <script type="text/javascript" src="{{ url_for(\'static\', '
                        'filename=\'socket.io.js\') }}"></script>\n    <script src="{{ url_for(\'static\', '
                        'filename=\'echarts.min.js\') }}"></script>\n    <script src="{{ url_for(\'static\', '
                        'filename=\'dark.js\') }}"></script>\n</head>\n<body>\n    {{ logout|safe }}\n    '
                        '<h1>Monitor</h1>\n    <div id="CPU"></div>\n    <div id="Mem"></div>\n    <script '
                        'type="text/javascript" src="{{ url_for(\'static\', filename=\'charts.js\') }}"></script>\n   '
                        ' <hr>\n    <p>Powered by HTMLMonitor<br><small>Version: {{ ver }}  UI version: '
                        '1.0.1</small></p>\n</body>\n</html>')
        indexPage.close()
        loginPage = open('html_monitor/templates/login.html', 'w')
        loginPage.write('<!DOCTYPE html>\n <html lang="en">\n <head>\n     <meta  charset="UTF-8">\n     '
                        '<title>Login</title>\n     <link rel="shortcut icon" href="{{ url_for(\'static\', '
                        'filename=\'favicon.ico\') }}">\n     <style>\n        body{background-color:#292929;}\n       '
                        ' @keyframes fadeInAnimation  {0% {opacity:0;} 100% {opacity:1;}}\n        div {margin: 20px; '
                        'padding: 10px;}\n        hr  {border-top: 5px solid#c3c3c3; border-bottom-width: 0; '
                        'border-left-width: 0; border-right-width: 0; border-radius: 3px;}\n        h1  {color: '
                        '#c3c3c3; font-family: Arial,serif; font-size: 250%; text-align: center; '
                        'letter-spacing:3px;}\n        h2  {color: #c3c3c3; font-family: Arial,serif; font-size: 220%; '
                        'text-align: center; letter-spacing:3px;}\n        h3  {color: #c3c3c3; font-family: Arial,'
                        'serif; font-size: 190%; text-align: center; letter-spacing:3px;}\n        h4  {color: '
                        '#c3c3c3; font-family: Arial,serif; font-size: 170%; text-align: center; '
                        'letter-spacing:3px;}\n        h5  {color: #c3c3c3; font-family: Arial,serif; font-size: 150%; '
                        'text-align: center; letter-spacing:3px;}\n        h6  {color: #c3c3c3; font-family: Arial,'
                        'serif; font-size: 130%; text-align: center; letter-spacing:3px;}\n        code{color: '
                        '#c8c8c8; font-family: Courier New,serif;}\n        a   {text-decoration: None; color: '
                        '#58748d; font-family: sans-serif; letter-spacing:1px;}a:link,\n        a:visited   {color: '
                        '#58748d;}\n        a:hover     {color: #539899; text-decoration:none;}\n        a:active	{'
                        'color: #c3c3c3; background: #101010;}\n        p   {color: #c3c3c3; font-family: Helvetica,'
                        'serif;font-size: 100%; display: inline; text-indent: 100px; letter-spacing:1px; '
                        'line-height:120%;}\n        p.warn      {color: #e33a3a; font-family: Helvetica,'
                        'serif;font-size: 100%; display: inline; text-indent: 100px; letter-spacing:1px; '
                        'line-height:120%;}\n        ul  {list-style-type: square; font-family: Helvetica,'
                        'serif; color: #c3c3c3;}ol{font-family: Helvetica,serif; color: #c3c3c3;}\n        table      '
                        ' {border: 2px solid #101010; font-family: Helvetica,serif;}\n        th  {border: 1px solid '
                        '#101010; font-family: Helvetica,serif; color: #c3c0c3; font-weight: bold; text-align: '
                        'center; padding: 10px;}\n        td  {font-family: Helvetica,serif; color: #c3c3c3; '
                        'text-align: center; padding: 2px;}\n        input       {color: #c3c3c3; font-family: '
                        'Courier,serif; background: #101010; border-top-width: 0; border-bottom-width: 2px; '
                        'border-left-width: 0; border-right-width: 0; height: 30px; width: 500px; font-size: 15px;}\n '
                        '       div.fade    {animation: fadeInAnimation ease 0.3s; animation-iteration-count: '
                        '1;animation-fill-mode: forwards;}\n    </style>\n </head>\n <body>\n {% if msg %}\n    '
                        '<div>\n {% else %}\n    <div class="fade">\n {% endif %}\n         <h1>Login to access this '
                        'site</h1>\n         <p>This site is a private site! </p><br>\n         <a href="/">I think '
                        'I`ve already logged in -></a>\n         <hr>\n         <center>\n             <form  '
                        'method="post">\n                <label>\n                <input type="text"  name="user" >\n '
                        '               </label><br>\n                <label>\n                <input  '
                        'type="password" name="psw" >\n                </label><br>\n                <input  '
                        'type="submit" name="Login"><br><br>\n                <p class="warn">{{msg}}</p>\n           '
                        '  </form>\n         </center>\n         <br><p>Powered by HTMLMonitor</p>\n     </div>\n '
                        '</body>\n </html>\n')
        loginPage.close()
    if not os.path.exists('html_monitor/static'):
        os.mkdir('html_monitor/static')
        chartJS = open('html_monitor/static/charts.js', 'w')
        chartJS.write('var time = ["", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", '
                      '"", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", "", ""],\n    cpu = ['
                      '0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '
                      '0, 0, 0, 0, 0, 0, 0, 0, 0],\n    mem = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, '
                      '0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]\n\nvar CPU = echarts.init('
                      'document.getElementById(\'CPU\'), \'dark\');\nCPU.setOption({\n    title: {text: \'CPU\'},'
                      '\n    tooltip: { trigger: \'none\' },\n    legend: {data: [cpu]},\n    calculable: true,'
                      '\n    xAxis: {data: []},\n    yAxis: {},\n    series: [{name: \'CPU\', type: \'line\', '
                      'data: [],}],\n    toolbox: {\n        show: true,\n        feature: {\n            magicType: '
                      '{ type: [\'line\', \'bar\'] },\n            restore: {},\n            saveAsImage: {}\n    '
                      '}}\n});\n\nvar update_CPU = function (res) {\n    CPU.hideLoading();\n    cpu.push(parseFloat('
                      'res.data[1]));\n    if (time.length >= 40) {\n        time.shift();\n        cpu.shift();\n    '
                      '}\n    CPU.setOption({series: [{name: \'CPU\', data: cpu}]})\n};\n\nvar Mem = echarts.init('
                      'document.getElementById(\'Mem\'), \'dark\');\nMem.setOption({\n    title: {text: \'Memory\'},'
                      '\n    tooltip: { trigger: \'none\' },\n    legend: {data: [\'mem\']},\n    calculable: true,'
                      '\n    xAxis: {data: []},\n    yAxis: {},\n    series: [{name: \'Memory\', type: \'line\', '
                      'data: []}],\n    toolbox: {\n        show: true,\n        feature: {\n            magicType: { '
                      'type: [\'line\', \'bar\'] },\n            restore: {},\n            saveAsImage: {}\n    '
                      '}}\n});\n\nvar update_Mem = function (res) {\n    Mem.hideLoading();\n    mem.push(parseFloat('
                      'res.data[2]));\n    if (time.length >= 40) {\n        time.shift();\n        mem.shift();\n    '
                      '}\n    Mem.setOption({series: [{name: \'Memory\', data: mem}]});\n\n};\n\nCPU.showLoading('
                      ')\nMem.showLoading()\ncpu.push(parseFloat(100.0));\nmem.push(parseFloat(100.0));\n$('
                      'document).ready(function () {\n    var namespace = \'/test\';\n    var socket = io.connect('
                      'location.protocol + \'//\' + document.domain + \':\' + location.port + namespace);\n\n    '
                      'socket.on(\'server_response\', function (res) {\n        update_CPU(res);\n        update_Mem('
                      'res);\n    });\n});')
        chartJS.close()
        globalCSS = open('html_monitor/static/style.css', 'w')
        globalCSS.write('@keyframes fadeInAnimation  {0% {opacity:0;} 100% {opacity:1;}}\nbody        {'
                        'background-color: #333333; animation: fadeInAnimation ease 0.3s; animation-iteration-count: '
                        '1;animation-fill-mode: forwards;}\np   {color: #c3c3c3; font-family: Helvetica,'
                        'serif;font-size: 100%; display: inline; text-indent: 100px; letter-spacing:1px; '
                        'line-height:120%;}\na   {text-decoration: None; color: #58748d; font-family: sans-serif; '
                        'letter-spacing:1px;}\na:link, a:visited   {color: #58748d;}\na:hover     {color: #539899; '
                        'text-decoration:none;}\na:active	{color: #292929; background: #101010;}\ndiv     {height: '
                        '200px; border:0;}\nh1      {color: #c3c3c3; font-family: Arial,serif; font-size: 250%; '
                        'text-align: center; letter-spacing:3px;}')
        globalCSS.close()
        os.system('curl https://cdnjs.cloudflare.com/ajax/libs/jquery/3.3.1/jquery.min.js --output .'
                  '/html_monitor/static/jquery.min.js')
        os.system('curl https://cdn.socket.io/3.1.2/socket.io.js --output ./html_monitor/static/socket.io.js')
        os.system('curl https://cdn.socket.io/3.1.2/socket.io.js.map --output ./html_monitor/static/socket.io.js.map')
        os.system('curl https://cdn.staticfile.org/echarts/4.3.0/echarts.min.js --output '
                  './html_monitor/static/echarts.min.js')
        os.system('curl https://echarts.apache.org/en/asset/theme/dark.js --output ./html_monitor/static/dark.js')
        os.system('curl https://github.com/D2Lib/HTMLMonitor/raw/main/favicon.ico --output '
                  './html_monitor/static/favicon.ico')

    configFile = open('./html_monitor/config.ini', 'w')
    configFile.write('[Network]\n'
                     'ip=0.0.0.0\n'
                     'port=80\n'
                     '\n'
                     '[Security]\n'
                     'enable-auth=true\n'
                     'username=root\n'
                     'password=root\n')
    configFile.close()
    print('Finish!')


print('Reading config...')
if os.path.exists('html_monitor/config.ini'):
    readConfig()
else:
    resetConfig()
    readConfig()

app = Flask('Monitor', template_folder='html_monitor/templates', static_folder='html_monitor/static')
app.secret_key = 'QWERTYUIOP'
app.name = 'Monitor'
FORMAT = '[%(asctime)s](%(levelname)s|%(threadName)s): %(message)s'
logging.basicConfig(format=FORMAT, datefmt='%Y-%M-%d %H:%M:%S', level=logging.INFO)
async_mode = None
socketio = SocketIO(app, async_mode=async_mode, cors_allowed_origins='*')
thread = None
thread_lock = Lock()


def background_thread():
    count = 0
    while True:
        socketio.sleep(2)
        count = count + 1
        t = time.strftime('%H:%M:%S', time.localtime())
        datas = [psutil.cpu_percent(interval=None), psutil.virtual_memory().percent]  # 获取系统cpu使用率 non-blocking
        socketio.emit('server_response',
                      {'data': [t] + datas, 'count': count}, namespace='/test')


@app.route('/login', methods=['GET', "POST"])
def login():
    if ENABLE_AUTH:
        if request.method == 'GET':
            return render_template('login.html')
        user = request.form.get('user')
        psw = request.form.get('psw')
        if user + ':' + psw == USR + ':' + PSW:
            session['user'] = user
            return redirect('/')
        else:
            return render_template('login.html', msg='Error username or password')
    else:
        return redirect('/')


@app.route('/logout')
def logout():
    if ENABLE_AUTH:
        try:
            del session['user']
        except KeyError:
            pass
        return redirect('login')
    else:
        return redirect('/')


@socketio.on('connect', namespace='/test')
def test_connect():
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(target=background_thread)


@app.route('/index')
def monitor():  # put application's code here
    user_info = session.get('user')
    if not user_info and ENABLE_AUTH:
        return redirect('/login')
    if ENABLE_AUTH:
        logout = '<a href="/logout">Logout</a>'
    else:
        logout = ''
    return render_template('index.html', logout=logout, ver=VER)


@app.route('/')
def home():
    return redirect('/index')


def stop(*args):
    try:
        socketio.stop()
    except Exception:
        pass
    print('Server stopped at ' + str(time.strftime('%Y-%M-%d %H:%M:%S', time.localtime())))
    sys.exit(0)


if __name__ == '__main__':
    print(f'Server opened on: http://{IP}:{PORT}')
    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)
    cli = sys.modules['flask.cli']
    cli.show_server_banner = lambda *x: None
    socketio.run(app, debug=True, host=IP, port=PORT)
