from bs4 import BeautifulSoup
from urllib import parse
from aip import AipOcr
from PIL import Image
import numpy as np
import requests
import random
import time
import re
import os

# 抓取网页get
def getHTMLText(url,headers,data):
    try:
        r=session.get(url,headers=headers,params=data,timeout=10)
        r.raise_for_status()
        return r
    except:
        return 'error'

# 抓取网页post方法
def postHTMLText(url,headers,data,Referer):
    headers['Referer']=Referer
    try:
        r=session.post(url,headers=headers,data=data,timeout=10)
        r.raise_for_status()
        return r.text
    except:
        return 'error'

# 爬取验证码图片并返回结果
def getyzm(yzmurl,headers,Referer):
    headers['Referer']=Referer
    rand=random.random()*10000
    yzmurl=yzmurl+str(rand)
    
    root="C://Users//admin//Desktop//"
    path=root+str(rand)+'.jpg'
    try:
        pic=getHTMLText(yzmurl,headers,data={})
        with open(path,'wb') as f:
            f.write(pic.content)
            f.close()
    except:
        print('save failed')
        return 'none'

    image=Image.open(path)
    yzm=OCR(image,root,int(rand))
    if os.path.exists(path):
            os.remove(path)
    return yzm

# 识别图片中的数字加字母
def OCR(image,root,n):
    npath=root+'new'+str(n)+'.jpg'
    image = image.convert('L')

    # 二值化
    threshold=200
    table=[]
    for i in range(256):
        if i < threshold:
            table.append(0)
        else:
            table.append(1)
    image=image.point(table,'1')

    # 去掉图片中的噪声
    out = cut_noise(image)
    out.save(npath)
    with open(npath, 'rb') as f:
        image=f.read()
        f.close()

    # 调用百度api，识别图片中的数字和字母
    APP_ID = '你的app_id'# 请换成你自己的！
    API_KEY = '你的api_key'# 请换成你自己的！
    SECRET_KEY = '你的secret_key'# 请换成你自己的！
    client = AipOcr(APP_ID, API_KEY, SECRET_KEY)
    options = {"detect_language":"true"}
    r=client.webImage(image, options)

    # 去掉识别结果中的特殊字符，同时限定长度为4
    if r.get('error_msg') == None and r['words_result_num'] == 1:
        text=r['words_result'][0]['words']
        exclude_char_list = ' .:\\|\'\"?![],()~@#$%^&*_+-={};<>/¥'
        text = ''.join([x for x in text if x not in exclude_char_list])
        if len(text) > 4:
            text=text[0:4]

        if os.path.exists(npath):
            os.remove(npath)
        return text
    else:
        if os.path.exists(npath):
            os.remove(npath)
        return 'failed'

# 去掉二值化处理后的图片中的噪声
def cut_noise(image):
    cols, rows = image.size # 图片的宽度和高度
    a = np.asarray(image).astype('float')

    # 遍历图片中的每个点去除噪声
    for i in range(1, rows-1):
        for j in range(1, cols-1):
            pixel_set = 0
            for m in range(i-1, i+2):
                for n in range(j-1, j+2):
                    if a[m, n] == 0: # 1为白色,0位黑色
                        pixel_set = pixel_set+1
            if pixel_set < 4 and a[i][j] != 1:
                a[i][j] = 1
    a=a*255
    image = Image.fromarray(a.astype('uint8'))
    return image

