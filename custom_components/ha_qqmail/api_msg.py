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

    # 默认消息
    def default(self, title, message, data, base_url):
        
        _action = ''
        if 'actions' in data:
            for item in data['actions']:
                _action += '<a href="' + base_url + '?action=' + item['action'] + '''" style="background: #03a9f4;color: white;text-decoration: none;width: 50%; padding: 10px;margin: 5px;">
''' + item['title'] + '</a>'

        return self.template('''
<div style="padding:10px; box-shadow: 1px 1px 5px silver; border-radius:5px;">
	<h3 style="padding:5px;margin:0;">''' + title + '''</h3>
	<div style="padding:20px 5px;">	''' + message + '''</div>
	<div style="display:flex;text-align:center;">''' + _action + '''</div>
</div>
        ''')