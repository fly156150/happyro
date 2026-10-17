# 职业线技能第二轮审查

本轮重新审查当前代码，按职业线完成一至四转、继承技能及派生入口，再提交该线的修复与记录。第一轮依据见 [主要职业线技能审查](skill-review.md)。代码审查和定向回归不等同于逐技能实机战斗验收。

## 进度

| 顺序 | 职业线 | 本轮状态 |
| --- | --- | --- |
| 1 | 弓箭手／猎人／神射手／游侠／风鹰 | 68 个技能代码复查完成，回归与编译通过 |
| 2 | 魔法师／巫师／大法师／至高法师 | 待复查 |
| 3 | 服事／牧师／大主教／枢机主教 | 待复查 |
| 4 | 剑士／十字军／皇家卫士／帝国卫士 | 待复查 |
| 5 | 盗贼／刺客／十字斩首者／暗影十字 | 待复查 |
| 6 | 商人／铁匠／机甲神匠／机甲大师 | 待复查 |
| 7 | 魔法师／贤者／妖术师／元素大师 | 待复查 |
| 8 | 商人／炼金术师／基因学者／生物学者 | 待复查 |
| 9 | 服事／武僧／修罗／审判官 | 待复查 |
| 10 | 盗贼／流氓／魅影追踪者／深渊追踪者 | 待复查 |
| 11 | 弓箭手／诗人、舞娘及对应三、四转 | 待复查 |
| 12 | 待确认是否为此前单独审查的骑士线 | 待复查 |

## 猎人线工作记录

### 已核对的服务端路径

- 随行状态切换：战狼召唤、骑乘、冲刺及猎鹰召唤；施放前状态要求和攻击时路径检查。
- 主动攻击：箭矢、猎鹰、战狼、三转弓箭与四转弓箭的独立实现；恐惧微风连射与额外箭矢扣除；普通攻击自动触发随行攻击。
- 陷阱：独立施放类、地面单位触发、范围攻击、使用后变形、到期回收及拆除返还路径；四转陷阱的被动延时与 AP 获取。
- 增益与减益：专注、风之步、伪装、全力推进、电击陷阱的状态初始化与定时路径；风之符分别在普通攻击与技能攻击中的 AP 恢复入口。`status_heal` 的五参数调用中第四项是 AP，不能误判为无效回复。

已补齐 68 个技能的数据库、工厂、独立实现和共享路径复查，以及客户端目标选择、施放封包、动作、效果、地面单位与随行动作路由。被动技能继续核对属性、射程、精通伤害和技能前置条件，未将无主动特效视为缺陷。

### 当前验证

- 服务端 `map-server` 增量编译通过，未重启在线服务。
- 客户端随行动作、话匣子、技能目标、技能使用和四转映射共 5 个测试文件、25 项测试通过。这里只覆盖对应契约，不作为 68 个技能全部完成审查的证明。
- 重新从当前技能树和数据库提取 68 个技能，与客户端常量及生成信息逐项比较，ID、名称键、等级上限均一致。
- 31 个风鹰原生 STR 及 338 个依赖贴图通过 Gateway 读取与结构验证。客户端本轮没有修改，不重复构建相同产物。
- 本轮未做逐技能实机战斗或人工听音；荒野疾行未知系数的上游 TODO 保持不变，未凭猜测调整平衡数值。

### 已复现并修复：电击陷阱 SP 百分比溢出

`status.cpp` 的电击陷阱定时扣除先将最大 SP 与等级百分比做 32 位乘法，再除以 100。以 5 级技能和 200,000,000 最大 SP 为例，旧代码得到 7,050,327，正确结果是 50,000,000。该值高于当前默认最大 SP 配置，但在配置允许的最大值范围内，属于高数值边界问题。

改为先提升至 `int64` 再计算，保持原有比例、整数舍入和持续时间。没有改动 SP 不足时 `status_charge` 的既有行为。

