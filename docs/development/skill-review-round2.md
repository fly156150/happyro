# 职业线技能第二轮审查

本轮重新审查当前代码，按职业线完成一至四转、继承技能及派生入口，再提交该线的修复与记录。第一轮依据见 [主要职业线技能审查](skill-review.md)。代码审查和定向回归不等同于逐技能实机战斗验收。

## 进度

| 顺序 | 职业线 | 本轮状态 |
| --- | --- | --- |
| 1 | 弓箭手／猎人／神射手／游侠／风鹰 | 68 个技能代码复查完成，回归与编译通过 |
| 2 | 魔法师／巫师／大法师／至高法师 | 78 个技能及派生入口复查完成，修复与验证通过 |
| 3 | 服事／牧师／大主教／枢机主教 | 77 个技能及派生入口复查完成，修复与验证通过 |
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

## 巫师线复查结果

从当前 Mage、Wizard、High_Wizard、Warlock、Warlock_T、Arch_Mage 技能树重新提取 78 个去重技能，逐项检查定义、工厂、主动实现或共享被动；另外覆盖读取魔法书、四种元素球攻击、四属性漩涡与四转派生攻击。客户端检查技能与地面单位映射、封包播放阶段、白色监狱身体状态和球体快照更新。

### 已复现并修复：四属性漩涡命中序号

- 原实现用元素球槽位相对位置作为命中序号。四球位于 1–4 槽时得到 1–4，而定时器将序号大于等于 3 视为末段，导致末段异常状态尝试两次。
- 只检查第 5 槽是否存在就删除第 1 槽；如果中间有球先到期，剩余四球可能因此只释放三次。
- 六级以上范围版的四种派生攻击固定传入序号 0，导致末段异常状态不触发。

修复为先统计球数，只有五球齐全才舍弃第 1 槽；实际攻击连续编号 0–3，并传入范围版派生定时器。保留元素顺序和 200 毫秒间隔。

`tests/tetra-sequence.test.mjs` 提取实际主技能与四种派生方法编译执行，覆盖四球的全部空槽位置、五球、1／5／6／10 级、单体／双目标范围和怪物施放；旧代码失败，修复后通过。既有火属性封包回归也通过。这些定向测试验证具体缺陷，整条线的代码复查覆盖见下表。

### 已复现并修复：魔法半径覆盖施法等级

共享固定咏唱计算把 `pc_checkskill(WL_RADIUS)` 赋给当前施法等级，且在技能范围检查之前就执行赋值。未学习半径的玩家也会将当前等级置零，后续状态修正读取错误等级。改为独立的 `radius_lv`，仅在巫师技能范围内读取；半径原来的减免公式保持不变。

`tests/wizard-cast.test.mjs` 提取生产固定咏唱分支，覆盖玩家／非玩家、未学／各级半径、范围内外技能和 1–10 级施法。旧代码失败，修复后通过，施法等级保持不变。

### 验证与限制

- 六组服务端回归通过：四属性漩涡命中顺序、火属性封包、魔法半径、吸取生命、能量外套、魔法书容量与失败保留；执行实际代码并启用未定义行为检测。
- 服务端 `map-server` 编译通过，未重启在线服务。
- 客户端 9 个测试文件、46 项测试通过，覆盖球体、身体状态、效果路由、四转地面效果和共用施放入口；测试环境有不支持 canvas 的提示，不将其视为实际 WebGL 渲染验收。
- 78 个技能的 ID、名称键和等级上限与客户端一致；55 个 STR 与 642 个贴图／音频等依赖通过 Gateway 读取检查。
- 本轮没有客户端代码修改，没有重复构建相同 PWA。没有逐技能实机战斗、人工听音或官方逐帧比对；石化扩散抵抗等未定上游平衡项保持原状。

### 本轮逐技能覆盖

