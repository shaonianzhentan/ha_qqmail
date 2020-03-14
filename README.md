# ha_qqmail
在HA里使用的QQ邮箱通知

# 使用方式

```

# 配置后生成【ha_qqmail.notify】服务
ha_qqmail:
  qq: QQ号码
  code: QQ邮箱授权码
  ha_base_url: https://xxx.xxx.com（外网地址，默认本机局域网地址）

```

调用服务格式
```
entity:
  - light.men_kou_de_diao_deng
  - light.fang_jian_de_deng
action:
  - automation.guan_diao_deng
  - automation.guan_fang_jian_de_deng
message: '已经十点了，灯还没有关掉哦，是不是搞忘记了？'
title: 门口的灯还没有关掉

```

# 更新日志

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