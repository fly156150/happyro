# 盗贼 → 刺客 → 十字刺客 → 十字斩首者 → 暗影十字：实机转职流程

[流程索引与共用转生／四转步骤](../walkthrough.md) · [审计进度](../README.md) · [修复记录](../fixes.md)

本文随实机测试更新。未测试的阶段保留明确标记；材料准备、强化素质等测试措施不属于正常玩家转职要求。

| 阶段 | NPC 与位置 | 来源 | 状态 |
| --- | --- | --- | --- |
| 二转 | `Guildsman#asn` · `in_moc_16 19,33` | [脚本](../../../../repos/happyro-server/npc/jobs/2-1/assassin.txt) | 源码入口已定位，流程待实测 |
| 进阶二转 | `Assassin Cross#Valkyrie` · `valkyrie 44,58` | [脚本](../../../../repos/happyro-server/npc/jobs/2-1a/AssassinCross.txt) | 源码入口已定位，流程待实测 |
| 三转 | `Guild Member#3rdgc01` · `que_job01 75,96` | [脚本](../../../../repos/happyro-server/npc/re/jobs/3-1/guillotine_cross.txt) | 源码入口已定位，流程待实测 |

实测操作步骤、选项／材料、前置条件失败提示和结果：待按实际流程补充。转生、一转与四转使用上面的共用入口，但本线仍需逐阶段验证。


已实测本线一转：初心者 Base 10 / Job 10、学完基础技能后，找 `moc_prydb1 39,129`，依次选择「我想成为盗贼。」→「是。」→「是的。」完成面试；再找 `42,133` 公会成员办理仪式，原生转为盗贼（6、Job 1）。当前 Renewal 流程无需旧版蘑菇收集。[证据](../evidence/thief-npc.json)。等级和基础技能为测试准备，职业由 NPC 改变。
