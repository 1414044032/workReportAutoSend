# -*- coding: utf-8 -*-
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import os
import time
from email.mime.base import MIMEBase
import email
import sched
import logging

logging.basicConfig(level=logging.INFO,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='sendWorkReport.log',
                filemode='w')
scheduler = sched.scheduler(time.time,time.sleep)

localReport = "E:\\"
# send person
sender = "1414044032@qq.com"
# password  Generally, third party login is required authorization code
psw = "your password"
# recevie  here It could be yourself
receive = "1414044032@qq.com"


class scheSendWeekReport:

    def __init__(self):
        pass
    # 编写邮件
    def createEmail(self,hour,file_name):
        message = MIMEMultipart('related')
        if hour == 17:
            print("提醒邮件")
            subject = "一小时后将开始发送周报，请及时填写"
            message['Subject'] = subject
            message['From'] = "王刘奇"
            message['To'] = receive
            content = MIMEText(
                '<html><body><h3>请及时填写周报！！</3></body></html>',
                'html',
                'utf-8')
        elif hour == 0:
            print("未发送邮件")
            subject = "路径存在问题，请检查，手动发送邮件"
            message['Subject'] = subject
            message['From'] = "王刘奇"
            message['To'] = receive
            content = MIMEText(
                '<html><body><h3>请检查周报路径</3></body></html>',
                'html',
                'utf-8')
        elif hour ==18:
            print("周报邮件")
            subject = "请注意查收工作周报"
            message['Subject'] = subject
            message['From'] = "王刘奇"
            message['To'] = receive
            content = MIMEText(
                '<html><body><h3>李总：</3> <h4> 您好！附件为上周的工作周报。请您注意查收！</h4></body></html>', 'html',
                'utf-8')
            contype = 'application/octet-stream'
            maintype, subtype = contype.split('/', 1)
            file_msg = MIMEBase(maintype, subtype)
            data = open(file_name, 'rb')
            file_msg.set_payload(data.read())
            data.close()
            email.encoders.encode_base64(file_msg)
            basename = os.path.basename(file_name)
            file_msg.add_header('Content-Disposition', 'attachment', filename=basename)
            message.attach(file_msg)
            message['Date'] = email.utils.formatdate()
        else:
            return None

        message.attach(content)

        return message

    # 发送邮件
    def sendEmail(self,message):
        try:
            server = smtplib.SMTP_SSL("smtp.qq.com", 465)
            server.login(sender, psw)
            server.sendmail(sender, receive, message.as_string())
            server.quit()
            print("邮件发送成功")
        except smtplib.SMTPException as e:
            print("发送失败",e)


    # 检查本地文件修改时间
    def checkLocalReport(self):
        if os.path.exists(localReport):
            if os.path.isdir(localReport):
                fileList = os.listdir(localReport)
                ReportList = []
                for file in fileList:
                    if "工作周报" in file:
                        ReportList.append(os.path.join(localReport,file))
                if len(ReportList) == 1:
                    localReportsend = ReportList[0]
                else:
                    print("目录下存在多个或者不存在包含“工作周报”的文件")
                    return False
            else:
                localReportsend = localReport
            modifytimestamp = os.path.getmtime(localReportsend)
            modifytime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(modifytimestamp))
            logging.info("周报上次修改时间："+str(modifytime))
            # 判断当前时间与文件最近一次修改时间的间距（小时）小于24 则默认为已填写周报
            nowtimestamp = time.time()
            timegap = int((nowtimestamp - modifytimestamp)/60/60)
            if timegap< 24:
                return localReportsend
            else:
                print("周报未进行填写")
                return False
        else:
            print("路径错误")
            return False

# 判断是否为周五
def checkFriDay():
    now_time = datetime.datetime.now().strftime("%w")
    if now_time == "5":
        return True
    else:
        return False

# 获取当前小时数
def getHour():
    now_time = datetime.datetime.now()
    now_hour = now_time.hour
    return now_hour

# 封装函数
def run_loop():
    logging.info(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    # 是否为周五
    if checkFriDay():
        # 周报前一小时提醒
        if getHour() == 17:
            sswr = scheSendWeekReport()
            localtext = sswr.checkLocalReport()
            message = sswr.createEmail(17, localtext)
            sswr.sendEmail(message)
        # 发送周报
        elif getHour() == 18:
            sswr = scheSendWeekReport()
            localtext = sswr.checkLocalReport()
            # 判断文件是否存在
            if localtext:
                message = sswr.createEmail(18, localtext)
                sswr.sendEmail(message)
                scheduler.enter(360*12, 0, run_loop)
            else:
                message = sswr.createEmail(0, localtext)
                sswr.sendEmail(message)
        else:
            scheduler.enter(360,0,run_loop)
    else:
        scheduler.enter(360*12,0,run_loop)


if __name__ =="__main__":
    # 开始sched 循环
    sswr = scheSendWeekReport()
    localtext = sswr.checkLocalReport()
    if localtext:
        scheduler.enter(0,0,run_loop)
        scheduler.run()
    else:
        print("文件夹中不存在在该文件或者路径错误")



