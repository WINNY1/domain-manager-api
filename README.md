# Domain Manager API

>  域名管理系统: 接口
>
>  基于Python3
>
>  依赖: flask, flask_cors, pymysql, requests, gunicorn

## 项目结构

```
.
├── API
│   ├── __init__.py
│   ├── api.py              # Flask主程序, 定义接口路由和行为
│   ├── db.py               # 数据库连接和操作程序, 使用MYSQL
│   ├── get_md5.py          # 加密组件, md5加盐
│   ├── qq_checker.py       # QQ网址安全性检测程序
│   └── we_chat_checker.py  # 微信登陆和域名检测程序
├── README.md               # 说明文档
├── config.py               # 程序设置, 如请求使用的Header, 需要使用的数据库信息等
├── api.sh                  # 控制脚本
└── run.py                  # 启动文件
```

## 接口说明


| API             | Params             | Retuen                   | Reference |
| :-------------- | :----------------: | :----------------------: | :-------------: |
| /api/take_token | None               | Token of the user `test` |为爬虫获取token|
| /api/auto_login | user_id, token     | User's data              |自动登陆|
| /api/login      | username, password | User's id and token      |登陆|
| /api/qq_check | user_id, token, url | Result of check |QQ网址检测|
| /api/we_chat_check | user_id, token, domain | Result of check |微信域名检测|
| /api/login/we_chat/get_qr | None | Url for QRCode |获取微信登陆二维码|
| /api/login/we_chat/get_status | user_id, uuid | Status of login |检测微信登陆状态|
| /api/get_domain | where_condition, row_count, offset | list of domain |从数据库获取域名信息|
| /api/get_user_information | user_id, token | Information of Users |获取全部用户的信息|

## 使用说明

启动器依赖`gunicorn`

使用时直接执行脚本即可, 脚本共三种命令

* 启动  $./api.sh start
* 停止  $./api.sh stop
* 重启  $./api.sh restart