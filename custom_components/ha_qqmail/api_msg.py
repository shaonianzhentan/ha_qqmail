import requests, base64
from homeassistant.helpers import template

class ApiMsg():

    def __init__(self, hass, mail):
        self.hass = hass
        self.mail = mail

    # 模板解析
    def template(self, _message):
        self.mail.log('【模板解析前】：' + _message)
        # 解析模板
        tpl = template.Template(_message, self.hass)
        _message = tpl.async_render(None)
        self.mail.log('【模板解析后】：' + _message)
        return _message

    # 图片转base64
    def url_to_base64(self, img_url):
        r = requests.get(img_url, headers={}, stream=True)
        if r.status_code == 200:
            base64_data = base64.b64encode(r.content)
            s = base64_data.decode()
            return 'data:image/jpeg;base64,' + s
        return None

    # 默认消息
    def default(self, title, message, data, base_url, URL):
        
        _action = ''
        if 'actions' in data:
            for item in data['actions']:
                _action += '<a href="' + base_url + URL + '?action=' + item['action'] + '''" style="background: #03a9f4;color: white;text-decoration: none;width: 50%; padding: 10px;margin: 5px;">
''' + item['title'] + '</a>'
        # 添加图片
        if 'image' in data:
            # 如果当前图片传入的是摄像头实体ID，则使用实体图片
            entity_id = data['image']
            state = self.hass.states.get(entity_id)
            if state is not None:
                entity_picture = base_url + state.attributes['entity_picture']
                # 进行图片格式转换
                entity_id = self.url_to_base64(entity_picture)
            # 生成图片标签
            message += '<img src="' + entity_id + '" style="max-width:100%;display:block;" />'

        return self.template('''
<div style="padding:10px; box-shadow: 1px 1px 5px silver; border-radius:5px;">
	<h3 style="padding:5px;margin:0;">''' + title + '''</h3>
	<div style="padding:20px 5px;">	''' + message + '''</div>
	<div style="display:flex;text-align:center;">''' + _action + '''</div>
</div>
        ''')