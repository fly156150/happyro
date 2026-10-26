# 发布工具

构建机上的发布实现，统一入口为 `release.py`。不带参数只显示帮助；版本只读 `deploy/docker/VERSION`。运行前执行[发布流程](../../docs/operations/docker-release.md)中的源码、资源与构建能力预检。

## 一键流程

公开用法见 [happyro-doc 构建离线包](../../repos/happyro-doc/docs/development/offline-package.md)。已完成真实双架构构建、打包和独立拆分测试；本机基础运行验收覆盖 Linux arm64，不表示 Docker Hub 已发布或另一架构运行已通过。

```bash
# 读取 deploy/docker/VERSION，准备、构建并组装离线 ZIP
python3 tools/release/release.py run
# 预检通过后删除该版本旧 ZIP 和中间产物，完整重建
python3 tools/release/release.py rebuild --version "$(cat deploy/docker/VERSION)"
# 默认只预览；加 --execute 清理中间产物，加 --include-package 同时清理 ZIP
python3 tools/release/release.py clean --version "$(cat deploy/docker/VERSION)"
```

`run` 遇到已有版本目录会拒绝执行。`run/rebuild` 的目标版本必须匹配 VERSION，不自动切换源码；`clean` 可指定其它已登记版本。输出位于 `artifacts/releases/<版本>/`，日志及状态位于 `work/releases/<版本>/`。清理保留日志和审计状态，不处理未登记输出、Docker 缓存或部署数据。重建会删除旧 ZIP，失败不恢复；运行中的同版本任务持锁时拒绝清理。中断后使用 `rebuild` 全量重建，不支持断点续跑。

## 拆分交付

```bash
python3 tools/release/release.py run --split
python3 tools/release/release.py rebuild --version "$(cat deploy/docker/VERSION)" --split
# 对已登记且未改变的完整 ZIP 拆分，不重建镜像：
python3 tools/release/release.py split --version "$(cat deploy/docker/VERSION)"
```

生成同目录的 `happyro-<版本>-runtimes.zip`、`happyro-<版本>-images.zip` 和 `happyro-<版本>-split.json`，保留完整 ZIP。两包均带外层 `happyro-<版本>-SPLIT-README.md` 合并安装说明；镜像包还包含原完整部署 README。逐项核对拆分后的合并内容与完整包一致，报告记录来源批次及 ZIP 摘要。输入必须是 run/rebuild 登记的完整 ZIP，已有拆分输出拒绝覆盖。

`clean` 默认保留完整包、拆分包及报告，`--include-package --execute` 一并删除；`rebuild` 自动删除全部旧交付产物，只有加 `--split` 才重新生成拆分包。暂存目录由版本锁保护，中断遗留可随 clean/rebuild 清理。

## 显式推送（默认关闭）

`run/rebuild` 默认不推送，`--split` 也不隐含推送。登录 Docker Hub 后，仅显式加 `--push` 才在完整包及可选拆分校验成功后发布版本标签、更新 latest 并核验远程摘要：

```bash
python3 tools/release/release.py run --split --push
python3 tools/release/release.py rebuild --version "$(cat deploy/docker/VERSION)" --push
```

先验收后推送可使用独立命令，不重复构建：

```bash
release_version=$(cat deploy/docker/VERSION)
python3 tools/release/release.py push \
  --images "artifacts/releases/${release_version}/images" \
  --bundle "artifacts/releases/${release_version}/bundle"
```

推送要求保留 OCI 和 bundle。自动推送的核验记录位于当前日志批次的 `dockerhub/`，独立推送默认写入 `work/dockerhub/<UTC 批次>/`。推送失败保留本地包，不回滚已经推送的远程标签；可修复原因后用独立 push 重试。所有推送都不替代运行验收。

## 分阶段流程

以下命令使用独立输出目录，不纳入上述自动清理：

```bash
python3 tools/release/release.py prepare
python3 tools/deployment/manage.py verify --directory artifacts/deployment/release --prepared
python3 tools/release/release.py build
python3 tools/release/release.py package
# 对最终包完成本机验收后，显式执行：
python3 tools/release/release.py push
```

每个分阶段子命令只运行对应阶段，不会隐式启动下一阶段。`prepare/build --output` 接受尚不存在的目录；`package/push --images --bundle` 接受同一批产物目录；`push --evidence` 可指定新的核验记录目录，默认使用 UTC 时间批次。支持 `--workspace` 和 `--no-color`。

| 模块 | 职责 |
| --- | --- |
| `release.py` | 参数与命令派发 |
| `split.py` | 流式拆分、双包安装说明及合并内容一致性校验 |
| `workflow.py` | 一键编排、前置检查、阶段日志和最终校验 |
| `lifecycle.py` | 版本目录登记、进程锁与受控清理 |
| `sources.py` | 版本及六个仓库 HEAD、dirty 状态与工作区源码指纹 |
| `package.py` | 准备资源、复制离线工具、生成 ZIP |
| `images.py` | 全量无缓存构建五类双架构 OCI、转换可导入镜像 |
| `publish.py` | 校验完整本地产物、推送版本及 latest、保存远程摘要 |

发布前完整校验五个 OCI 与离线目录。先推送并核对全部版本标签，再更新全部 latest；最后重新读取两个标签，与本地完整 index 逐字节比较，包含 amd64/arm64 子 manifest。失败立即停止，不生成成功记录，不自动回滚已推送标签。不同运行保留独立证据，不覆盖上一轮记录。

离线包只携带 deployment 下的运行文件，不携带 Git/Buildx/Skopeo 发布逻辑。一键流程默认只生成离线包，显式 `--push` 可追加推送，本机验收仍需单独执行；不能把打包成功当作验收通过。发布受管产物时，`push` 必须用 `--images` 和 `--bundle` 指定同版本目录。

打包后的隔离运行、罗安基础验收和测试环境清理使用 [独立验收入口](../acceptance/offline/README.md)。产物测试目录位于 work/releases/<版本>/acceptance/<批次>/，不被 release clean/rebuild 删除。

允许直接打包未提交代码。来源记录使用 `sources` 字段，包含 HEAD、dirty、源码内容指纹与文件数；任何构建阶段发现来源变化均拒绝混批。不自动提交、暂存或复制源码仓库。
