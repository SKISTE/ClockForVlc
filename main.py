from flask import Flask, render_template, redirect, url_for, request
from threading import Thread
import utils
app = Flask(__name__)

Settings = utils.Settings()


Controller = utils.Controller(Settings.auth_code)
ClockManager = utils.ClockManager()

Thread(target=Controller.Clock_Play,args=(Settings,)).start()


exc = ''
@app.route('/')
def load_main_page():
    return redirect(url_for('main'))

@app.route('/main')
def main():
    global exc
    temp = exc
    print(exc)
    exc = ''
    print(temp)
    return render_template('index.html',alarms=ClockManager.list(), exceptions=temp)


@app.route('/create_alarm', methods=['POST'])
def create_alarm():
    global exc
    name, time = request.form['name'], request.form['time']
    days = []
    try:
        if request.form['0'] == 'on':
            days.append(0)
    except Exception as e:
        print(str(e))
    try:
        if request.form['1'] == 'on':
            days.append(1)
    except Exception as e:
        print(str(e))
    try:
        if request.form['2'] == 'on':
            days.append(2)
    except Exception as e:
        print(str(e))
    try:
        if request.form['3'] == 'on':
            days.append(3)
    except Exception as e:
        print(str(e))
    try:
        if request.form['4'] == 'on':
            days.append(4)
    except Exception as e:
        print(str(e))
    try:
        if request.form['5'] == 'on':
            days.append(5)
    except Exception as e:
        print(str(e))
    try:
        if request.form['6'] == 'on':
            days.append(6)
    except Exception as e:
        print(str(e))
    if name == '':
        exc = 'Не введено название'
        return redirect(url_for('main'))
    if time == '':
        exc = 'Не введено время'
        return redirect(url_for('main'))
    if days == []:
        exc = 'Не выбрано ни дня'
        return redirect(url_for('main'))
    for x in ClockManager.list():
        if name == x['name']:
            exc = 'Такое название уже имеется'
            return redirect(url_for('main'))
    ClockManager.add_clock_to_json(utils.OneClock({'name':name,'days':days,'hour':time.split(':')[0],'min':time.split(':')[1]}))
    print(request.form)
    return redirect(url_for('main'))

@app.route('/delete_alarm', methods=['POST'])
def delete_alarm():
    name = request.form['name']
    for x in ClockManager.list():
        if name == x['name']:
            ClockManager.delete_clock(name)
    return redirect(url_for('main'))

@app.errorhandler(404)
def page_404(e):
    global exc
    exc = 'Вы зашли на неизвестную ветвь веб интерфейса, я вас перенаправил обратно'
    return redirect(url_for('main')), 404
@app.errorhandler(500)
def page_500(e):
    global exc
    exc = 'Вы зашли на неизвестную ветвь веб интерфейса, я вас перенаправил обратно'
    return redirect(url_for('main')), 404


Flask.run(app)