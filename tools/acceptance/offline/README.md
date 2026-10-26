# 离线产物基础验收

使用 `manage.py start/check/stop/clean --version VERSION --batch NAME`。不带参数只输出帮助，支持 `--no-color`；clean 默认预览，`--execute` 才停止容器并删除安装目录。

完整说明见 [happyro-doc](../../../repos/happyro-doc/docs/development/offline-acceptance.md)。按版本与批次保存安装、数据、日志和证据；release 的清理不删除验收环境。本入口不构建镜像、不推送 Docker Hub。

- `environment.py`：安全解压、批次锁、配置隔离、包内部署工具调用、停止与清理。
- `checks.py`：包完整性、容器健康、HTTP、报告。
- `browser.mjs`：真实启动页、默认测试账号登录、罗安进图、正常鼠标移动及截图；不注入客户端代码，不覆盖专项游戏功能。

包内 `tools/deployment/manage.py` 通过显式 `--compose-override PATH` 接受隔离配置，正式部署默认行为不变。只有重新打包后的 ZIP 才包含此功能。源码单元测试不表示真实包验收通过。

真实试打包已验证 Linux arm64 隔离部署、HTTP、罗安进图及移动。网段分配忽略 Docker 无子网网络；浏览器以角色接口响应确认身份，按实际大小选择主画布，不依赖骑乘区域等无关界面文字。验收结果和截图保留在批次 evidence/，不把单元测试结果当作实机结果。