#模拟登录
def login(session, whedmajor, id, password):
    login_url = r'https://iaaa.pku.edu.cn/iaaa/oauthlogin.do'
    login_data = {'appid': 'syllabus',
                  'userName': id,
                  'password': password,
                  'randCode': '',
                  'smsCode': '',
                  'otpCode': '',
                  'redirUrl': r'http://elective.pku.edu.cn:80/elective2008/ssoLogin.do'}
    login_headers = {'Host': r'iaaa.pku.edu.cn',
                     'Referer': r'https://iaaa.pku.edu.cn/iaaa/oauth.jsp?appID=syllabus&appName=%E5%AD%A6%E7%94%9F%E9%80%89%E8%AF%BE%E7%B3%BB%E7%BB%9F&redirectUrl=http://elective.pku.edu.cn:80/elective2008/ssoLogin.do',
                     'User-Agent': r'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362',
                     'Origin' : r'https://iaaa.pku.edu.cn'}
    response = session.post(login_url, data=login_data, headers=login_headers)
    token = response.text.split('"')[-2]
    response = session.get(login_url)
    
    login_url = r'http://elective.pku.edu.cn/elective2008/ssoLogin.do'
    rand=random.random()
    login_data = {'rand': str(rand),
                  'token': token}
    login_headers.pop('Origin')
    login_headers.pop('Referer')
    login_headers['Host']=r'elective.pku.edu.cn'
    response = session.get(login_url, params=login_data, headers=login_headers)
    referer = response.url
    pattern = re.compile(r'sida=[0-9a-z]+')
    sida=pattern.search(response.text).group().split('=')[-1]
    
    login_data = {'sida': sida,
                   'sttp': whedmajor}
    login_headers['Referer']=referer
    response = session.get(login_url, params=login_data, headers=login_headers)


print('欢迎使用 dollboyjack刷课机6.0 ！使用此刷课机代表您已知晓使用不当可能带来的一切后果！并愿意承担全部责任！')
id = input('please enter your id: ')
password = input('please enter your password: ')
wants = []
print('请依此输入你想选的课程并按回车键，输入‘PC’结束输入')
while True:
    c = input()
    if c != 'PC':
        wants.append(c)
    else:
        break

while True:
    judge = input('主修刷课请输入‘1’，双学位刷课请输入‘2’:')
    if judge == '1':
       whedmajor='bzx'
       break
    elif judge == '2':
       whedmajor='bfx'
       break

yzmurl=r'http://elective.pku.edu.cn/elective2008/DrawServlet?Rand='
geturl=r'http://elective.pku.edu.cn/elective2008/edu/pku/stu/elective/controller/supplement/SupplyCancel.do'
postyzmurl=r'http://elective.pku.edu.cn/elective2008/edu/pku/stu/elective/controller/supplement/validate.do'
elecurl=r'http://elective.pku.edu.cn/elective2008/edu/pku/stu/elective/controller/supplement/electSupplement.do'
headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362',
         'Host':'elective.pku.edu.cn',
         'Referer':r'http://elective.pku.edu.cn/elective2008/edu/pku/stu/elective/controller/help/HelpController.jpf'}

# 登录
session = requests.Session()
login(session, whedmajor, id, password)

while True:
    html=getHTMLText(geturl,headers,data={}).text
    soup=BeautifulSoup(html,'lxml')
    courses=soup.select('a[href^="/elective2008/edu/pku/stu/elective/controller/supplement/electSupplement.do"]')
    mark=[]
    for c in courses:
        lst=c.attrs['onclick'].replace(',','').split("'")
        href=c.attrs['href']
        cname=lst[3]
        judge=lst[-3]
        mark=[cname,judge]
        if mark[0] in wants and mark[1]=='false':
            break
        if mark[0] in wants:
            print(mark)

    if mark[1]=='false':
        print('\a','您想选的《'+mark[0]+'》有名额了！')
        valid='0'
        while valid=='0':
            yzm=getyzm(yzmurl,headers,geturl)
            if yzm == 'failed':
                time.sleep(0.4)
                continue
            data={'validCode': yzm}
            valid=postHTMLText(postyzmurl,headers,data,geturl)
            valid=valid.split('"')[3]
            time.sleep(0.4)

        href=href.split('&')
        index=href[0].split('=')[-1]
        seq=href[1].split('=')[1]
        eid=href[2].split('=')[1]
        rn=href[3].split('=')[1]
        data={'index': index,
              'seq': seq,
              'eid': parse.unquote(eid),
              'rn': rn}
        headers['Referer'] = geturl
        r = getHTMLText(elecurl,headers,data)

        pattern = re.compile(mark[0])
        r = pattern.search(r.text)
        if r != None:
            print('《'+mark[0]+'》选课成功！')
            break
    time.sleep(2)