| ID | 技能 | 服务端复查入口 |
| --- | --- | --- |
| 9 | 增加SP恢复 `MG_SRECOVERY` | 共享属性／被动／资源前置 |
| 10 | 火狩 `MG_SIGHT` | SkillSight |
| 11 | 圣灵召唤 `MG_NAPALMBEAT` | SkillNapalmBeat |
| 12 | 暗之障壁 `MG_SAFETYWALL` | SkillSafetyWall；地面单位 Safetywall |
| 13 | 灵魂打击 `MG_SOULSTRIKE` | SkillSoulStrike |
| 14 | 冰箭术 `MG_COLDBOLT` | SkillColdBolt |
| 15 | 冰冻术 `MG_FROSTDIVER` | SkillFrostDiver |
| 16 | 石化术 `MG_STONECURSE` | SkillStoneCurse |
| 17 | 火球术 `MG_FIREBALL` | SkillFireBall |
| 18 | 火墙术 `MG_FIREWALL` | SkillFireWall；地面单位 Firewall |
| 19 | 火箭术 `MG_FIREBOLT` | SkillFireBolt |
| 20 | 雷击术 `MG_LIGHTNINGBOLT` | SkillLightningBolt |
| 21 | 雷暴术 `MG_THUNDERSTORM` | SkillThunderStorm；地面单位 Dummyskill |
| 80 | 火柱术 `WZ_FIREPILLAR` | SkillFirePillar；地面单位 Firepillar_Waiting |
| 81 | 火狩 `WZ_SIGHTRASHER` | SkillSightRasher |
| 83 | 陨石术 `WZ_METEOR` | SkillMeteorStorm；地面单位 Dummyskill |
| 84 | 雷鸣术 `WZ_JUPITEL` | SkillJupitelThunder |
| 85 | 雷鸣风暴 `WZ_VERMILION` | SkillLordOfVermilion；地面单位 Dummyskill |
| 86 | 水球术 `WZ_WATERBALL` | SkillWaterBall；地面单位 Dummyskill |
| 87 | 冰墙术 `WZ_ICEWALL` | SkillIceWall；地面单位 Icewall |
| 88 | Frost Nova `WZ_FROSTNOVA` | SkillFrostNova |
| 89 | Storm Gust `WZ_STORMGUST` | SkillStormGust；地面单位 Dummyskill |
| 90 | Earth Spike `WZ_EARTHSPIKE` | SkillEarthSpike |
| 91 | Heaven's Drive `WZ_HEAVENDRIVE` | SkillHeavensDrive；地面单位 Dummyskill |
| 92 | Quagmire `WZ_QUAGMIRE` | SkillQuagmire；地面单位 Quagmire |
| 93 | Sense `WZ_ESTIMATION` | SkillSense |
| 157 | Energy Coat `MG_ENERGYCOAT` | SkillEnergyCoat |
| 364 | Soul Drain `HW_SOULDRAIN` | 共享属性／被动／资源前置 |
| 365 | Stave Crasher `HW_MAGICCRASHER` | WeaponSkillImpl |
| 366 | Mystical Amplification `HW_MAGICPOWER` | StatusSkillImpl |
| 400 | 凝固汽油火神炮 `HW_NAPALMVULCAN` | SkillNapalmVulcan |
| 483 | 岩碎术 `HW_GANBANTEIN` | SkillGanbantein |
| 484 | 重力场 `HW_GRAVITATION` | SkillGravitationField；地面单位 Gravitation |
| 1006 | 视线爆破 `WZ_SIGHTBLASTER` | SkillSightBlaster |
| 2201 | 白色监禁 `WL_WHITEIMPRISON` | SkillWhiteImprison |
| 2202 | 灵魂扩张 `WL_SOULEXPANSION` | SkillSoulExpansion |
| 2203 | 冰霜迷雾 `WL_FROSTMISTY` | SkillFrostyMisty |
| 2204 | 杰克霜冻 `WL_JACKFROST` | SkillJackFrost |
| 2205 | Marsh of Abyss `WL_MARSHOFABYSS` | StatusSkillImpl |
| 2206 | Recognized Spell `WL_RECOGNIZEDSPELL` | StatusSkillImpl |
| 2207 | Sienna Execrate `WL_SIENNAEXECRATE` | SkillSiennaExecrate |
| 2208 | Radius `WL_RADIUS` | 共享属性／被动／资源前置；修复覆盖施法等级 |
| 2209 | Stasis `WL_STASIS` | SkillStasis |
| 2210 | Drain Life `WL_DRAINLIFE` | SkillDrainLife |
| 2211 | Crimson Rock `WL_CRIMSONROCK` | SkillCrimsonRock |
| 2212 | Hell Inferno `WL_HELLINFERNO` | SkillHellInferno |
| 2213 | Comet `WL_COMET` | SkillComet；地面单位 Dummyskill |
| 2214 | Chain Lightning `WL_CHAINLIGHTNING` | SkillChainLightning |
| 2216 | Earth Strain `WL_EARTHSTRAIN` | SkillEarthStrain；地面单位 Earthstrain |
| 2217 | Tetra Vortex `WL_TETRAVORTEX` | SkillTetraVortex；修复命中序号与球数判定 |
| 2222 | 召唤火球 `WL_SUMMONFB` | SkillSummonFireBall |
| 2223 | 召唤雷球 `WL_SUMMONBL` | SkillSummonLightningBall |
| 2224 | 召唤水球 `WL_SUMMONWB` | SkillSummonWaterBall |
| 2229 | 召唤石块 `WL_SUMMONSTONE` | SkillSummonStone |
| 2230 | 释放 `WL_RELEASE` | SkillRelease |
| 2231 | 阅读魔法书 `WL_READING_SB` | 共享属性／被动／资源前置 |
| 2232 | 冻结魔法 `WL_FREEZE_SP` | 共享属性／被动／资源前置 |
| 5012 | 强力念力 `WL_TELEKINESIS_INTENSE` | StatusSkillImpl |
| 5014 | 全力推进 `ALL_FULL_THROTTLE` | StatusSkillImpl |
| 5214 | 致命投影 `AG_DEADLY_PROJECTION` | SkillDeadlyProjection |
| 5215 | 毁灭飓风 `AG_DESTRUCTIVE_HURRICANE` | SkillDestructiveHurricane |
| 5216 | 水晶之雨 `AG_RAIN_OF_CRYSTAL` | SkillRainOfCrystal；地面单位 Rain_Of_Crystal |
| 5217 | 神秘幻象 `AG_MYSTERY_ILLUSION` | SkillMysteryIllusion；地面单位 Mystery_Illusion |
| 5218 | 暴烈地震 `AG_VIOLENT_QUAKE` | SkillViolentQuake；地面单位 Violent_Quake |
| 5220 | 灵魂火神击 `AG_SOUL_VC_STRIKE` | SkillSoulVulcanStrike |
| 5221 | 地层震颤 `AG_STRANTUM_TREMOR` | SkillStrantumTremor；地面单位 Strantum_Tremor |
| 5222 | 全花绽放 `AG_ALL_BLOOM` | SkillAllBloom；地面单位 All_Bloom |
| 5225 | Crystal Impact `AG_CRYSTAL_IMPACT` | SkillCrystalImpact |
| 5227 | Tornado Storm `AG_TORNADO_STORM` | SkillTornadoStorm；地面单位 Tornado_Storm |
| 5228 | Two Hand Staff Mastery `AG_TWOHANDSTAFF` | 共享属性／被动／资源前置 |
| 5229 | Floral Flare Road `AG_FLORAL_FLARE_ROAD` | SkillFloralFlareRoad；地面单位 Floral_Flare_Road |
| 5230 | Astral Strike `AG_ASTRAL_STRIKE` | SkillAstralStrike；地面单位 Astral_Strike |
| 5232 | Climax `AG_CLIMAX` | StatusSkillImpl |
| 5233 | Rock Down `AG_ROCK_DOWN` | SkillRockDown |
| 5234 | Storm Cannon `AG_STORM_CANNON` | SkillStormCannon |
| 5235 | Crimson Arrow `AG_CRIMSON_ARROW` | SkillCrimsonArrow |
| 5237 | Frozen Slash `AG_FROZEN_SLASH` | SkillFrozenSlash |
| 6516 | Energy Conversion `AG_ENERGY_CONVERSION` | SkillEnergyConversion |

