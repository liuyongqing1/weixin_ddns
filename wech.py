import json
from wx.WXBizMsgCrypt import *
from wx.ierror import *
import requests
from aliyunsdkcore.client import AcsClient
from aliyunsdkecs.request.v20140526 import DescribeInstancesRequest
from aliyunsdkecs.request.v20140526 import StopInstanceRequest
from aliyunsdkalidns.request.v20150109 import DescribeDomainsRequest, DescribeDomainRecordsRequest, \
    UpdateDomainRecordRequest, AddDomainRecordRequest, DeleteDomainRecordRequest, SetDomainRecordStatusRequest
import json, urllib, re
import sys

# 创建AcsClient实例
client = AcsClient(
    "accesskey",
    "accessSecret",
    "regiond（cn-shenzhen）"
);

# 获取域名信息（修改自己的DomainName）
def list_dns_record(DomainName):
    DomainRecords = DescribeDomainRecordsRequest.DescribeDomainRecordsRequest()
    DomainRecords.set_accept_format('json')
    DomainRecords.set_DomainName(DomainName)
    DomainRecordsJson = json.loads(str(client.do_action_with_exception(DomainRecords).decode('utf8')))
    for x in DomainRecordsJson['DomainRecords']['Record']:
        RR = x['RR']
        if RR == 'rspi':
            Value = x['Value']
            return Value

# 更新域名解析（修改的域名DomainName，和要修改的hostname，修改成hostname_new，解析的类型Types，解析的地址IP）
def edit_dns_record(DomainName, hostname, hostname_new, Types, IP):
    DomainRecords = DescribeDomainRecordsRequest.DescribeDomainRecordsRequest()
    DomainRecords.set_accept_format('json')
    DomainRecords.set_DomainName(DomainName)
    DomainRecordsJson = json.loads(client.do_action_with_exception(DomainRecords).decode('utf-8'))
    for x in DomainRecordsJson['DomainRecords']['Record']:
        if hostname == x['RR']:
            RecordId = x['RecordId']
            UpdateDomainRecord = UpdateDomainRecordRequest.UpdateDomainRecordRequest()
            UpdateDomainRecord.set_accept_format('json')
            UpdateDomainRecord.set_RecordId(RecordId)
            UpdateDomainRecord.set_RR(hostname_new)
            UpdateDomainRecord.set_Type(Types)
            UpdateDomainRecord.set_TTL('600')
            UpdateDomainRecord.set_Value(IP)
            UpdateDomainRecordJson = json.loads(str(client.do_action_with_exception(UpdateDomainRecord).decode('utf-8')))
            print(UpdateDomainRecordJson)

class weixin_msg(object):
    def __init__(self,corpid,corpsecret):
        self.corpid=corpid
        self.corpsecret=corpsecret

    def GetToken(self):
        url='https://qyapi.weixin.qq.com/cgi-bin/gettoken'
        param={
            'corpid':self.corpid,
            'corpsecret':self.corpsecret
        }
        res_Token=requests.get(url,params=param).text
        Token=json.loads(res_Token)['access_token']
        return Token

    def Message(self,agentid,msg):
        msg={
           "touser" : "@all",
           # "toparty" : "PartyID1|PartyID2",
           "totag" : "TagID1 | TagID2",
           "msgtype" : "text",
           "agentid" : agentid,
           "text" : {
               "content" : msg
           },
           "safe":0
        }
        msgs=json.dumps(msg)
        return msgs

    def Get_Ip(self):
        url='http://ip.sb'
        header={'User-Agent':'curl/7.54.0'}
        Ip_Addr=requests.get(url,headers=header).text
        return Ip_Addr

    def send_Message(self,agentid,msg):
        url='https://qyapi.weixin.qq.com/cgi-bin/message/send'
        try:
            Token=self.GetToken()
        except:
            raise Exception()
        else:
            parm={
                'access_token':Token
            }
        try:
            Res=requests.post(url,data=self.Message(agentid,msg),params=parm).text
        except Exception:
            print(Exception)
        print(Res)
        return Res

if __name__ == '__main__':
    corpid='企业微信 id'
    corpsecret='应用程序id'
    wx=weixin_msg(corpid,corpsecret)
    msg=wx.Get_Ip()
    Doamin_IP=list_dns_record('huaweipay.win')
    if str(Doamin_IP.strip()) != str(msg.strip()):
        wx.send_Message(1000011,msg)
        edit_dns_record('huaweipay.win','rspi','rspi','A',msg.strip())
