# 诗人／舞娘职业线：实机转职流程

[流程索引与共用转生／四转步骤](../walkthrough.md) · [审计进度](../README.md) · [修复记录](../fixes.md)

本文随实机测试更新。未测试的阶段保留明确标记；材料准备、强化素质等测试措施不属于正常玩家转职要求。

## 弓箭手 → 诗人 → 搞笑艺人 → 宫廷乐师 → 天籁颂者

男性诗人分支，与舞娘分开记录。

| 阶段 | NPC 与位置 | 来源 | 状态 |
| --- | --- | --- | --- |
| 二转 | `Wandering Bard` · `comodo 226,123` | [脚本](../../../../repos/happyro-server/npc/jobs/2-2/bard.txt) | 源码入口已定位，流程待实测 |
| 进阶二转 | `Minstrel#Valkyrie` · `valkyrie 53,54` | [脚本](../../../../repos/happyro-server/npc/jobs/2-2a/Clown.txt) | 源码入口已定位，流程待实测 |
| 三转 | `Bard#job_min` · `alberta 196,133` | [脚本](../../../../repos/happyro-server/npc/re/jobs/3-2/minstrel.txt) | 源码入口已定位，流程待实测 |

实测操作步骤、选项／材料、前置条件失败提示和结果：待按实际流程补充。转生、一转与四转使用上面的共用入口，但本线仍需逐阶段验证。

## 弓箭手 → 舞娘 → 冷艳舞姬 → 漫游舞者 → 乐之舞灵

女性舞娘分支，与诗人分开记录。

| 阶段 | NPC 与位置 | 来源 | 状态 |
| --- | --- | --- | --- |
| 二转 | `Bor Robin#1` · `comodo 193,151` | [脚本](../../../../repos/happyro-server/npc/jobs/2-2/dancer.txt) | 源码入口已定位，流程待实测 |
| 进阶二转 | `Gypsy#Valkyrie` · `valkyrie 53,56` | [脚本](../../../../repos/happyro-server/npc/jobs/2-2a/Gypsy.txt) | 源码入口已定位，流程待实测 |
| 三转 | `Aspiring Wanderer, Soy` · `xmas 162,209` | [脚本](../../../../repos/happyro-server/npc/re/jobs/3-2/wanderer.txt) | 源码入口已定位，流程待实测 |

实测操作步骤、选项／材料、前置条件失败提示和结果：待按实际流程补充。转生、一转与四转使用上面的共用入口，但本线仍需逐阶段验证。
