import requests
import json
from datetime import datetime, date
from time import sleep
import os
import configparser
import urllib.parse
from win10toast import ToastNotifier


class Logger():
    def __init__(self,from_class) -> None:
        self._CheckLogFile()
        self.from_class = from_class
        self.toaster = ToastNotifier()

    def _CheckLogFile(self):
        filepath = os.path.join(os.getcwd(), 'log.txt')  # Создаем полный путь к файлу
        if os.path.isfile(filepath):
            pass
        else:
            open('log.txt','w',encoding='utf-8')

    def current_time(self):
        return date.today()

    def write(self,text):
        with open('log.txt','a',encoding='utf-8') as file:
            file.write('\n'+text)

    def info(self,text):
        self.write(self.current_time+f':[INFO][{self.from_class}]'+text)
    def warn(self,text):
        self.write(self.current_time+f':[WARN][{self.from_class}]'+text)
    def error(self,text):
        self.toaster.show_toast("Ошибка в будильнике", text, duration=10, threaded=True)
        self.write(self.current_time+f':[ERROR][{self.from_class}]'+text)


class Controller:
    def __init__(self, token) -> None:
        self.auth_token = token
        self.headers = {"authorization": self.auth_token}
        self.url = "http://localhost:8080/requests/status.xml?command="
        self.logger = Logger('Controller')
        print(self.auth_token)

    def pause(self):
        req = requests.get(f"{self.url}pl_pause", headers=self.headers)
        if req.status_code in [200,204]:
            self.logger.info('Pause set')
            return req
        else:
            self.logger.error('Error in pause: '+req.text)

    def volume(self, vol):
        """
        Volume: 0 - 512, int
        """
        req = requests.get(f"{self.url}volume&val={str(vol)}", headers=self.headers)
        if req.status_code in [200,204]:
            self.logger.info('Volume set on = '+str(vol))
            return req
        else:
            self.logger.error(f'Error in volume({str(vol)}): '+req.text)

        return req

    def start_file(self, path):
        # return requests.get(f'{self.url}in_play&input=file:///'+requests.utils.quote(path, encoding='utf-8'),headers=self.headers)
        path_url = urllib.parse.quote(path.encode("cp1251"))
        req = requests.get(
            "http://localhost:8080/requests/status.xml?command=in_play&input=file:///"
            + path_url,
            headers=self.headers,
        )
        if req.status_code in [200,204]:
            self.logger.info('Start file = '+str(path))
            return req
        else:
            self.logger.error(f'Error in start_file({str(path)}): '+req.text)
        return req


    def Clock_Play(self, settings):
        used_clocks = []
        sleep_delay = settings.sleep_delay
        playlist_path = settings.Playlist_path
        alarm_type = settings.alarm_type
        volume = settings.Volume_value
        while True:
            print('Clock_Play tick')
            turn_on = True
            all_clocks = json.load(open("clocks.json"))
            for x in all_clocks["clocks"]:
                if (
                    int(x["hour"]) == datetime.today().hour
                    and int(x["min"]) == datetime.today().minute
                    and datetime.today().weekday() in x["days"]
                ):
                    for i in used_clocks:
                        print(x["name"] + " == " + i["name"])
                        if x["name"] == i["name"]:
                            turn_on = False
                    if turn_on:
                        if alarm_type == "1":
                            self.start_file(playlist_path)
                        elif alarm_type == "2":
                            print(self.pause().status_code)
                        self.volume(volume)
                        used_clocks.append(
                            {"name": x["name"], "counter": int(sleep_delay) * 10}
                        )
                        pass
                    else:
                        turn_on = True
            for x in used_clocks:
                if x["counter"] >= 1:
                    x.update({"counter": x["counter"] - 1})
                else:
                    used_clocks.remove(x)
            sleep(int(sleep_delay))


class OneClock:
    def __init__(self, clock_list):
        self.hour = clock_list["hour"]
        self.min = clock_list["min"]
        self.days = clock_list["days"]
        self.name = clock_list["name"]


class ClockManager:
    def __init__(self):
        self.logger = Logger('ClockManager')
        pass

    def day_manager(self, days):
        """
        return numbers from string days
        """
        pattern = {"пн": 0, "вт": 1, "ср": 2, "чт": 3, "пт": 4, "сб": 5, "вс": 6}
        temp = []
        for x in days.split(","):
            temp.append(pattern[x])
        return temp

    def add_clock_to_json(self, clock):
        temp = json.load(open("clocks.json"))
        print(temp)
        temp["clocks"].append(
            {
                "hour": clock.hour,
                "min": clock.min,
                "days": clock.days,
                "name": clock.name,
            }
        )
        with open("clocks.json", "w") as file:
            file.write(json.dumps(temp, sort_keys=True, indent=4))
            self.logger.info(f'Added clock to JSON: {str({"hour": clock.hour,"min": clock.min,"days": clock.days,"name": clock.name})}')
        return

    def create_clock(self, name, time, days):
        days = self.day_manager(days)
        hour, min = time.split(":")
        file = json.load(open("clocks.json"))
        for x in file["clocks"]:
            if name == x["name"]:
                self.logger.info('Unnable add clock to json, name is already have')
                return "Такое название уже имеется, давай новое думай"
        self.add_clock_to_json(
            OneClock({"hour": hour, "min": min, "days": days, "name": name})
        )
        return "Успешно добавлен новый будильник"

    def list(self):
        file = json.load(open("clocks.json"))
        days_pattern = {
            0: "пн",
            1: "вт",
            2: "ср",
            3: "чт",
            4: "пт",
            5: "сб",
            6: "вс",
        }
        print(file["clocks"])
        temp = []
        for x in range(0, len(file["clocks"])):
            days = ""
            for i in file["clocks"][x]["days"]:
                days = days + str(days_pattern[i]) + ","
            temp.append({'name':file["clocks"][x]["name"],'time':f'{file["clocks"][x]["hour"]}:{file["clocks"][x]["min"]}','days':days[:-1]})
            # temp = temp + f'\n-= {str(x+1)} =-\n{file["clocks"][x]["name"]}\n{file["clocks"][x]["hour"]}:{file["clocks"][x]["min"]}\n{days[:-1]}'
            
        return temp

    def delete_clock(self, name):
        temp = json.load(open("clocks.json"))
        for x in temp["clocks"]:
            if name == x["name"]:
                temp["clocks"].remove(x)
                with open("clocks.json", "w") as file:
                    self.logger.info('Deleted clock with name '+name)
                    file.write(json.dumps(temp, sort_keys=True, indent=4))
                return "Успешно удалено"
        self.logger.info('[delete_clock] Clock with name '+name+' not found')
        return "Такое название не найдено"


class Settings:
    config = configparser.ConfigParser()
    config.read("settings.ini")
    auth_code = config["Settings"]["Auth_code"]
    sleep_delay = config["Settings"]["Sleep_delay"]
    Volume_value = config["Settings"]["Volume_value"]
    Playlist_path = config["Settings"]["Playlist_path"]
    alarm_type = config["Settings"]["alarm_type"]
