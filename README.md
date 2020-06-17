# ha_qqmail
在HA里使用的QQ邮箱通知

# 使用方式

```yaml

# 配置后生成【ha_qqmail.notify】服务
ha_qqmail:
  qq: QQ号码
  code: QQ邮箱授权码

```

> 调用服务格式
```yaml
title: 标题
message: 消息内容
data:
  url: https://github.com/shaonianzhentan/ha_qqmail
  image: https://vuejs.org/images/logo.png
  actions:
    - action: close_light
      title: 关灯
    - action: close_all
      title: 关掉全部灯
```

> 获取点击事件(参考链接：https://www.home-assistant.io/integrations/html5/)
```yaml
- alias: 这是一个H5的通知提示
  trigger:
    platform: event
    event_type: html5_notification.clicked
    event_data:
      action: close_light
```

# 更新日志

### v1.4
- 新增查询全部实体状态功能

### v1.3
- 重构代码逻辑
- 删除外网链接配置
- 兼容摄像头实体ID和图片
- 新增url参数，点击标题可以跳转指定链接

### v1.2.1
- 加入图片发送

### v1.2
- 重新邮件通知逻辑，兼容html5通知

### v1.1
- 支持执行多个脚本或自动化
- 模板显示实体状态
- 修复代码错误
- 兼容yaml列表格式

### v1.0
- 发送通知到QQ邮箱
- 发送通知到其它邮箱
- 支持模板消息
- 支持执行脚本或自动化