新增服务端 `tests/hunter-status.test.mjs`，提取实际定时器分支编译执行，覆盖 1–5 级、零值、小值、当前默认上限、高 SP、32 位边界以及到期后不再扣除。旧实现断言失败，修复后通过；启用未定义行为检测。

运行方式（在服务端仓库）：

```sh
node tests/hunter-status.test.mjs ../../work/skill-review/hunter-status-test --no-color
```

### 本轮逐技能覆盖

下表记录本轮复查入口；共享施放、目标验证、资源要求及客户端路由同时覆盖对应主动技能。

| ID | 技能 | 服务端复查入口 |
| --- | --- | --- |
| 43 | Owl's Eye `AC_OWL` | status／battle 被动与前置条件 |
| 44 | Vulture's Eye `AC_VULTURE` | status／battle 被动与前置条件 |
| 45 | Improve Concentration `AC_CONCENTRATION` | SkillConcentration |
| 46 | Double Strafe `AC_DOUBLE` | SkillDoubleStrafe |
| 47 | Arrow Shower `AC_SHOWER` | SkillArrowShower |
| 115 | 滑动陷阱 `HT_SKIDTRAP` | SkillSkidTrap；地面单位 Skidtrap |
| 116 | 地雷 `HT_LANDMINE` | SkillLandMine；地面单位 Landmine |
| 117 | 定身陷阱 `HT_ANKLESNARE` | SkillAnkleSnare；地面单位 Anklesnare |
| 118 | 冲击波陷阱 `HT_SHOCKWAVE` | SkillShockwaveTrap；地面单位 Shockwave |
| 119 | 睡魔 `HT_SANDMAN` | SkillSandman；地面单位 Sandman |
| 120 | 闪光陷阱 `HT_FLASHER` | SkillFlasher；地面单位 Flasher |
| 121 | 冰冻陷阱 `HT_FREEZINGTRAP` | SkillFreezingTrap；地面单位 Freezingtrap |
| 122 | 爆破地雷 `HT_BLASTMINE` | SkillBlastMine；地面单位 Blastmine |
| 123 | 克雷莫陷阱 `HT_CLAYMORETRAP` | SkillClaymoreTrap；地面单位 Claymoretrap |
| 124 | 拆除陷阱 `HT_REMOVETRAP` | SkillRemoveTrap |
| 125 | 话匣子 `HT_TALKIEBOX` | SkillTalkieBox；地面单位 Talkiebox |
| 126 | 兽物驱除 `HT_BEASTBANE` | status／battle 被动与前置条件 |
| 127 | 猎鹰精通 `HT_FALCON` | status／battle 被动与前置条件 |
| 128 | 钢铁之鸦 `HT_STEELCROW` | status／battle 被动与前置条件 |
| 129 | 闪电冲击 `HT_BLITZBEAT` | SkillBlitzBeat |
| 130 | 探测 `HT_DETECTING` | SkillDetect |
| 131 | 弹簧陷阱 `HT_SPRINGTRAP` | SkillSpringTrap |
| 147 | 制作箭矢 `AC_MAKINGARROW` | SkillMakingArrow |
| 148 | 箭矢击退 `AC_CHARGEARROW` | SkillChargeArrow |
| 380 | 鹰眼 `SN_SIGHT` | StatusSkillImpl |
| 381 | 猎鹰突击 `SN_FALCONASSAULT` | SkillFalconAssault |
| 382 | 集中射击 `SN_SHARPSHOOTING` | SkillFocusedArrowStrike |
| 383 | 风之步 `SN_WINDWALK` | SkillWindWalker |
| 499 | Beast Strafing `HT_POWER` | SkillBeastStrafing |
| 1009 | 幻影之箭 `HT_PHANTASMIC` | SkillPhantasmicArrow |
| 2233 | Arrow Storm `RA_ARROWSTORM` | SkillArrowStorm |
| 2234 | Fear Breeze `RA_FEARBREEZE` | SkillFearBreeze |
| 2235 | Ranger Main `RA_RANGERMAIN` | status／battle 被动与前置条件 |
| 2236 | Aimed Bolt `RA_AIMEDBOLT` | SkillAimedBolt |
| 2237 | Detonator `RA_DETONATOR` | SkillDetonator |
| 2238 | Electric Shocker `RA_ELECTRICSHOCKER` | SkillElectricShocker；地面单位 Electricshocker；修复定时 SP 计算 |
| 2239 | Cluster Bomb `RA_CLUSTERBOMB` | SkillClusterBomb；地面单位 Clusterbomb |
| 2240 | Warg Mastery `RA_WUGMASTERY` | SkillWargMastery |
| 2241 | Warg Rider `RA_WUGRIDER` | SkillWargRider |
| 2242 | Warg Dash `RA_WUGDASH` | SkillWargDash |
| 2243 | Warg Strike `RA_WUGSTRIKE` | SkillWargStrike |
| 2244 | Warg Bite `RA_WUGBITE` | SkillWargBite |
| 2245 | Tooth of Warg `RA_TOOTHOFWUG` | status／battle 被动与前置条件 |
| 2246 | Sensitive Keen `RA_SENSITIVEKEEN` | SkillSensitiveKeen |
| 2247 | Camouflage `RA_CAMOUFLAGE` | SkillCamouflage |
| 2248 | Research Trap `RA_RESEARCHTRAP` | status／battle 被动与前置条件 |
| 2249 | Magenta Trap `RA_MAGENTATRAP` | SkillMagentaTrap；地面单位 Magentatrap |
| 2250 | 钴陷阱 `RA_COBALTTRAP` | SkillCobaltTrap；地面单位 Cobalttrap |
| 2251 | 玉米陷阱 `RA_MAIZETRAP` | SkillMaizeTrap；地面单位 Maizetrap |
| 2252 | 翠绿陷阱 `RA_VERDURETRAP` | SkillVerdureTrap；地面单位 Verduretrap |
| 2253 | 火焰陷阱 `RA_FIRINGTRAP` | SkillFiringTrap；地面单位 Firingtrap |
| 2254 | 冰封陷阱 `RA_ICEBOUNDTRAP` | SkillIceboundTrap；地面单位 Iceboundtrap |
| 5002 | 无限 `RA_UNLIMIT` | StatusSkillImpl |
| 5014 | 全力推进 `ALL_FULL_THROTTLE` | 通用状态 Full_Throttle |
| 5323 | 高级陷阱 `WH_ADVANCED_TRAP` | status／battle 被动与前置条件 |
| 5324 | 风之符 `WH_WIND_SIGN` | StatusSkillImpl |
| 5325 | 亲近自然 `WH_NATUREFRIENDLY` | status／battle 被动与前置条件 |
| 5326 | 猎鹰冲锋 `WH_HAWKRUSH` | SkillHawkRush |
| 5327 | 猎鹰精通 `WH_HAWK_M` | SkillHawkMastery |
| 5328 | 灾厄狂风 `WH_CALAMITYGALE` | StatusSkillImpl |
| 5329 | 猎鹰回旋镖 `WH_HAWKBOOMERANG` | SkillHawkBoomerang |
| 5330 | 狂风暴雨 `WH_GALESTORM` | SkillGaleStorm |
| 5331 | 深度失明陷阱 `WH_DEEPBLINDTRAP` | SkillDeepBlindTrap；地面单位 Deepblindtrap |
| 5332 | 坚固陷阱 `WH_SOLIDTRAP` | SkillSolidTrap；地面单位 Solidtrap |
| 5333 | 迅捷陷阱 `WH_SWIFTTRAP` | SkillSwiftTrap；地面单位 Swifttrap |
| 5334 | 成长箭矢 `WH_CRESCIVE_BOLT` | SkillCresciveBolt |
| 5335 | 火焰陷阱 `WH_FLAMETRAP` | SkillFlameTrap；地面单位 Flametrap |
| 6520 | Wild Walk `WH_WILD_WALK` | SkillWildWalk |
