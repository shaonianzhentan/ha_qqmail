import requests, base64, json
import urllib.parse
from homeassistant.helpers import template
import logging
_LOGGER = logging.getLogger(__name__)

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

class QQMail:

    # 初始化
    def __init__(self, hass, from_addr, password, api_url):
        self.hass = hass
        self.from_addr = from_addr
        self.password = password
        self.api_url = api_url

    # 发送邮件
    def sendMail(self, to_addr, _title, _message):
        try:
            from_addr = self.from_addr
            smtp_server = 'smtp.qq.com'
            msg = MIMEText(_message, 'html', 'utf-8')
            msg['From'] = _format_addr('HomeAssistant <%s>' % from_addr)
            #msg['To'] = _format_addr('智能家居 <%s>' % to_addr)
            msg['To'] = ','.join(to_addr)
            msg['Subject'] = Header(_title, 'utf-8').encode()
            server = smtplib.SMTP(smtp_server, 25)
            server.set_debuglevel(1)
            server.login(from_addr, self.password)
            server.sendmail(from_addr, to_addr, msg.as_string())
            server.quit()            
            _LOGGER.info('【' + _title + '】邮件通知发送成功')
        except Exception as e:
            _LOGGER.info('【' + _title + '】邮件通知发送失败')
            _LOGGER.info(e)

    ######################## 功能 ########################
    # 读取文件内容
    def getContent(self, _path):        
        fp = open(_path, 'r', encoding='UTF-8')
        content = fp.read()
        fp.close()
        return content

    # 通知服务
    def notify(self, call):
        data = call.data
        # 读取服务参数
        _type = data.get('type', '')
        _email = data.get('email', self.from_addr)
        if not isinstance(_email,list):
            _email = [_email]
        _title = data.get('title', '')
        _message = self.template(data.get('message', ''))
        _data = data.get('data', [])
        # 生成操作按钮
        _list = []
        _action = ''
        if 'actions' in _data:
            for item in _data['actions']:
                _list.append({
                    'name': item['title'],
                    'url': self.api_url + '?action=' + item['action']
                })
            if len(_list) > 0:
                _action = self.template('''
        {% set actions = ''' + json.dumps(_list) + ''' %}
        {% for action in actions -%}
            <a href="{{action.url}}" style="background: #03a9f4;color: white;text-decoration: none;width: 50%; padding: 10px;margin: 5px;">{{ action.name }}</a>
        {%- endfor %} ''')

        # 生成图片
        if 'image' in _data:
            _image = _data['image']
            _LOGGER.info('图片地址：' + _image)
            # 判断是否图片地址
            if 'https://' in _image or 'http://' in _image:
                _image = self.url_to_base64(_image)
            else:
                # 如果当前图片传入的是摄像头实体ID，则使用实体图片
                entity_id = _image
                state = self.hass.states.get(entity_id)
                if state is not None:
                    entity_picture = self.hass.config.api.base_url + state.attributes['entity_picture']
                    _LOGGER.info('摄像头图片地址：' + entity_picture)
                    # 进行图片格式转换
                    _image = self.url_to_base64(entity_picture)
                else:
                    _image = ''
            # 生成图片标签
            if _image != '': 
                _message += '<img src="' + _image + '" style="max-width:100%;display:block;" />'

        # 传入URL链接
        if 'url' in data:
            _LOGGER.info('URL链接地址：' + data['url'])
            _title = '<a href="' + data['url'] + '" style="color:#03a9f4;text-decoration: none;">' + _title + '</a>'

        # 如果类型是状态，则查询全部状态
        if _type == 'state':
            _message += self.template('''
            <table border="1px solid #eee" cellspacing="2" cellpadding="10" width="100%" style="width:100%;text-align:left;">
                <tr>
                    <th>设备类型</th>
                    <th>实体名称</th>
                    <th>状态</th>
                </tr>
                {% for state in states -%}
                <tr style="background-color:{% if is_state(state.entity_id, "on") -%}yellow{%- else -%}white{%- endif %};" >
                    <td>{{ state.domain }}</td>
                    <td>{{ state.name }}</td>
                    <td>{{state.state}}</td>
                </tr>
                {%- endfor %}
            </table>
            ''')
        # 读取消息模板
        template_info = self.getContent(self.hass.config.path("custom_components/ha_qqmail/local/template/info.html"))

        # 替换标题和信息，重新生成消息
        _message = template_info.replace('{TITLE}', _title).replace('{CONTENT}', _message).replace('{BUTTON}', _action)
        # 发送邮件
        _LOGGER.info(_message)
        self.sendMail(_email, _title, _message)

    # 模板解析
    def template(self, _message):
        _LOGGER.info('【模板解析前】：' + _message)
        # 解析模板
        tpl = template.Template(_message, self.hass)
        _message = tpl.async_render(None)
        _LOGGER.info('【模板解析后】：' + _message)
        return _message

    # 图片转base64
    def url_to_base64(self, img_url):
        r = requests.get(img_url, headers={}, stream=True)
        if r.status_code == 200:
            base64_data = base64.b64encode(r.content)
            s = base64_data.decode()
            return 'data:image/jpeg;base64,' + s
        return None
