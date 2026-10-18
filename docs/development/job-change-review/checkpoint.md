# 暂停断点（2026-10-18）

状态：用户明确要求暂停。四个测试浏览器服务及场景控制进程均已停止；没有后台验收继续执行。游戏 login / char / map 服务保持运行。暂停时尚未提交代码；用户随后授权本批断点文档及现有修改在六个仓库提交并推送。此授权不恢复验收，也不授权打包资源。

## 范围与完成状态

恢复须等待用户明确要求。只继续原生 NPC 转职及最终正常重登；冒险工具验收已被用户取消，旧证据保留但不再补测。等级、技能点、金币和材料可作为明确记录的测试准备，不能改任务变量或以直接改职业替代 NPC 转职。

完整原生职业线通过 3/12：巫师、大主教、骑士三线，均完成四转及最终重登。其余均未完整通过。每条线流程见 [walkthrough.md](walkthrough.md)，缺陷见 [fixes.md](fixes.md)。

## 角色断点

下表为停止浏览器前的实际状态；恢复后重新登录并核验，不能假定仍停留在相同对话页。暂停现场包含位置、背包、聊天及对话：[脱敏快照](evidence/pause-checkpoint-2026-10-18.json)。

| 控制端口／账号选择 | 角色／槽位 | 现场状态 | 下一步 |
| --- | --- | --- | --- |
| 9351，默认第一对男性 | JobDirectM／1 | 神射手 4012，`tur_dun01 93,165`；第一关 20/20，炸弹关通过；狼考试 5/20，原生判负送回 | 分析狼攻击调度及 CPU 延迟；通过教官正常重试，不能跳过前两关；之后完成游侠、风鹰和重登 |
| 9361，第一对女性 | JobDirectF／1 | 剑士 1，`prt_cas 110,156`；本线原生一转通过，十字军报名尚未完成 | 核对城堡内部传送点并步行抵达 `251,75`，继续十字军报名 |
| 9371，`--pair=2` 男性 | JobAudit2M／0 | 商人 5，`ein_in01 201,26`；铁匠报名、知识考试 100 分通过；已领取材料清单 | 准备并交付铁 1、绿色药草 1、动物外皮 2、环首刀 1；接着原生送货与最终考试 |
| 9381，`--pair=2 --female` | JobAudit2F／0 | 盗贼 6，`in_moc_16 19,152`；报名及凯面试通过；笔试 100 分通过 | 快照采集时仍在分数页，随后证据已记录对话关闭；恢复时核验任务实际阶段，再继续下一区域实战 |

第一对女性槽位 0 的 JobAuditF 已完成枢机主教，不要误当作十字军测试角色。第一对男性槽位 0 的 JobAuditM 为已完成的骑士／工具审计角色，不是当前游侠。

## 最近证据与未解决点

- 大主教完整试炼：[第一段](evidence/archbishop-trial-escort-fast.json)、[第二段和最终转职](evidence/archbishop-trial-finish.json)；枢机主教[四转](evidence/cardinal-fourth.json)、[重登](evidence/cardinal-relog.json)通过。
- 游侠第三轮：[考试阶段](evidence/ranger-practical-tests-third-attempt.json)。狼考试失败的 5/20 结果在暂停快照聊天中，不能把进入第三关记作通过。`ranger-line-complete.js`、`windhawk-fourth.js`、`windhawk-relog.js` 已准备但未通过执行。
- 铁匠：[报名](evidence/blacksmith-registration.json)、[知识考试](evidence/blacksmith-questions.json)、[材料要求](evidence/blacksmith-material-request.json)。尚未准备本次材料、未交付。
- 刺客：[一转](evidence/thief-npc.json)、[报名](evidence/assassin-registration.json)、[面试](evidence/assassin-interview.json)、[笔试](evidence/assassin-questions.json)。笔试证据为 10 题、100 分、对话关闭，不等同于刺客转职完成。
- 城堡 `prt_cas` 有原生 `nowarpto`，不能直接导航传送。已从 `prontera 156,357` 正门进入，再走右楼梯到 `110,156`；直接寻路至 `174,235` 不连通。恢复应核对 `npc/re/warps/cities/prontera.txt` 的楼梯、主厅、十字军房门路线，不修改地图限制。
- 地图服务状态可能先于客户端完成加载。测试工具已增加客户端 Playing／坐标就绪检查；同地图跨房间传送会结束当前步行段。不要把旧网格导致的寻路失败认定为产品缺陷。

## 修复状态

