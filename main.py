import requests
import time
from bs4 import BeautifulSoup
from datetime import datetime, timezone, timedelta


def post2mvdis(url, licenseTypeCode, expectExamDateStr, dmvNoLv1, dmvNo):
    request_headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 '
                      'Safari/537.36 Edg/115.0.1901.203',
        # 'referer': 'https://www.mvdis.gov.tw/m3-emv-trn/exm/locations',
    }
    form_data = {
        'method': 'query',
        'secDateStr': '',
        'secId': '',
        'licenseTypeCode': licenseTypeCode,
        'expectExamDateStr': expectExamDateStr,
        'dmvNoLv1': dmvNoLv1,
        'dmvNo': dmvNo,
    }
    r = requests.post(url, headers=request_headers, data=form_data)
    r.encoding = 'utf-8'
    # print(r.text)
    print("成功爬取網頁")
    return r.text


def savefile(text):
    f = open("Temp.html", "w", encoding='utf8')
    f.write(text)
    f.close()
    print("成功存檔")


def loadfile():
    f = open("Temp.html", 'r', encoding='utf8')
    text = f.read()
    f.close()
    print("成功讀檔")
    return text


def findtable(text):
    context = BeautifulSoup(text, "html.parser")  # 格式化
    # 找到讀取的 table
    result = context.find("table", class_="tb_list_std gap_b2 gap_t")
    tbody = result.find('tbody')
    tr_tags = tbody.find_all('tr')

    Date = []
    Desc = []
    Number = []
    All = []
    columns = ['Date', 'Desc', 'Number']

    # 預先放入 table 欄位名稱
    All.append(columns)

    for tr in tr_tags:
        all = []
        td_tags = tr.find_all('td')
        # 日期
        Date.append(td_tags[0].text.strip())
        all.append(td_tags[0].text.strip())
        # 場次組別
        temp = td_tags[1].text.strip()
        Desc.append(temp[0:10])
        all.append(temp[0:10])
        # 可報名人數
        Number.append(td_tags[2].text.strip())
        all.append(td_tags[2].text.strip())

        All.append(all)
    print("成功提取所需表單內容")
    return All


def chooseExpectExamDate(All, InputDate):
    DateStr = []
    DateStr.append('欄位名(佔位用)')

    for i in range(len(All)):
        # 跳過欄位名
        if i >= 1:
            DateTemp = All[i][0]
            # 替代 年
            DateTemp = DateTemp.replace('年', ',')
            # 替代 月
            DateTemp = DateTemp.replace('月', ',')
            # 替代 日
            DateTemp = DateTemp.replace('日', ',')
            # 拆分字串
            DateArray = DateTemp.split(',')
            # 刪除最後一個元素
            DateArray.pop(3)

            # 將月份補為兩位數
            if int(DateArray[1]) < 10:
                DateArray[1] = '0' + DateArray[1]
            # 將日期補為兩位數
            if int(DateArray[2]) < 10:
                DateArray[2] = '0' + DateArray[2]

            Temp = DateArray[0] + DateArray[1] + DateArray[2]

            DateStr.append(Temp)

    # print(DateStr)

    # 與想要日期清單做比對且沒有額滿的話提取數據
    i = 0
    length = int(len(All))
    marklist = []
    while i < length:
        for j in range(len(InputDate)):
            if (str(DateStr[i]) == str(InputDate[j])) & (str(All[i][2]) != '額滿'):
                marklist.append(All[i][:])
        i = i + 1
    # print(i)
    print("與選擇的日期比對完成")
    print(marklist)
    return marklist


def tabletoimage(All):
    import os
    from matplotlib.font_manager import fontManager
    import matplotlib as mpl
    import matplotlib.pyplot as plt
    import wget

    # 確認是否有台北思源黑體
    if os.path.isfile("./TaipeiSansTCBeta-Regular.ttf"):
        print("字體檔案存在。")
    else:
        print("字體檔案不存在，下載台北思源黑體中..")
        # 下載台北思源黑體
        wget.download('https://drive.google.com/uc?id=1eGAsTN1HBpJAkeVM57_C7ccp7hbgSz3_&export=download')

    # 更改matplotlib字體
    fontManager.addfont('TaipeiSansTCBeta-Regular.ttf')
    mpl.rc('font', family='Taipei Sans TC Beta')

    # 將表轉為png
    plt.axis('off')
    plt.table(cellText=All[1:], colLabels=All[0], loc="center")
    plt.savefig('Output.png', bbox_inches='tight')


