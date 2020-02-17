import os
import uuid
import urllib.parse
import logging
from homeassistant.components.http import HomeAssistantView
from aiohttp import web
# ----------邮件相关---------- #
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr
import smtplib

def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))
# ----------邮件相关---------- #

from .api_msg import ApiMsg

_LOGGER = logging.getLogger(__name__)

DOMAIN = 'ha_qqmail'
VERSION = '1.1'
URL = '/' + DOMAIN + '-api-' + str(uuid.uuid4())
ROOT_PATH = '/' + DOMAIN +'-local/' + VERSION

def setup(hass, config):
    # 显示插件信息
    _LOGGER.info('''
-------------------------------------------------------------------
    QQ邮箱通知插件【作者QQ：635147515】
    
    版本：''' + VERSION + '''    
        
    项目地址：https://github.com/shaonianzhentan/ha_qqmail
-------------------------------------------------------------------''')
    cfg  = config[DOMAIN]
    # 注册静态目录
    local = hass.config.path('custom_components/'+DOMAIN+'/local')
    if os.path.isdir(local):
        hass.http.register_static_path(ROOT_PATH, local, False)

    _qq = str(cfg.get('qq')) + '@qq.com'
    _code = cfg.get('code')

    qqmail = QQMail(hass, _qq, _code)
    qqmail.api_msg = ApiMsg(hass, qqmail)
    hass.services.register(DOMAIN, 'notify', qqmail.notify)

    hass.http.register_view(HassGateView)
    return True

class QQMail:

    def __init__(self, hass, from_addr, password):
        self.from_addr = from_addr
        self.password = password
        self._hass = hass
        self.log = _LOGGER.info

    def sendMail(self, to_addr, _title, _message):
        try:
            from_addr = self.from_addr
            smtp_server = 'smtp.qq.com'
            msg = MIMEText(_message, 'html', 'utf-8')
            msg['From'] = _format_addr('HomeAssistant <%s>' % from_addr)
            msg['To'] = _format_addr('智能家居 <%s>' % to_addr)
            msg['Subject'] = Header(_title, 'utf-8').encode()
            server = smtplib.SMTP(smtp_server, 25)
            server.set_debuglevel(1)
            server.login(from_addr, self.password)
            server.sendmail(from_addr, [to_addr], msg.as_string())
            server.quit()            
            _LOGGER.info('【' + _title + '】邮件通知发送成功')
        except Exception as e:
            _LOGGER.info('【' + _title + '】邮件通知发送失败')
            _LOGGER.info(e)


    def notify(self, call):
        data = call.data
        hass = self._hass
        from_addr = self.from_addr
        _title = data['title']
        _message = data['message']
        _entity = None
        _action = None
        if 'entity' in data:
            _entity = data['entity']
        if 'action' in data:
            _action = data['action']
            # _message = _message + '<br/><br/><a href="' + hass.config.api.base_url.strip('/') + URL + '?action=' +  call.data['action'] + '" style="background:#03a9f4;color:white;padding:15px 0;text-decoration:none;display:block;text-align:center;">执行命令</a>' 
        
        _message = self.api_msg.default(_message, _entity, _action, hass.config.api.base_url.strip('/') + URL)

        if 'email' in data and data['email'] != None and data['email'] != '':
            from_addr = data['email']
            
        # 发送邮件
        self.sendMail(from_addr, _title, _message)
    

class HassGateView(HomeAssistantView):

    url = URL
    name = DOMAIN
    requires_auth = False
    
    async def get(self, request):
        # 这里进行重定向
        hass = request.app["hass"]
        if 'action' in request.query:
            _action = urllib.parse.unquote(request.query['action'])
            arr = _action.split('.', 1)
            if arr[0] == 'script':
                await hass.services.async_call('script', str(arr[1]))
            elif arr[0] == 'automation':
                await hass.services.async_call('automation', 'trigger', {'entity_id': _action})
            return web.HTTPFound(location= ROOT_PATH + '/tips.html?msg=执行成功&id=' + _action)
        else:
            return self.json({'code': '401', 'msg': '参数不正确'})