四项产品修复均已有相应实机证据：NPC 对话期间拒绝工具改职业／等级；保留任务怪物专用名称；修正大主教入场监控时序；修正游侠炸弹范围公告。最后一项已加载到本机地图服务，实测公告为周围 5 格、至少离开 6 格：[回归证据](evidence/ranger-blast-warning-after.json)。没有改变炸弹伤害、范围或考试时限。

本批交接修改分布：根仓库 `docs/development/job-change-review/`、`tools/job-change-audit/`、集中 changelog；server 的 `game_control.cpp`、`archbishop.txt`、`ranger.txt` 与 changelog；client 的 Entity / EntityName、相关测试与 changelog；admin 的 AdventureToolController、语言提示、相关测试与 changelog。恢复时先查看各仓库 `git status`，保留用户其他改动。

## 恢复方法与资源限制

1. 先读本文件、README 和进度记录，检查游戏服务及各仓库状态。
2. 按所需账号启动会话，启动本身只登录角色，不自动执行考试。四个旧 transient 服务已停止；若单元已被系统回收，使用 `systemd-run` 重新创建。工作目录为 `/vol2/1000/kugarocks/happyro`，入口为 `node tools/job-change-audit/session.mjs --run`。
3. 游侠加 `--slot=1 --port=9351`；十字军加 `--female --slot=1 --port=9361`；铁匠加 `--pair=2 --port=9371`；刺客加 `--pair=2 --female --port=9381`。
4. 会话 ready 后，在对应控制会话初始化 `globalThis.jobNpc=(await import('./dialogue.mjs')).dialogueDriver(game,snapshot)`，先读取实际角色、地图、职业和对话状态，再选择场景。不要直接重跑已完成的报名或把旧进程编号当作运行中任务。
5. 使用 `python3 tools/job-change-audit/control.py --run <场景文件> --port <端口>` 运行经核对的场景；需要调整路径时，先核对碰撞格与原生传送点。

本机是 N150、4 核。四路 headless Chromium 使用 SwiftShader 软件渲染，测得 CPU 99–100%、负载约 31、CPU PSI 约 90%，是明确瓶颈。不要默认重新启动四路活跃渲染；应先限制帧率、降低并发或迁移浏览器后实测。`render-budget.js` 的首次图形设置 UI 操作失败，**尚未成功降低帧率**，不能声称已优化。内存可用约 1.8 GiB、无内存 PSI 压力，当前主要是 CPU。

凭据只在忽略目录 `work/runtime/job-change-audit.json` 和 `job-change-audit-2.json`，不写入文档、不提交。`prepare.py --run --pair 2` 已执行，无需重复创建账号。新机器应采用其自身配置核对连接地址和凭据，不直接照搬本机运行态。

## macOS M5 续接与并发

用户确认另一台机器是 macOS M5，可以加大并发。恢复时优先在该机器运行浏览器；先单会话验证，再扩大到现有四个独立账号，依据 CPU、内存压力、WebGL 实际渲染器、操作延迟及考试计时逐步提高并发，不预设最终上限。当前工具只支持两对账号，超过四路需要先扩展账号隔离及端口配置，不能重复登录同一账号。共享考试场地仍须串行占用。

当前工具尚未适配 macOS：`session.mjs` 写死 `/usr/bin/chromium` 和本机 3338 入口，部分场景写死 Linux 工作区绝对路径；`systemd-run` 仅用于原 Linux 主机。下一位 agent 应先适配浏览器路径、项目根目录、服务地址和 macOS 进程管理，并实测硬件渲染是否生效；不能因为芯片型号就认定 GPU 加速已启用。不要照搬 SwiftShader 软件渲染参数。

六个 Git 仓库同步只迁移代码和文档，不迁移数据库、任务变量、测试账号、私密凭据及离线资源。如连接原游戏服务，应核对远程入口及相关端口；如在 Mac 独立部署，应先完成数据库和必要配置的受控迁移，再核验断点角色。没有原数据库时，不能声称已恢复这些角色的任务阶段。

## 资源包待办与续接入口

资源包仍停留在清单核对，用户要求“先不操作”，尚未打包。当前资源脚本包含 `inputs/runtime/kro-20211105/`、`work/game-data/items/kro-20211105/`、`work/game-data/monsters/kro-20211105/`。这三项是非 Git 运行资源，不构成整个项目的独立离线环境；还依赖同版本代码中的翻译覆盖、后台地图／NPC 图片和目录数据，以及运行依赖、配置与数据库。资源产物的新鲜度尚未全部核验。

下一位 agent 的可复制指令见 [continue-prompt.md](continue-prompt.md)。该文件只有在用户明确要求继续验收时执行；本次仅完成交接和 Git 同步。
