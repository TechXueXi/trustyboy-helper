from func.common import *
from func.user import *
import selenium
from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from func.dingding import DingDingHandler
from func.pluspush import PlusPushHandler
from pyzbar.pyzbar import decode
from PIL import Image
from io import BytesIO
import re
import urllib.parse


class XCore:

    def __init__(self, noimg=True, nohead=True, nofake=False):

        try:
            self.options = Options()
            self.nohead = nohead
            # 判断Chrome 位置，linux&macos 后期再加入输入参数，暂时统一处理
            if os.path.exists(get_appsyspatch() + "\App\chrome.exe"):
                chrome_app_path = get_appsyspatch() + "\App\chrome.exe"
                chrome_driver_path = get_appsyspatch() + "\App\chromedriver.exe"
            else:
                if os.path.exists("C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"):  # win
                    chrome_app_path = "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
                    chrome_driver_path = get_appsyspatch() + "\App\chromedriver.exe"
                elif os.path.exists("/usr/lib/chromium/chromium"):  # linux & macos
                    chrome_app_path = "/usr/lib/chromium/chromium"
                    chrome_driver_path = "/usr/lib/chromium/chromedriver"
                elif os.path.exists("/usr/lib/chromium/chrome"):  # alpine
                    chrome_app_path = "/usr/lib/chromium/chrome"
                    chrome_driver_path = "/usr/lib/chromium/chromedriver"
                else:
                    print("@启动失败，程序包已损坏")
                    os._exit(0)
            self.options.binary_location = chrome_app_path
            # 初始二维码窗口大小
            windows_size = '--window-size=500,450'
            user_agent_set = self.getheaders()  # 随机UA
            self.options.add_argument(f'--user-agent={user_agent_set}')
            if noimg:
                self.options.add_argument(
                    'blink-settings=imagesEnabled=true')  # 不加载图片, 提升速度，但无法显示二维码
            if nohead:
                self.options.add_argument('--headless')
                self.options.add_argument('--disable-extensions')
                self.options.add_argument('--disable-dev-shm-usage')
                self.options.add_argument('--disable-gpu')
                self.options.add_argument('--no-sandbox')
                windows_size = '--window-size=1920,1080'
                # self.options.add_argument('--start-maximized')

            self.options.add_argument('--mute-audio')  # 关闭声音
            self.options.add_argument(windows_size)
            # Chrome启动位置
            self.options.add_argument('--window-position=0,0')
            self.options.add_argument('--log-level=3')
            # 忽略掉证书错误
            # self.options.add_argument("--ignore-certificate-errors")
            # 忽略掉ssl错误
            # self.options.add_argument("--ignore-ssl-errors")
            # 忽略 webdriver 错误信息输出到控制台
            #self.options.add_experimental_option('excludeSwitches', ['enable-logging'])

            # 启动Chrome页面崩溃时用
            self.options.add_argument(
                '--disable-features=RendererCodeIntegrity')
            # 打开Chome时屏蔽显示浏览器正在被控制
            self.options.add_argument("--disable-blink-features")
            self.options.add_argument(
                "--disable-blink-features=AutomationControlled")

            self.options.add_experimental_option(
                'excludeSwitches', ['enable-automation'])
            self.options.add_experimental_option(
                'useAutomationExtension', False)

            self.webdriver = webdriver
            self.driver = self.webdriver.Chrome(
                chrome_driver_path, chrome_options=self.options)
            # 加载屏蔽Webdriver标识脚本
            if nofake == False:
                try:
                    net_stealth = requests.get(
                        "https://cdn.jsdelivr.net/gh/requireCool/stealth.min.js/stealth.min.js").content.decode("utf8")
                    self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                        "source": net_stealth
                    })
                except:
                    pass
        except:
            print("=" * 60)
            print("内置驱动初始化失败")
            print("=" * 60)
            raise

    def getheaders(self):
        fake_useragent = [
            # 最新UA不一定随机就是好，按具体情况使用
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win32; x86) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36"
        ]
        UserAgent = random.choice(fake_useragent)
        return UserAgent

    def get_url(self, url):
        self.driver.get(url)

    def base64_to_image(self, base64_str):
        base64_data = re.sub('^data:image/.+;base64,', '', base64_str)
        byte_data = base64.b64decode(base64_data)
        image_data = BytesIO(byte_data)
        img = Image.open(image_data)
        return img

    def logging(self):
        try:
            tryCount = 1
            maxCount = int(xue_cfg["base"]["maxtrylogin"]) + 1
            while tryCount < maxCount:
                print("正在打开二维码登陆界面,请稍后...")
                self.driver.get("https://pc.xuexi.cn/points/login.html")
                # 删除登录二维码界面多余元素
                try:
                    remover = WebDriverWait(self.driver, 30, 0.2).until(
                        lambda driver: driver.find_element_by_class_name("redflagbox"))
                except exceptions.TimeoutException:
                    print("当前网络缓慢...")
                else:
                    self.driver.execute_script(
                        'arguments[0].remove()', remover)
                try:
                    remover = WebDriverWait(self.driver, 30, 0.2).until(
                        lambda driver: driver.find_element_by_class_name("layout-header"))
                except exceptions.TimeoutException:
                    print("当前网络缓慢...")
                else:
                    self.driver.execute_script(
                        'arguments[0].remove()', remover)
                try:
                    remover = WebDriverWait(self.driver, 30, 0.2).until(
                        lambda driver: driver.find_element_by_class_name("layout-footer"))
                except exceptions.TimeoutException:
                    print("当前网络缓慢...")
                else:
                    self.driver.execute_script(
                        'arguments[0].remove()', remover)
                try:
                    remover = WebDriverWait(self.driver, 30, 0.2).until(
                        lambda driver: driver.find_element_by_class_name("oath"))
                except exceptions.TimeoutException:
                    print("当前网络缓慢...")
                else:
                    self.driver.execute_script(
                        'arguments[0].remove()', remover)
                    self.driver.execute_script(
                        'window.scrollTo(document.body.scrollWidth/2 - 200 , 0)')
                # 取出iframe中二维码，并发往钉钉
                if self.nohead == True:
                    QRcode_src = self.getQRcode()
                    img = self.base64_to_image(base64_str=QRcode_src)
                    decocdeQR = decode(img)
                    url = "dtxuexi://appclient/page/study_feeds?url=" + \
                        urllib.parse.quote(decocdeQR[0].data.decode('ascii'))
                    print("发送二维码...\n" + "=" * 60)
                    URID = self.sendMessage(msg=url, mode="link")
                else:
                    print("等待用户扫描二维码...\n" + "=" * 60)
                try:
                    WebDriverWait(self.driver, 120, 1).until(
                        EC.title_is(u"我的学习"))
                    cookies = self.driver.get_cookies()
                    userID, userName = get_userInfo(cookies)
                    save_user_cookies(cookies, userID)
                    return cookies, None
                except Exception as e:
                    print("等待扫描超时，等待再次重试")
                    tryCount = tryCount + 1
                    if xue_cfg.has_option("base", "tryloginsleep"):
                        time.sleep(int(xue_cfg["base"]["tryloginsleep"]))
            print("登录超时，退出程序")
            os._exit(0)
        except KeyError as e:
            print("生成二维码登录失败，请手动扫描二维码登陆...")
            URID = 0

    def sendMessage(self, msg, mode="msg"):
        if xue_cfg["push"]["PushMode"] == "2":
            token = xue_cfg["push"]["DDtoken"]
            secret = xue_cfg["push"]["DDsecret"]
            if token is not None and secret is not None:
                ddhandler = DingDingHandler(token, secret)
                ddhandler.ddmsgsend(msg, mode)
            else:
                print("钉钉token未设置，取消发送消息")
        elif xue_cfg["push"]["PushMode"] == "3":
            token = xue_cfg["push"]["PPtoken"]
            if token is not None:
                ddhandler = PlusPushHandler(token)
                ddhandler.ppmsgsend(msg, mode)
            else:
                print("PlusPush token未设置，取消发送消息")

    def getQRcode(self):
        try:
            # 获取iframe内的二维码
            self.driver.switch_to.frame(
                WebDriverWait(self.driver, 30, 0.2).until(
                    lambda driver: driver.find_element_by_id("ddlogin-iframe"))
            )
            img = WebDriverWait(self.driver, 30, 0.2).until(
                lambda driver: driver.find_element_by_tag_name("img")
            )
            path = img.get_attribute("src")
            self.driver.switch_to.default_content()
        except exceptions.TimeoutException:
            print("当前网络缓慢...")
        else:
            return path

    def set_cookies(self, cookies):
        try:
            for cookie in cookies:
                if cookie['domain'] == 'pc.xuexi.cn':
                    self.driver.get("https://pc.xuexi.cn/")
                if cookie['domain'] == '.xuexi.cn':
                    self.driver.get("https://www.xuexi.cn/")
                    # print(f'current cookie: {cookie}')
                    self.driver.add_cookie(cookie)
        except exceptions.InvalidCookieDomainException as e:
            print(e.__str__)

    def quit(self):
        self.driver.quit()

    def click_xpath(self, xpath):
        try:
            self.condition = EC.visibility_of_element_located(
                (By.XPATH, xpath))
            WebDriverWait(driver=self.driver, timeout=15,
                          poll_frequency=1).until(self.condition)
        except Exception as e:
            print("加载页面失败：", str(e))
        self.driver.find_element_by_xpath(xpath).click()

    # 实验功能，检测是否有验证滑块等，用于检测是否被网站反检测到脚本
    def check_swiper(self):
        tryTimes = 0
        while tryTimes < 5:
            tryTimes += 1
            if self.driver.find_elements_by_class_name("nc-mask-display"):
                print("出现滑块验证。")
                time.sleep(1)
                self.swiper_valid()
                time.sleep(5)
                if self.driver.find_elements_by_class_name("nc-mask-display"):
                    print("滑块解锁失败，进行重试。")
                    continue
                else:
                    print("滑块解锁成功")
                    break
            else:
                break
        if tryTimes >= 5:
            print("滑块解锁失败")
            raise Exception("滑块解锁失败")

    def swiper_valid(self):
        try:
            builder = ActionChains(self.driver)
            builder.reset_actions()
            track = self.move_mouse(300)
            btnSlide = self.driver.find_element_by_class_name("btn_slide")
            builder.move_to_element(btnSlide)
            builder.click_and_hold()
            time.sleep(0.2)
            for i in track:
                builder.move_by_offset(xoffset=i, yoffset=0)
                builder.reset_actions()
            time.sleep(1)
            # 释放左键，执行for中的操作
            builder.release().perform()
            time.sleep(5)
            self.swiper_valid()
        except Exception as e:
            pass

    # 鼠标移动
    def move_mouse(self, distance):
        remaining_dist = distance
        moves = []
        a = 0
        # 加速度，速度越来越快...
        while remaining_dist > 0:
            span = random.randint(15, 20)
            a += span
            moves.append(a)
            remaining_dist -= span
            if sum(moves[:-1]) > 300:
                print(sum(moves))
                break
        return moves

    def get_tips(self, mode=1, answer_num=None):
        content = ""
        answer = "不知道"
        tip_full_text = "无"
        if mode == 2 and answer_num:
            print("正在回答专项答题: 第 " + str(answer_num) + " 题")

        try:
            tips_open = self.driver.find_element_by_xpath(
                '//*[@id="app"]/div/div[*]/div/div[*]/div[*]/div[*]/span[contains(text(), "查看提示")]')
            print("正在识别答案提示...")
            # time.sleep(1)
            tips_open.click()
            time.sleep(1)
        except Exception as e:
            print("无法识别答案提示！")
            return answer, tip_full_text

        try:
            # tips ant-popover-open #app .q-body .tips .ant-popover-open
            check_tips_open = self.driver.find_element_by_css_selector(
                ".tips.ant-popover-open")
            check_tips_open.click()
            time.sleep(1)
            print("答案提示信息处理完成")  # 调试用
        except Exception as e:
            # print("无法识别答案提示！")
            print("处理答案提示过程异常" + str(e))  # 调试用
            # os.system("pause")
            # pass

        tip_div = self.driver.find_element_by_css_selector(
            ".ant-popover .line-feed")
        time.sleep(1)
        tip_html = tip_div.get_attribute('innerHTML')
        tip_full_text = tip_html

        # 返回的答案必须为List
        if "请观看视频" not in tip_html:
            answer = self.format_tips(tip_html)
        else:
            answer = ["请观看视频"]
        print('获得答案提示：', answer)

        return answer, tip_full_text

    def radio_get_options(self):
        get_options = self.driver.find_elements_by_css_selector(
            ".q-answer.choosable")
        answer_options = []
        for i in get_options:
            answer_options.append(i.text)
        print('获取答题选项：', answer_options)
        # os.system("pause")
        return answer_options

    def radio_check(self, check_options):
        for check_option in check_options:
            try:
                button_click = self.driver.find_element_by_xpath(
                    '//*[@id="app"]/div/div[*]/div/div[*]/div[*]/div[*]/div[contains(text(), "' + check_option + '")]')
                #self.driver.execute_script("arguments[0].click();", button_click)
                button_click.click()
                time.sleep(1)
            except Exception as e:
                print("选择答案", check_option, '失败！')
                print(e)

        # 选完答案缓缓再提交
        check_delay()
        # 检查提交下一题或交卷按钮是否可用
        self.check_next_botton()
        # 检测验证滑块，一般只有检测到 Webdriver标识才会出现
        # 实验功能，用于调试
        self.check_swiper()

    def fill_in_blank(self, answer, movie=False):
        check_blank_num = 0
        try:
            check_blank = self.driver.find_elements_by_css_selector(
                "#app .q-body input")
            check_blank_num = len(check_blank)
            # print(check_blank_num) #调试使用
        except Exception as e:
            print("无法找到填空格位置！" + str(e))
            return False

        # 识别多字符串处理
        answer_num = len(answer)
        if check_blank_num == 1 and answer_num > 1:
            answer = ''.join(answer)
            answer = answer.split(',')
            print('DEBUG-1002#1: 答案提示要素已合并处理')

        # 可能有很多个填空栏
        for i in range(0, check_blank_num):
            check_blank[i].send_keys(answer[i])

        # 填完答案缓缓再提交
        check_delay()
        # 检查提交下一题或交卷按钮是否可用
        self.check_next_botton()
        # 检测验证滑块，一般只有检测到 Webdriver标识才会出现
        # 实验功能，用于调试
        self.check_swiper()

    def format_answer(self, answer):
        answer = re.sub(r'<input[^<]*>', '______', answer)
        answer = re.sub(r'<div[^<]*>|<span[^<]*>|</div>|</span>', '', answer)
        return answer

    def format_tips(self, tips):
        tips = re.findall(r'<font[^<]*</font>', tips)
        tip = ','.join(tips)
        tip = re.sub(r'<font[^<]*>|</font>', '', tip)
        tip = tip.split(',')
        return tip

    def check_next_botton(self):
        next_submit = self.driver.find_elements_by_css_selector(
            "#app .action-row > button")
        if len(next_submit) > 1:
            #next_submit_attr = next_submit[1].get_attribute("disabled")
            next_submit[1].click()
            print("已成功交卷！")
            time.sleep(5)
            # return next_submit_attr
        else:
            # print(next_submit[0].get_attribute("disabled"))
            #next_submit_attr = next_submit[0].get_attribute("disabled")
            if next_submit[0].get_attribute("disabled") == None:
                next_submit[0].click()
                print("正在加载下一题")
                time.sleep(2)
            else:
                return False
        # 检查是否有答错题目
        try:
            right_answerlog = []
            check_right_answer = self.driver.find_element_by_css_selector(
                "#app .explain .answer")
            right_answer = check_right_answer.text
            print(color.yellow("找到参考" + right_answer))
            # 此处作为暂时处理，所有打错题目都暂记录到电影题目日志中
            right_answerlog.append(right_answer)
            log_data("/User/QS_Movie.log", right_answerlog)
            print("加载失败，正在重新加载下一题...")
            #self.driver.execute_script("arguments[0].click();", next_submit[0])
            next_submit = self.driver.find_elements_by_css_selector(
                "#app .action-row > button")
            next_submit[0].click()
            time.sleep(1)
        except Exception as e:
            #print("没有检查到答案解释" + str(e))
            pass

    def select_answer_page(self, model, mode="notall"):

        data_select = 0
        if model == "daily":
            #model_name = '每日答题'
            pass
        elif model == "weekly":
            model_name = '每周答题'
            model_selector = "#app .month .week button"
        elif model == "special":
            model_name = '专项答题'
            model_selector = "#app .items .item button"

        next_page_button = self.driver.find_elements_by_css_selector(
            "#app .ant-pagination-next")
        while len(next_page_button) == 1 and next_page_button[0].get_attribute("aria-disabled") == "false":
            select_page = self.driver.find_elements_by_css_selector(
                model_selector)
            for i in range(len(select_page) - 1, -1, -1):  # 从最后一个遍历到第一个
                j = select_page[i]
                if ("重新" in j.text or "满分" in j.text):
                    continue
                else:
                    # 实验功能，跳过电影专题，开始
                    if model == "special":
                        toclick = j
                        dati_title = self.driver.find_elements_by_css_selector(
                            "#app .items .item .item-title")[i]
                        time.sleep(1)
                        # print(dati_title.text) #调试用
                        if ("电影试题" in dati_title.text):
                            print('发现有未答的电影试题，自动略过...')
                            continue
                        else:
                            toclick.click()
                            time.sleep(2)
                            data_select = 1
                            # os.system("pause")
                            break
                    # 实验功能，跳过电影专题，结尾
                    j.click()
                    time.sleep(1)
                    data_select = 1
                    break
            if data_select == 1:
                break

            print('获取' + model_name + '下一页')
            next_page_button[0].click()
            time.sleep(1)
            next_page_button = self.driver.find_elements_by_css_selector(
                "#app .ant-pagination-next")
