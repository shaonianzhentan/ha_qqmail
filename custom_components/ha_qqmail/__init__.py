import os, uuid, logging

from homeassistant.helpers.network import get_url
from homeassistant.components.http import HomeAssistantView
from aiohttp import web
from .qqmail import QQMail

from .const import DOMAIN, VERSION, URL, ROOT_PATH

_LOGGER = logging.getLogger(__name__)

def setup(hass, config):
    # 没有配置和已经运行则不操作
    if DOMAIN not in config or DOMAIN in hass.data:
        return True
    # 显示插件信息
    _LOGGER.info('''
-------------------------------------------------------------------
    QQ邮箱通知插件【作者QQ：635147515】
    
    版本：''' + VERSION + '''

    API地址：''' + URL + '''
        
    项目地址：https://github.com/shaonianzhentan/ha_qqmail
-------------------------------------------------------------------''')
    # 读取配置    
    cfg  = config[DOMAIN]
    _qq = str(cfg.get('qq')) + '@qq.com'
    _code = cfg.get('code')
    # 默认使用自定义的外部链接
    base_url = hass.config.external_url
    # 如果未定义，则使用内网链接
    if base_url is None:
        base_url = hass.config.internal_url
        if base_url is None:
            base_url = hass.config.api.base_url
    # 定义QQ邮箱实例
    qm = QQMail(hass, _qq, _code, base_url.strip('/') + URL)
    hass.data[DOMAIN] = qm
    # 设置QQ邮箱通知服务
    if hass.services.has_service(DOMAIN, 'notify') == False:
        hass.services.async_register(DOMAIN, 'notify', qm.notify)
    # 注册静态目录
    hass.http.register_static_path(ROOT_PATH, hass.config.path('custom_components/' + DOMAIN + '/local'), False)    
    # 注册事件网关
    hass.http.register_view(HassGateView)
    return True

# 集成安装
async def async_setup_entry(hass, entry):
    setup(hass, { DOMAIN: entry.data })
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
