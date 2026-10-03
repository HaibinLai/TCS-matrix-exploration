# 多级通信下界的先前工作与本项目边界

必须纳入比较的先前工作：

[Grigori, Jacquelin, Khabou, Performance predictions of multilevel communication optimal LU and QR factorizations on hierarchical platforms](https://eprints.maths.manchester.ac.uk/2122/1/isc_camera_ready.pdf), 2013。

## Hcp 工作已经做了什么

该工作提出 Hierarchical Cluster Platform (Hcp) 模型，显式表示多个 parallelism levels。每层有自己的节点数、memory size、latency、inverse bandwidth 和 message aggregation capacity；论文还讨论每层需要的通信 volume 和 message count，并给出多级 QR 算法。文中指出其模型可把已有的 direct-linear-algebra lower bounds 推广到层次平台，并给出每层的通信下界框架。

因此不能把以下说法作为本项目的贡献：

- “第一个多级层次通信模型”；
- “第一个在每层给出通信下界的工作”；
- “第一个为层次平台构造 matching communication-avoiding algorithm”。

## 本项目仍可能精确化的地方

Hcp 是面向层次平台和 direct linear algebra 的架构/性能模型。当前项目的候选增量在于更细的 classical GEMM 组合结构：

1. 以 GEMM product set 的 A/B/C projections 定义 owner partitions；
2. 证明 arbitrary nested partitions 的逐边 incidence lower bound；
3. 把矩形 grid 作为特例，而不把 factor chain 当作普适最优结构；
4. 在 asymmetric edge/data-type costs 下给出非矩形化反例；
5. 用 copy-lineage/Steiner envelope 表示每个 entry 的多级传播和 C partial reduction；
6. 明确 phase/HBL 与 owner boundary 的 overlap，而不是把两种下界未经证明相加。

这些是“经典 GEMM 的组合/依赖级精化”，不是多级通信下界领域的首次工作。

## 与当前模型的对应关系

| Hcp 概念 | 当前项目对应物 |
|---|---|
| hierarchy level | (E_1,E_2,E_3) 收费边 |
| level memory (M_i) | phase/HBL capacity (M_\ell) |
| bandwidth/latency (β_i,α_i) | edge/data-type weights和 message costs |
| aggregation capacity (φ_i) | phase trace 和 batch/reload 约束 |
| lower bound at each level | nested-partition incidence 或 Steiner edge cost |
| multilevel algorithm | nested broadcast/reduction schedule |

## 研究定位

如果未来只能恢复 Hcp 式的每层
[
W_i=\Omega(\text{work}/\sqrt{\text{memory}})
]
标度，那么结果主要是已有 multilevel lower-bound 框架在 GEMM 上的重述。真正有区分度的目标应是：在明确的 GEMM owner/phase 模型下，证明一个逐边、带成本权重、带 matching schedule 的 nested-partition theorem，并说明何时可推广到 dynamic replication 或 recomputation。
