# 商人 → 铁匠 → 神工匠 → 机甲神匠 → 机甲大师：实机转职流程

[流程索引与共用转生／四转步骤](../walkthrough.md) · [审计进度](../README.md) · [修复记录](../fixes.md)

本文随实机测试更新。未测试的阶段保留明确标记；材料准备、强化素质等测试措施不属于正常玩家转职要求。

| 阶段 | NPC 与位置 | 来源 | 状态 |
| --- | --- | --- | --- |
| 二转 | `Guildsman#BLS` · `ein_in01 18,28` | [脚本](../../../../repos/happyro-server/npc/jobs/2-1/blacksmith.txt) | 源码入口已定位，流程待实测 |
| 进阶二转 | `MasterSmith#Valkyrie` · `valkyrie 44,50` | [脚本](../../../../repos/happyro-server/npc/jobs/2-1a/WhiteSmith.txt) | 源码入口已定位，流程待实测 |
| 三转 | `Chainheart` · `yuno 129,156` | [脚本](../../../../repos/happyro-server/npc/re/jobs/3-1/mechanic.txt) | 源码入口已定位，流程待实测 |

实测操作步骤、选项／材料、前置条件失败提示和结果：待按实际流程补充。转生、一转与四转使用上面的共用入口，但本线仍需逐阶段验证。


已实测本线一转：初心者 Base 10 / Job 10、学完基础技能后，找 `alberta_in 53,43` 公会职员曼苏，选择「我想成为商人。」并完成对话，原生转为商人（5、Job 1）。当前 Renewal 流程无需旧版送货考试。[证据](../evidence/merchant-npc.json)。等级和基础技能为测试准备，职业由 NPC 改变。
