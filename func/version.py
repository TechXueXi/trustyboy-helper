from func.common import *


def get_version(verstr):
    vernums = ",".join(verstr)
    vernums = re.findall("v\d+", vernums)
    return vernums

def compare_version(ver1, ver2):
    return int(ver1[1:]) - int(ver2[1:])


def up_info():
    print(color.yellow("[*] 正在联网获取更新信息..."))

    __Version = "v20230330"

    __INFO = "By Kenf, Alex"
    try:
        update_log = requests.get(
            "https://ghproxy.com/https://github.com/trustyboy/xxqg-helper/blob/master/Config/Update.html", timeout = 5).content.decode("utf8")
        update_log = update_log.split("\n")
        print(color.yellow("[*] " + __INFO))
        print(color.yellow("[*] 程序版本为：{}".format(__Version)))
        print(color.yellow("[*] 最新版本为：{}".format(update_log[1].split("=")[1])))

        update_version = ",".join(re.findall("v\d+", update_log[1]))
        canuse_version = get_version(update_log[2].split(","))

        if __Version in canuse_version and compare_version(__Version , update_version) < 0:
            print(color.red("[*] 检测到当前不是最新版本，此版本仍在支持列表，但即将失效"))
            print(color.red("[*] " * 15))
            print(color.red("[*] 更新提要："))
            for i in update_log[4:]:
                print(color.red("[*] " + i))
            sendMessage("检测到当前不是最新版本，此版本仍在支持列表，但即将失效")
        elif __Version not in canuse_version and compare_version(__Version , update_version) < 0:
            print(color.red("[*] 检测到当前版本已不再支持，请更新后再运行"))
            print(color.red("[*] " * 15))
            print(color.red("[*] 更新提要："))
            for i in update_log[4:]:
                print(color.red("[*] " + i))
            print(color.red("[*] 程序已中断"))
            sendMessage("检测到当前版本已不再支持，请更新后再运行")
            os._exit(0)
    except:
        print(color.yellow("[*] 验证版本信息网络错误"))
        # os._exit(0)


if __name__ == '__main__':
    up_info()
