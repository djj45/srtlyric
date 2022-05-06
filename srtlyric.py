import base64
import requests
import json
import time
import os


class Lyric(object):
    def __init__(self, song_id):
        self.song_id = song_id
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36"
        }
        self.lyric_list = []
        self.lyric = ""
        self.trans_lyric = ""
        self.line = ""

    @staticmethod
    def get_lyric_list(line, lyric, trans_lyric, lyric_list):
        for content in lyric:
            if content == "\n":
                lyric_list.append(line)
                line = ""
            else:
                line += content
        for content in trans_lyric:
            if content == "\n":
                lyric_list.append(line)
                line = ""
            else:
                line += content

    @staticmethod
    def write_lrc_file(file_name, lyric_list):
        with open(file_name + ".lrc", "w", encoding="utf-8") as lrc:
            for line in lyric_list:
                lrc.write(line + "\n")
        lrc.close()


class QQ(Lyric):
    def __init__(self, song_id):
        super().__init__(song_id)
        self.lyric_url = "https://c.y.qq.com/lyric/fcgi-bin/fcg_query_lyric_new.fcg"
        self.info_url = "https://c.y.qq.com/v8/fcg-bin/fcg_play_single_song.fcg"
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36",
            "referer": "https://y.qq.com/portal/player.html",
        }
        self.params = {
            "callback": "MusicJsonCallback_lrc",
            "pcachetime": str(round(time.time(), 3)).replace(".", ""),
            "songmid": self.song_id,
            "g_tk": "5381",
            "jsonpCallback": "MusicJsonCallback_lrc",
            "loginUin": "0",
            "hostUin": "0",
            "format": "jsonp",
            "inCharset": "utf8",
            "outCharset": "utf8",
            "notice": "0",
            "platform": "yqq",
            "needNewCode": "0",
        }
        self.song_info = requests.get(url=self.info_url, headers=self.headers, params=self.params).text
        self.info_dict = json.loads(self.song_info.replace("MusicJsonCallback_lrc(", "").replace(")", ""))
        self.song_name = self.info_dict["data"][0]["name"]
        self.singer_name = self.info_dict["data"][0]["singer"][0]["name"]
        self.full_name = self.song_name + "-" + self.singer_name
        self.get_content = requests.get(url=self.lyric_url, headers=self.headers, params=self.params).text
        self.lyric_dict = json.loads(self.get_content.replace("MusicJsonCallback_lrc(", "").replace(")", ""))
        self.lyric = base64.b64decode(self.lyric_dict["lyric"]).decode("utf-8")
        self.trans_lyric = base64.b64decode(self.lyric_dict["trans"]).decode("utf-8")
        self.get_lyric_list(self.line, self.lyric, self.trans_lyric, self.lyric_list)


class Wyy(Lyric):
    def __init__(self, song_id):
        super().__init__(song_id)
        self.lyric_url = "http://music.163.com/api/song/lyric?os=pc&id=" + self.song_id + "&lv=-1&kv=-1&tv=-1"
        self.info_url = "http://music.163.com/api/song/detail/?id=" + self.song_id + "&ids=[" + self.song_id + "]"
        self.song_info = requests.get(url=self.info_url, headers=self.headers).text
        self.info_dict = json.loads(self.song_info)
        self.song_name = self.info_dict["songs"][0]["name"]
        self.singer_name = self.info_dict["songs"][0]["artists"][0]["name"]
        self.full_name = self.song_name + "-" + self.singer_name
        self.get_content = requests.get(url=self.lyric_url, headers=self.headers)
        self.lyric_dict = json.loads(self.get_content.text)
        self.lyric = self.lyric_dict["lrc"]["lyric"]
        self.trans_lyric = self.lyric_dict["tlyric"]["lyric"]
        self.get_lyric_list(self.line, self.lyric, self.trans_lyric, self.lyric_list)