## 牧师线复查结果

重新核对 Acolyte、Priest、High_Priest、Arch_Bishop、Arch_Bishop_T、Cardinal 的 77 个去重技能，覆盖独立实现、通用状态、被动属性、治疗与复活、协助者条件、地面单位、双重圣光和 Arbitrium 派生入口。客户端同时复查技能选择、传送菜单、受益者特效、状态图标及四转地面效果路径。

### 已复现并修复：传送之阵丢失本次等级

选点菜单将 `menuskill_val` 用于保存地面坐标，但没有保存本次技能等级；确认选点时又使用已学习的最高等级创建传送门，并将坐标误作等级查询最大数量。已学四级、选用一级时，生成的门仍按四级处理。

将本次等级保存到现有 `menuskill_val2`，确认时用该等级检查可选目的地、数量、需求和创建技能单位，并重新确认当前仍有对应技能／道具等级。成功、取消及失败统一清除三个菜单字段。未修改封包长度或客户端协议。

`tests/warp-menu.test.mjs` 执行生产选点完成函数及菜单保存代码，覆盖 1–4 级、越级目的地、窗口打开后技能重置、死亡／禁施法／需求不足、取消、道具传送阵和瞬间移动。旧代码失败，修复后通过。

### 已复现并修复：霸邪护盾容量溢出

霸邪之阵和群体霸邪在计算最大 HP 百分比时先做 32 位乘法。例如最大 HP 为 200,000,000、10 级时，原基础容量只有 17,050,327，正确值应为 60,000,000。改用 `int64` 中间值，保留比例、人数增量和可抵挡次数。

