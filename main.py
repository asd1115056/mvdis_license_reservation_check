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


def linenotify(token):
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

def now_AD2ROCera():
    dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
    dt2 = dt1.astimezone(timezone(timedelta(hours=8)))  # 轉換時區 -> 東八區
    roctra=int(dt2.strftime("%Y%m%d")) - 19110000
    print(roctra)
    return str(roctra)

def job():
    # 監理服務網 - 考照預約報名網址
    url = 'https://www.mvdis.gov.tw/m3-emv-trn/exm/locations#anchor&gsc.tab=0'
    # 報考照類
    # 普通重型機車 3
    # 普通輕型機車 (50cc 以下) 5
    # 普通小型車 A
    # 職業小型車 B
    # 普通大貨車 C
    # 職業大貨車 D
    # 普通大客車 E
    # 職業大客車 F
    # 普通聯結車 G
    # 職業聯結車 H
    licenseTypeCode = '3'

    # 臺北市區監理所（含金門馬祖） 20
    # 臺北區監理所（北宜花）40
    # 新竹區監理所（桃竹苗） 50
    # 臺中區監理所（中彰投） 60
    # 嘉義區監理所（雲嘉南） 70
    # 高雄市區監理所 30
    # 高雄區監理所（高屏澎東） 80
    dmvNoLv1 = '70'

    # 士林監理站(臺北市士林區承德路5段80號) 21
    # 基隆監理站(基隆市七堵區實踐路296號) 25
    # 金門監理站(金門縣金湖鎮黃海路六之一號) 26
    # 臺北區監理所(新北市樹林區中正路248巷7號) 40
    # 板橋監理站(新北市中和區中山路三段116號) 41
    # 宜蘭監理站(宜蘭縣五結鄉中正路二段9號) 43
    # 花蓮監理站(花蓮縣吉安鄉中正路二段152號) 44
    # 玉里監理分站(花蓮縣玉里鎮中華路427號) 45
    # 蘆洲監理站(新北市蘆洲區中山二路163號) 46
    # 新竹區監理所(新竹縣新埔鎮文德路三段58號) 50
    # 新竹市監理站(新竹市自由路10號) 51
    # 桃園監理站(桃園市介壽路416號) 52
    # 中壢監理站(桃園縣中壢市延平路394號) 53
    # 苗栗監理站(苗栗市福麗里福麗98號) 54
    # 臺中區監理所(臺中市大肚區瑞井里遊園路一段2號) 60
    # 臺中市監理站(臺中市北屯路77號) 61
    # 埔里監理分站(南投縣埔里鎮水頭里水頭路68號) 62
    # 豐原監理站(臺中市豐原區豐東路120號) 63
    # 彰化監理站(彰化縣花壇鄉南口村中山路二段457號) 64
    # 南投監理站(南投縣南投市光明一路301號) 65
    # 嘉義區監理所(嘉義縣朴子市朴子七路29號) 70
    # 東勢監理分站(雲林縣東勢鄉新坤村新坤路333號) 71
    # 雲林監理站(雲林縣斗六市雲林路二段411號) 72
    # 新營監理站(臺南市新營區大同路55號) 73
    # 臺南監理站(臺南市崇德路1號) 74
    # 麻豆監理站(臺南市麻豆區北勢里新生北路551號) 75
    # 嘉義市監理站(嘉義市東區保建街89號) 76
    # 高雄市區監理所(高雄市楠梓區德民路71號) 30
    # 苓雅監理站(高雄市苓雅區安康路22號) 31
    # 旗山監理站(高雄市旗山區旗文路123-1號) 33
    # 高雄區監理所(高雄市鳳山區武營路361號) 80
    # 臺東監理站(臺東市正氣北路441號) 81
    # 屏東監理站(屏東市忠孝路222號) 82
    # 恆春監理分站(屏東縣恒春鎮草埔路11號) 83
    # 澎湖監理站(澎湖縣馬公市光華里121號) 84
    dmvNo = '76',

    # 預期考試日期，預設填今日
    expectExamDateStr = now_AD2ROCera()

    # LINE Notify 權杖
    # 參考 https://tools.wingzero.tw/article/sn/1224
    token = 'your token'

    text = post2mvdis(url, licenseTypeCode, expectExamDateStr, dmvNoLv1, dmvNo)

    # For debug
    # savefile(text)
    # text = loadfile()

    All = findtable(text)
    tabletoimage(All)
    linenotify(token)


if __name__ == '__main__':
    # 單位秒
    delaytime = 600

    while True:
        dt1 = datetime.utcnow().replace(tzinfo=timezone.utc)
        dt2 = dt1.astimezone(timezone(timedelta(hours=8)))  # 轉換時區 -> 東八區
        print(dt2.strftime("%Y-%m-%d %H:%M:%S"))
        job()
        print("下一次查詢在" + str(delaytime) + '秒以後')
        time.sleep(delaytime)