class LyricToSrt(object):
    def __int__(self):
        pass

    @staticmethod
    def check_version(headers):
        try:
            version_resp = requests.get("https://gitee.com/djj45/srtlyric/raw/master/version", headers=headers)
        except:
            try:
                version_resp = requests.get("https://raw.githubusercontent.com/djj45/srtlyric/master/version",
                                            headers=headers)
            except:
                return "error"
            else:
                return version_resp.text
        else:
            return version_resp.text

    def get_version(self, headers):
        new_version = self.check_version(headers)
        try:
            float(new_version)
        except:
            return "error"
        else:
            return float(new_version)

    @staticmethod
    def is_lyric(line):
        return line.split(":")[0].split("[")[1].isdigit()

    @staticmethod
    def get_time(line):
        return line.split("]")[0].split("[")[1]

    @staticmethod
    def get_lyric(line):
        return line.split("]")[1].split("[")[0]

    @staticmethod
    def time_trans(lyric_time):
        if len(lyric_time.split(".")[1]) == 3:
            return (
                    float(lyric_time.split(":")[0]) * 60
                    + float(lyric_time.split(":")[1].split(".")[0])
                    + float(lyric_time.split(".")[1]) * 0.001
            )
        else:
            return (
                    float(lyric_time.split(":")[0]) * 60
                    + float(lyric_time.split(":")[1].split(".")[0])
                    + float(lyric_time.split(".")[1]) * 0.01
            )

    def extend_time(self, lyric_time):
        bit = len(lyric_time.split(".")[1])
        duration = self.time_trans(lyric_time)
        duration += 8
        decimal = str(duration).split(".")[1]
        num = int(str(duration).split(".")[0])
        minutes = str(num // 60)
        seconds = str(num % 60)
        if len(minutes) < 2:
            minutes = "0" + minutes
        if len(seconds) < 2:
            seconds = "0" + seconds
        while len(decimal) < bit:
            decimal += "0"
        return minutes + ":" + seconds + "." + decimal

    def check_time(self, pre_lyric_time, lyric_time, pre_lyric, border_flag):
        if self.time_trans(lyric_time) - self.time_trans(pre_lyric_time) > 8:
            print(pre_lyric_time + " --> " + lyric_time + " " + pre_lyric.replace("\n", ""))
        elif self.time_trans(pre_lyric_time) - self.time_trans(lyric_time) > 50:
            lyric_time = self.extend_time(pre_lyric_time)
            border_flag = True
        return lyric_time, border_flag

    def write_content(self, count, pre_lyric_time, lyric_time, pre_lyric, last_flag=False):
        if not last_flag:
            return (
                    str(count)
                    + "\n"
                    + "00:"
                    + pre_lyric_time.replace(".", ",")
                    + " --> "
                    + "00:"
                    + lyric_time.replace(".", ",")
                    + "\n"
                    + pre_lyric
                    + "\\n"
                    + "\n\n"
            )
        else:
            return (
                    str(count)
                    + "\n"
                    + "00:"
                    + pre_lyric_time.replace(".", ",")
                    + " --> "
                    + "00:"
                    + self.extend_time(lyric_time).replace(".", ",")
                    + "\n"
                    + pre_lyric
                    + "\\n"
                    + "\n\n"
            )

    def write_srt(self, file_name, lyric_list):
        first_lyric_flag = True
        border_flag = False
        count = 0
        with open(file_name + ".srt", "w", encoding="utf-8") as srt:
            for line in lyric_list:
                line = line.replace("//", "")
                if not self.is_lyric(line):
                    continue
                if first_lyric_flag:
                    pre_time = self.get_time(line)
                    pre_lyric = self.get_lyric(line)
                    first_lyric_flag = False
                    continue
                count += 1
                time = self.get_time(line)
                time, border_flag = self.check_time(pre_time, time, pre_lyric, border_flag)
                srt.write(self.write_content(count, pre_time, time, pre_lyric))
                pre_time = time
                pre_lyric = self.get_lyric(line)
                if border_flag:
                    pre_time = self.get_time(line)
                    border_flag = False
            count += 1
            srt.write(self.write_content(count, pre_time, time, pre_lyric, True))
        srt.close()


def get_song_id(user_input):
    if user_input.find("=") != -1:
        return user_input.split("=")[1].strip()
    elif user_input.find("/") != -1:
        return user_input.split("/")[-1].strip()
    else:
        return user_input.strip()


if __name__ == "__main__":
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36"
    }
    version = 20220507
    os.system("")
    print("\033[1;32;40m显示持续时间大于8秒的歌词,请注意是否为间奏,同时注意最后一句歌词(默认持续时间为8秒)\033[0m")
    print("\033[1;32;40m请输入链接或者歌曲id\033[0m")
    song_id = get_song_id(input())
    if song_id.isdigit():
        lyric = Wyy(song_id)
    else:
        lyric = QQ(song_id)
    srt = LyricToSrt()
    srt.write_srt(lyric.full_name, lyric.lyric_list)
    latest_version = srt.get_version(headers)
    if latest_version == "error":
        os.system("")
        print("\033[1;31;40m版本检查失败,请检查网络连接\033[0m")
    elif latest_version > version:
        os.system("")
        print(
            "\033[1;31;40m有新版本,下载链接\nhttps://gitee.com/djj45/srtlyric/releases\nhttps://github.com/djj45/srtlyric/releases\033[0m"
        )
    os.system("pause")