`tests/priest-shield.test.mjs` 提取实际状态初始化分支执行，覆盖 1–10 级、无队伍及 1／2／12 人、普通 HP、首次回绕附近、20 亿和无符号 32 位上界。旧代码失败，修复后通过；启用未定义行为检测。

### 验证与限制

- 服务端四组回归通过：传送选点、两种霸邪护盾、治疗／反射／经验／复活、圣树多人周期。前一轮修复的实时协助者 SP、净化成功率、治疗百分比和复活失败计数继续通过。
- `map-server` 编译通过，未重启在线服务。
- 客户端 6 个测试文件、30 项测试通过，覆盖技能使用／目标、牧师效果路由与四转动作／效果／地面单位。
- 77 个技能的 ID、名称键和等级上限与客户端逐项一致；31 个 STR、250 个依赖经 Gateway 读取检查无缺失。
- 本轮没有客户端修改，不重复构建相同 PWA。未逐技能实机战斗或人工听音，不将代码复查等同于官方数值与动画完全一致。
- Dilectio 的范围中心和治疗来源仍沿用受益者；Mediale 仍由受益者的状态定时器驱动。已追踪到实际计算入口，但官方治疗来源／公式证据不足，不据此猜测修改。Silentium 等级和部分四转倍率的上游 TODO 也保持原状。
- 传送目的地 vector 前面的空字符串会被当前版本封包构造跳过，并非空菜单缺陷；Renewal 圣殿使用增益状态，不当作旧版地面领域。

### 本轮逐技能覆盖

