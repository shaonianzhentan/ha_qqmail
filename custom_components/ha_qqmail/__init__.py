import os
import uuid

from homeassistant.helpers.network import get_url
from homeassistant.components.http import HomeAssistantView
from aiohttp import web
from .qqmail import QQMail

import logging
_LOGGER = logging.getLogger(__name__)

DOMAIN = 'ha_qqmail'
VERSION = '1.4'
URL = '/' + DOMAIN + '-api-' + str(uuid.uuid4())
ROOT_PATH = '/' + DOMAIN +'-local/' + VERSION

def setup(hass, config):
    # 显示插件信息
    _LOGGER.info('''
-------------------------------------------------------------------
    QQ邮箱通知插件【作者QQ：635147515】
    
    版本：''' + VERSION + '''

    API地址：''' + URL + '''
        
    项目地址：https://github.com/shaonianzhentan/ha_qqmail
-------------------------------------------------------------------''')
    # 注册静态目录
    local = hass.config.path('custom_components/'+DOMAIN+'/local')
    if os.path.isdir(local):
        hass.http.register_static_path(ROOT_PATH, local, False)
    # 读取配置    
    cfg  = config[DOMAIN]
    _qq = str(cfg.get('qq')) + '@qq.com'
    _code = cfg.get('code')
    
    base_url = get_url(hass)
    # 定义QQ邮箱实例
    qm = QQMail(hass, _qq, _code, base_url.strip('/') + URL)
    # 设置QQ邮箱通知服务
    if hass.services.has_service(DOMAIN, 'notify') == False:
        hass.services.register(DOMAIN, 'notify', qm.notify)
    # 注册事件网关
    hass.http.register_view(HassGateView)
    return True

class HassGateView(HomeAssistantView):

    url = URL
    name = DOMAIN
    requires_auth = False
    
    async def get(self, request):
        # 这里进行重定向
        hass = request.app["hass"]
        if 'action' in request.query:
            action = request.query['action']
            # 触发事件
            hass.bus.fire("html5_notification.clicked", {"action": action})
            return web.HTTPFound(location= ROOT_PATH + '/tips.html?msg=触发事件成功&id=' + action)
        else:
            return self.json({'code': '401', 'msg': '参数不正确'})