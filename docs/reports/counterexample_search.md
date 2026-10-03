# Counterexample / multilevel-composition search report

日期：2026-10-03

## 目标

检查当前的“逐层 lower-envelope + nested compatibility”模型是否在小型非二次幂、非质数、三层/四层 hierarchy 中出现反例，重点搜索：

1. global nested/independent ratio 是否超过目前关注的 `3/2`；
2. 四层 hierarchy 是否比三层出现更大的兼容性开销；
3. 处理器数不是单纯二次幂、且含 composite factor 的配置是否破坏边界点规律。

这里的 `H` 是当前脚本中的三项 grid-volume proxy，结论只适用于这个离散模型，不能直接等同于完整 HCP/message-volume theorem。

## 使用的程序

- `work/scan_multilevel_boundary_hull.py`：在边界 `z/x=1` 上，用 Fraction-exact affine lower-envelope hull + dynamic programming 处理任意层数；每个层级的 grid 为 `(a,b,c)`，满足 `abc=P`，相邻层要求坐标整除。
- `work/scan_multilevel_boundary_dp.py`：同一边界的 pairwise exact pruning 版本，用于小规模交叉检查。
- `work/exact_multilevel_2d.py`：完整二维 aspect-ratio domain `0<=y<=z<=1` 的 exact arrangement；单个大 hierarchy 较慢，适合定点核验。
- `work/scan_composite_p_family.py`：三层 family `(2*p*q, p*q, p)` 的 exact endpoint scan，其中 `p` 可以 composite，`q` 取素数。

## 三层全扫描（非二次幂和 composite）

本地命令：

```text
python work/scan_multilevel_boundary_hull.py --levels 3 --limit 500 --top 30
```

枚举所有结构化三层计数 `(p0,p1,p2)`，其中 `p0=p2*r2*r1`、`p1=p2*r2`，总层级最大计数 `p0<=500`，共检查 4107 个 hierarchy。最大的边界比为：

```text
(470, 235, 5)  ratio 1075/823 = 1.3061968408262454  t=1/5
(430, 215, 5)  ratio 985/757  = 1.3011889035667108  t=1/5
(414, 207, 9)  ratio 963/748  = 1.2874331550802138  t=1/9
(492, 246, 6)  ratio 341/266  = 1.281954887218045  t=17/123
```

这些都是非二次幂配置。最大点多落在 `t=1/p2` 或附近，尚未出现 `>1.5` 的反例。

更大的远程扫描使用 `retreat`：

```text
scp work/scan_multilevel_boundary_hull.py work/scan_multilevel_boundary_dp.py retreat:/tmp/mmio-work/
ssh retreat 'cd /tmp/mmio-work; nohup python3 scan_multilevel_boundary_hull.py --levels 3 --limit 1000 --top 30 >/tmp/mmio-1000.out 2>&1 </dev/null &'
```

输出：`checked=11217 hierarchies levels=3 limit=1000`。最大值为：

```text
(954, 477, 9)  ratio 726/535 = 1.3570093457943926  t=1/9
(846, 423, 9)  ratio 645/478 = 1.3493723849372385  t=1/9
(774, 387, 9)  ratio 591/440 = 1.3431818181818183  t=1/9
(994, 497, 7)  ratio 2261/1685 = 1.341839762611276  t=1/7
```

第一名正好属于 family `(2*p*q,p*q,p)`，即 `p=9,q=53`。比值仍低于其渐近值 `3p/(2p+1)=27/19≈1.42105`，也低于 `3/2`。

## 三层 composite-family endpoint scan

本地命令：

```text
python work/scan_composite_p_family.py --p-max 30 --q-max 300 --top 20
```

共检查 1556 个 `(p,q)`（`q` 为素数且 `q>p`）。最大值：

```text
p=25 q=293 ratio=16525/11426 = 1.446262909
p=25 q=283 ratio=31925/22087 = 1.445420383
p=27 q=293 ratio=11898/8233  = 1.445159723
```

随着 `q` 增大，比值接近 `3p/(2p+1)`，但在扫描范围内没有超过 `3/2`。这与已有奇数 `p` 渐近公式一致。

## 四层扫描

远程命令：

```text
ssh retreat 'cd /tmp/mmio-work; nohup python3 scan_multilevel_boundary_hull.py --levels 4 --limit 120 --top 30 >/tmp/mmio-4-120.out 2>&1 </dev/null &'
```

输出：`checked=284 hierarchies levels=4 limit=120`。最大值：

```text
(104, 52, 26, 2)  ratio 1331/1165 = 1.1424892703862661  t=60/143
(112, 56, 28, 4)  ratio 803/707   = 1.1357850070721358  t=18/77
(88, 44, 22, 2)   ratio 385/339   = 1.1356932153392330  t=52/121
(84, 42, 21, 3)   ratio 453/400   = 1.1325                  t=1/3
```

这覆盖了 composite 计数以及明显的非二次幂层级；四层开销没有比三层扫描中观察到的 `1.357...` 更大。`limit=120` 是出于 exact DP 运行时间的限制，不能视作任意四层结论。

## 二维 exact spot-check

对一个较大的非二次幂三层配置：

```text
python work/exact_multilevel_2d.py --pstars 99 33 3
```

得到：

```text
max ratio = 459/395 = 1.1620253164556962
at (z,y)=(1,1/3)
```

这只是单点 hierarchy 的完整二维 arrangement 核验；它支持边界候选点的经验规律，但不能替代批量二维证明。

## 结论与当前假设的关系

目前没有找到反例。有限证据支持下列受限经验命题：

> 对当前 `H` proxy、坐标整除型 nested grids，以及 `0<=y<=z<=1` 的 aspect domain，三层和四层的 nested/independent overhead 在测试范围内小于 `3/2`；较大值主要来自三层 `(2*p*q,p*q,p)` family，并在 `t≈1/p` 处达到。

但这还不是定理，原因有三点：

1. 绝大多数批量扫描是在 `z/x=1` 边界，不是完整二维 domain；
2. processor counts 被限制为坐标整除的 nested chains，未覆盖 replication、非整除映射、通信算法中的重排；
3. `H` 是 grid-volume proxy，不能自动推出实际 message count、同步次数或 latency-sensitive lower bound。

因此，当前最小的可证明目标仍是：先为三层 family `(2*p*q,p*q,p)` 证明 `t=1/p` 是 global maximizer，并确认其 ratio 小于 `3/2`；然后再研究四层的递归兼容性。当前扫描应被视为“没有发现反例 + 缩小证明目标”，而不是新的普适紧下界。

## Superseding update (2026-10-03)

The restricted prime family `(2*p*q,p*q,p)` is now closed analytically for prime
\(p\ge3,q>2p\):
\[
\max N/I=p(9q+7)/((6p+3)q+3p^2+4p)
\]
 at \((z,y)=(1,1/p)\). This replaces the earlier “minimum provable target” wording for that
family. Composite p and the general three/four-level hierarchy scans remain empirical, and the
broader multilevel communication problem is still open.