| ID | 技能 | 服务端复查入口 |
| --- | --- | --- |
| 9 | 增加SP恢复 `MG_SRECOVERY` | status／battle／skill 共享被动与前置条件 |
| 12 | 暗之障壁 `MG_SAFETYWALL` | SkillSafetyWall；地面单位 Safetywall |
| 22 | 天使之护 `AL_DP` | status／battle／skill 共享被动与前置条件 |
| 23 | 恶魔克星 `AL_DEMONBANE` | status／battle／skill 共享被动与前置条件 |
| 24 | 光猎 `AL_RUWACH` | SkillRuwach |
| 25 | 光之障壁 `AL_PNEUMA` | SkillPneuma；地面单位 Pneuma |
| 26 | 瞬间移动 `AL_TELEPORT` | SkillTeleport |
| 27 | 传送之阵 `AL_WARP` | SkillWarpPortal；地面单位 Warp_Active；修复选点等级保存与校验 |
| 28 | 治愈术 `AL_HEAL` | SkillHeal |
| 29 | 敏捷提升 `AL_INCAGI` | SkillIncreaseAgi |
| 30 | 敏捷下降 `AL_DECAGI` | SkillDecreaseAgi |
| 31 | Aqua Benedicta `AL_HOLYWATER` | SkillHolyWater |
| 32 | Signum Crucis `AL_CRUCIS` | SkillCrucis |
| 33 | Angelus `AL_ANGELUS` | SkillAngelus |
| 34 | Blessing `AL_BLESSING` | SkillBlessing |
| 35 | Cure `AL_CURE` | SkillCure |
| 54 | 复活术 `ALL_RESURRECTION` | SkillResurrection |
| 65 | 钝器修炼 `PR_MACEMASTERY` | status／battle／skill 共享被动与前置条件 |
| 66 | 牺牲祈福 `PR_IMPOSITIO` | SkillImpositioManus |
| 67 | 牺牲祈福 `PR_SUFFRAGIUM` | SkillSuffragium |
| 68 | 圣水洗礼 `PR_ASPERSIO` | SkillAspersio |
| 69 | 圣体降福 `PR_BENEDICTIO` | SkillBenedictioSanctissimiSacramenti |
| 70 | 光耀之堂 `PR_SANCTUARY` | SkillSanctuary；地面单位 Sanctuary |
| 71 | 缓慢中毒 `PR_SLOWPOISON` | StatusSkillImpl |
| 72 | 状态恢复 `PR_STRECOVERY` | SkillStatusRecovery |
| 73 | 凯里艾勒松 `PR_KYRIE` | SkillKyrieEleison；修复共享护盾容量溢出 |
| 74 | 赞美诗 `PR_MAGNIFICAT` | SkillMagnificat |
| 75 | 荣耀 `PR_GLORIA` | SkillGloria |
| 76 | 神圣法典 `PR_LEXDIVINA` | SkillLexDivina |
| 77 | 退散不死 `PR_TURNUNDEAD` | SkillTurnUndead |
| 78 | 永恒法典 `PR_LEXAETERNA` | StatusSkillImpl |
| 79 | 大驱魔术 `PR_MAGNUS` | SkillMagnusExorcismus；地面单位 Magnus |
| 156 | Holy Light `AL_HOLYLIGHT` | SkillHolyLight |
| 361 | Assumptio `HP_ASSUMPTIO` | SkillAssumptio |
| 362 | Basilica `HP_BASILICA` | SkillBasilica |
| 363 | Meditatio `HP_MEDITATIO` | status／battle／skill 共享被动与前置条件 |
| 481 | 魔力充能 `HP_MANARECHARGE` | status／battle／skill 共享被动与前置条件 |
| 1014 | 牺牲祈福 `PR_REDEMPTIO` | SkillRedemptio |
| 2038 | 朱迪克斯 `AB_JUDEX` | SkillJudex |
| 2039 | 安琪拉 `AB_ANCILLA` | SkillAncilla |
| 2040 | 阿多拉穆斯 `AB_ADORAMUS` | SkillAdoramus |
| 2041 | 克莱门提亚 `AB_CLEMENTIA` | SkillCrementia |
| 2042 | 坎托·坎迪杜斯 `AB_CANTO` | SkillCantoCandidus |
| 2043 | 群体治愈 `AB_CHEAL` | SkillColuceoHeal |
| 2044 | 圣灵降临 `AB_EPICLESIS` | SkillEpiclesis；地面单位 Epiclesis |
| 2045 | 祷告 `AB_PRAEFATIO` | SkillPraefatio；修复共享护盾容量溢出 |
| 2046 | 祈祷 `AB_ORATIO` | SkillOratio |
| 2047 | 羔羊赞歌 `AB_LAUDAAGNUS` | SkillLaudaAgnus |
| 2048 | 枝条赞歌 `AB_LAUDARAMUS` | SkillLaudaRamus |
| 2050 | 新生 `AB_RENOVATIO` | SkillRenovatio |
| 2051 | 高级治愈 `AB_HIGHNESSHEAL` | SkillHighnessHeal |
| 2052 | 清除 `AB_CLEARANCE` | SkillClearance |
| 2053 | 赎罪 `AB_EXPIATIO` | StatusSkillImpl |
| 2054 | 双重光 `AB_DUPLELIGHT` | StatusSkillImpl；MELEE／MAGIC 派生与普攻触发 |
| 2057 | Silentium `AB_SILENTIUM` | SkillSilentium |
| 2515 | Secrament `AB_SECRAMENT` | StatusSkillImpl |
| 5011 | 奉献礼 `AB_OFFERTORIUM` | StatusSkillImpl |
| 5014 | 全力推进 `ALL_FULL_THROTTLE` | StatusSkillImpl |
| 5072 | 责骂 `AB_VITUPERATUM` | SkillVituperatum |
| 5073 | 契约 `AB_CONVENIO` | SkillConvenio |
| 5268 | 修复 `CD_REPARATIO` | SkillReparatio |
| 5269 | 中级祷言 `CD_MEDIALE_VOTUM` | SkillMedialeVotum |
| 5270 | 钝器书精通 `CD_MACE_BOOK_M` | status／battle／skill 共享被动与前置条件 |
| 5271 | 锐利生命 `CD_ARGUTUS_VITA` | StatusSkillImpl |
| 5272 | 锐利武器 `CD_ARGUTUS_TELUM` | StatusSkillImpl |
| 5273 | 裁决 `CD_ARBITRIUM` | SkillArbitrium；ATK 派生 |
| 5275 | 临在之锋 `CD_PRESENS_ACIES` | StatusSkillImpl |
| 5276 | 忠诚之魂 `CD_FIDUS_ANIMUS` | status／battle／skill 共享被动与前置条件 |
| 5277 | 释放 `CD_EFFLIGO` | SkillEffligo |
| 5278 | 能力 `CD_COMPETENTIA` | SkillCompetentia |
| 5279 | 气流风暴 `CD_PNEUMATICUS_PROCELLA` | SkillPneumaticusProcella；地面单位 Pneumaticus_Procella |
| 5280 | 恩爱治愈 `CD_DILECTIO_HEAL` | SkillDilectioHeal |
| 5281 | 信仰 `CD_RELIGIO` | StatusSkillImpl |
| 5282 | 祝福 `CD_BENEDICTUM` | StatusSkillImpl |
| 5283 | 请求 `CD_PETITIO` | SkillPetitio |
| 5284 | 框架 `CD_FRAMEN` | SkillFramen |
| 6518 | Divinus Flos `CD_DIVINUS_FLOS` | SkillDivinusFlos |
