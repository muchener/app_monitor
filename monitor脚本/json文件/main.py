# coding: utf-8
import requests
from bs4 import BeautifulSoup
import json
from shutil import copyfile


class Mon:
    def __init__(self):
        self.headers = {'User-Agent': "Mozilla/5.0 (Windows NT 6.3; WOW64; rv:35.0) Gecko/20100101 Firefox/35.0"}
        self.config = "config.json"
        self.destination_file = "config.json.bak"

    def call_request(self, url, num=0):
        try:
            res = requests.get(url)
            return res
        except Exception as e:
            if num <= 3:
                num += 1
                self.call_request(url, num)
            else:
                print("Error ,", str(e))


    def send_alert(self,appname, channel, old_version, new_version, message="null"):
        # 这是告警方法
        print("这里告警 appname : {} channel : {} {}-->{}".format(appname, channel,old_version, new_version))

    def call_tencent(self, package):
        url = 'https://sj.qq.com/myapp/detail.htm?apkName={}'.format(package)
        res = self.call_request(url)
        try:
            res = BeautifulSoup(res.text, 'lxml')
            res = res.find_all('div', class_='det-othinfo-data')
            version = res[0].text
            return version
        except Exception as e:
            print("未获取到版本信息")
            print(str(e))


    def call_xiaomi(self,package):
        url = 'https://app.mi.com/details?id={}'.format(package)
        res = self.call_request(url)
        try:
            res = BeautifulSoup(res.text, 'lxml')
            res = res.find_all('div', style='float:right;')
            version = res[2].text
            return version
        except Exception as e:
            print("未获取到版本信息")
            print(str(e))


    def call_huawei(self,package):
        url = 'https://web-drcn.hispace.dbankcloud.cn/uowap/index?method=internal.getTabDetail&serviceType=20&reqPageNum=1&maxResults=25&uri=app%7C{}&locale=zh'.format(package)
        res = self.call_request(url)
        try:
            res = json.loads(res.text)
            version = res["layoutData"][1]['dataList'][0]['versionName']
            return version
        except Exception as e:
            print("未获取到版本信息")
            print(str(e))


    def call_apple(self,package):
        url = "https://apps.apple.com/cn/app/{}".format(package)
        res = self.call_request(url)
        try:
            res = BeautifulSoup(res.text, 'lxml')
            version = res.find_all('p', class_='l-column small-6 medium-12 whats-new__latest__version')
            return version[0].text
        except Exception as e:
            print("未获取到版本信息")
            print(str(e))

    def job(self):
        # 用 pickle sqlite都行 这个简单点
        copyfile(self.config, self.destination_file)
        with open(self.config, 'r', encoding='utf-8') as f:
            data = json.loads(f.read())
            new_data = []
            is_change = False
            for i in data:
                channel_name = i['name']
                package_name = i['package']
                version = i['version']
                app_name = i['app_name']
                func = getattr(self, "call_"+channel_name, None)
                new_version = func(package_name)
                if new_version != version:
                    is_change = True
                    self.send_alert(app_name, channel_name, version, new_version)
                new_data.append({"name": channel_name, "package": package_name, "version": new_version, "app_name": app_name})
        if is_change:
            with open(self.config, 'w', encoding='utf-8') as f:
                new_data = json.dumps(new_data)
                f.write(new_data)



if __name__ == '__main__':
    mon = Mon()
    mon.job()
    # print(mon.call_apple('id1503141029'))