def linenotify1(token):
    # 要發送的訊息
    dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
    dt2 = dt1.astimezone(timezone(timedelta(hours=8)))  # 轉換時區 -> 東八區
    message = dt2.strftime("%Y-%m-%d %H:%M:%S")

    # HTTP 標頭參數與資料
    headers = {"Authorization": "Bearer " + token}
    data = {'message': message}

    # 要傳送的圖片檔案
    image = open('Output.png', 'rb')
    files = {'imageFile': image}

    # 以 requests 發送 POST 請求
    requests.post("https://notify-api.line.me/api/notify",
                  headers=headers, data=data, files=files)
    print("已送出 Line Notify")


def linenotify2(token, marklist):
    # 要發送的訊息
    dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
    dt2 = dt1.astimezone(timezone(timedelta(hours=8)))  # 轉換時區 -> 東八區

    message = dt2.strftime("%Y-%m-%d %H:%M:%S") + '\n'
    for i in range(len(marklist)):
        message = message + str(marklist[i][0]) + ',' + str(marklist[i][1][0:4]) + ',剩餘: ' + str(marklist[i][2])
        message = message + '\n'

    # HTTP 標頭參數與資料
    headers = {"Authorization": "Bearer " + token}
    data = {'message': message}

    # 以 requests 發送 POST 請求
    requests.post("https://notify-api.line.me/api/notify",
                  headers=headers, data=data)
    print("已送出 Line Notify")


def now_AD2ROCera():
    dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
    dt2 = dt1.astimezone(timezone(timedelta(hours=8)))  # 轉換時區 -> 東八區
    roctra = int(dt2.strftime("%Y%m%d")) - 19110000
    # print(roctra)
    return str(roctra)


def job(num):
    # 監理服務網 - 考照預約報名網址
    url = 'https://www.mvdis.gov.tw/m3-emv-trn/exm/locations#anchor&gsc.tab=0'
    # 報考照類
    licenseTypeCode = '3'
    # 監理所在區域
    dmvNoLv1 = '70'
    # 監理所詳細地址
    dmvNo = '76',
    # 預期考試日期，預設填今日
    expectExamDateStr = now_AD2ROCera()

    # 選擇的時段
    ChooseDate = [1120829,1120911,1120912]

    # LINE Notify 權杖
    # 參考 https://tools.wingzero.tw/article/sn/1224
    token = 'your token'

    # num=1時，發送包含所有時段的表格
    # num=2時，僅當選擇的時段不是額滿才發送訊息
    if num == 1:
        text = post2mvdis(url, licenseTypeCode, expectExamDateStr, dmvNoLv1, dmvNo)
        # savefile(text)
        # text = loadfile()
        All = findtable(text)
        tabletoimage(All)
        linenotify1(token)
    elif num == 2:
        text = post2mvdis(url, licenseTypeCode, expectExamDateStr, dmvNoLv1, dmvNo)
        # savefile(text)
        # text = loadfile()
        All = findtable(text)
        marklist = chooseExpectExamDate(All, ChooseDate)
        if len(marklist) != 0:
            linenotify2(token, marklist)
    else:
        print("輸入正確數字")

if __name__ == '__main__':
    # 單位秒
    delaytime = 600

    while True:
        dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
        dt2 = dt1.astimezone(timezone(timedelta(hours=8)))  # 轉換時區 -> 東八區
        print(dt2.strftime("%Y-%m-%d %H:%M:%S"))
        # num=1時，發送包含所有時段的表格
        # num=2時，僅當選擇的時段不是額滿才發送訊息
        job(1)
        print("下一次查詢在" + str(delaytime) + '秒以後')
        time.sleep(delaytime)
