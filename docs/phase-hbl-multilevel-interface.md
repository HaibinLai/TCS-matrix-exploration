# Phase/HBL 下界与多级 ownership 的接口

这份文件把经典的一层 phase argument 写成可接入多级定理的引理，并明确为什么目前只能取 `max`，不能未经证明直接把 phase 项和 ownership 项相加。

## 一层 phase 模型

一个 owner 计算 `W` 个 classical GEMM products，fast memory 容量为 `M` words。把执行划分为 phases，使每个完整 phase 至多发生 `M` 次 word transfer；phase 开始时最多已有 `M` 个 words。

在一个 phase 中，令 `x,y,z` 分别是出现过的 A、B 和 C/partial entries 数量。于是

$$
x+y+z ≤ 2M.
$$

Loomis–Whitney 给出

$$
F_phase ≤ √(xyz).
$$

在固定和下由 AM–GM，

$$
F_phase ≤ \left((x+y+z)/3\right)^{3/2}
≤ (2M/3)^{3/2}.
$$

因此完整 phases 数量至少为

$$
R ≥ W/(2M/3)^{3/2},
$$

而通信量满足

$$
Q ≥ M(R-1)
≥ (3/2)^{3/2}\,W/√M - M.
\tag{PHASE-HBL}
$$

常数来自这里明确采用的 `M transfers per phase` 约定；改变 phase 预算只会改变常数，不改变 (W/\sqrt M) 的量纲。

对 (P) 个 owner，若第 (r) 个 owner 完成 (W_r) 个 products、容量为 (M_r)，逐 owner 相加得到

$$
Q ≥ (3/2)^{3/2}\sum_r W_r/√{M_r}-\sum_r M_r.
$$

在均衡 (W_r=W/P)、均匀容量 (M_r=M) 时，主项为

$$
Q = Ω\left(W/(P√M)\right).
$$

这恢复了 classical GEMM 的标准 one-level phase/HBL scaling。

## 与 projection boundary 的关系

ownership theorem 统计“一个 entry 需要到达多少 owner groups”；phase theorem 统计“同一个 owner 在容量不足时需要重复装入多少 entries”。二者可能对同一个 transfer 计数：一个 A word 第一次到达 owner 时既创建了 owner copy，也可能是某个 phase 的输入。

所以在没有额外事件标记时，只能安全写成

$$
Q_\ell ≥
\max\{Q_\ell^{\rm owner},Q_\ell^{\rm phase},Q_\ell^{\rm I/O}\}.
\tag{MAX-interface}
$$

要得到加法式

$$
Q_\ell ≥ Q_\ell^{\rm owner}+Q_\ell^{\rm phase}-\text{overlap correction},
$$

必须定义 copy-creation、phase-reload 和 final-reduction 的不相交事件集，或者证明一个 charging scheme 对每个 transfer 只分配一次。当前还没有这个联合引理。

## 多级接口目标

对第 (ell) 条边，设其 owner partition 增量为

$$
\Delta_\ell^{\rm owner}=
\Delta_\ell^A+\Delta_\ell^B+\Delta_\ell^C.
$$

设这一层的 phase 容量为 (M_\ell)，并令 (W_{\ell,r}) 是对应 owner 在该层负责的 products 数。一个可验证的目标形式是

$$
V_\ell ≥
\max\left\{
\Delta_\ell^{\rm owner},
(3/2)^{3/2}\sum_r W_{\ell,r}/√{M_\ell}-\sum_r M_\ell,
\text{I/O term}
\right\}.
\tag{T3-interface}
$$

这仍然只是逐边候选式；要把三个层次相加，还要证明不同边上的 phase reload 不会被同一条跨层 word transfer 同时满足。

## 为什么这一步比继续扫参数重要

25-line arrangement 只能决定某个矩形 grid chain 的几何系数。`PHASE-HBL` 决定容量受限时一个 owner 能完成多少工作；两者属于不同层次的约束。只有完成 `T3-interface` 的 overlap charging，才能把几何 envelope 解释成有限容量下的真正 tight communication theorem。

## 当前边界

本引理假设：一次计算、无 recomputation、每个 phase 的 transfer budget 明确、所有 products 归属于固定 owner。它不自动覆盖：

- dynamic owner migration；
- free initial replication；
- recomputation；
- heterogeneous capacities 与不平衡工作；
- SYRK/SYMM 共享 operand 的额外复用。

下一步应先在 (2\times2\times2\) 或小型矩形 GEMM 上建立事件级 overlap 计数；若出现同一 transfer 同时承担两类下界的反例，则最终定理必须采用 `max` 或显式 overlap correction，而不能写成简单加法。
