# SYRK/SYR2K/SYMM：已有结果与本项目的超出范围

参考论文：

[Al Daas et al., Communication Lower Bounds and Optimal Algorithms for Symmetric Matrix Computations, arXiv:2409.11304](https://arxiv.org/abs/2409.11304)

## 2024 年论文已经覆盖的内容

该论文研究三类 symmetric 3NL kernel：

- SYRK：矩阵与自身转置相乘；
- SYR2K：两个矩阵乘积与其转置的组合；
- SYMM：一个输入矩阵是 symmetric 的矩阵乘法。

论文在 sequential 和 distributed-memory parallel 两种模型中都给出 communication lower bounds，并构造达到下界的算法。它区分 memory-dependent 和 memory-independent parallel bounds，并使用 symmetric Loomis–Whitney inequality、受约束优化和 triangle block partitioning。论文的 parallel model 使用每个 processor 的 local memory、fully connected network 和 bandwidth/latency 成本；算法覆盖 1D、2D、3D 组织以及 limited-memory 情况。

因此，本项目不能把“给 SYRK/SYMM 证明通信下界”本身作为新贡献目标。

## 本项目可能真正超出的部分

| 方向 | 2024 工作的主对象 | 本项目的候选扩展 |
|---|---|---|
| 层次 | sequential 或单层 distributed-memory parallel | 三层及 (L) 层嵌套层次树 |
| owner 结构 | triangular block partition 和 1D/2D/3D 算法 | 一般 nested partitions、Steiner/copy-lineage envelope |
| 成本 | bandwidth/latency 模型下的 parallel communication | 每条层次边独立的 word/read/write 权重 |
| tightness | 每个模型分别构造 optimal algorithm | 同一 nested partition 在每条边的 matching broadcast/reduction |
| 多级耦合 | 不以跨层 owner compatibility 为主要定理对象 | time-expanded owner、phase trace 和跨层 overlap charging |
| 对称结构 | 三角 iteration space 和 symmetric HBL | 把对称投影与三层 nested partition 同时纳入一个定理 |

## 需要保持的技术差异

SYRK/SYR2K/SYMM 的 iteration space 不是普通 GEMM 的完整立方体。对称输入和输出会改变：

1. 产品集合的定义；
2. A/B/C projection 的重叠关系；
3. 一个 partial 需要多少次归约；
4. 最优 block 是否是矩形块，而不是 triangle block；
5. HBL 约束是否应替换为 symmetric Loomis–Whitney inequality。

当前已先完成一个受限的 SYRK 静态起点：`docs/syrk-nested-incidence-extension.md` 用
union projection 处理对角项和非对角项的 A-entry 重叠，并证明 rooted nested
edge 上的 incidence lower bound 与树形 schedule tight。它仍然没有加入 finite-memory
phase 项，也不等于已经完成 SYMM。

因此，普通 GEMM 的 projection-boundary lemma 不能直接复制到 SYRK/SYMM。正确扩展顺序应是：

1. 先在普通 GEMM 上完成三层 nested-partition/phase theorem；
2. 把 symmetric 3NL 的 iteration set 和 projection map 单独定义；
3. 将 triangle block partition 视为已有的单层 matching construction；
4. 再研究 triangle owner partitions 在多级边权下是否也出现非矩形化或 Steiner 型最优结构。

## 当前可主张与不可主张的范围

可以主张：本项目已经得到 classical GEMM 的静态 nested-partition theorem、矩形 grid 特例、(L)-level/asymmetric-cost 形式和一个非对称成本下的矩形化反例。若未来完成 phase-trace coupling，其新意将是多级 owner/phase 兼容，而不是重新证明 SYRK/SYMM 的单层下界。

目前不能主张：已经改进了 2024 年 symmetric-kernel 的常数、已经覆盖 SYRK/SYMM 的多级 tight bound，或已经证明动态 replication/recomputation 下的对称 kernel 定理。
