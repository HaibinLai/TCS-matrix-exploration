# 多级嵌套通信下界：下一阶段研究计划

本文把下一阶段限定为一个可证伪、可逐步收紧的数学项目。目标不是立即宣称一个新的普适下界，而是确认：在经典 GEMM 的多级内存/处理器层次中，任意动态调度是否可以被一个嵌套分区问题刻画；若可以，再判断矩形处理器网格是否足以达到该分区问题的最优值。

## 当前已完成的基线

- 已固定三层模型：\(P_1\ge P_2\ge P_3\)，三条收费边分别是慢存储\(\leftrightarrow P_3\)、\(P_3\leftrightarrow P_2\)、\(P_2\leftrightarrow P_1\)。
- 已写出静态矩形网格的 ownership 下界，并验证其 leading term 是
  \[
  \frac{mk}{ab}+\frac{kn}{bc}+\frac{mn}{ac}
  \]
  （每个处理器的平均量，边界修正为 \(O((mk+kn+mn)/P)\)）。
- 已用 Loomis--Whitney 恢复单层 phase 项
  \[
  \Omega\!\left(\frac{mnk}{P\sqrt M}\right),
  \]
  但这还不能把任意调度提升为嵌套矩形网格定理。
- 已建立任意分区的投影边界候选量，并在 \(2\times2\times2\) 上完成一层和三层穷举检查。

这些结果分别属于“证明了的受限模型”“局部几何检查”和“尚未完成的目标定理”，不能混写。

## 研究主线

### 1. 先完成无容量 arbitrary-schedule theorem，再处理 phase

令产品集合为
\[
T=[m]\times[k]\times[n].
\]
对产品集合 \(S\subseteq T\)，定义三种投影
\[
\pi_A(S),\quad \pi_B(S),\quad \pi_C(S).
\]
对每个收费边，记录该边两侧 owner group 在时间窗口内共同负责的产品集合，得到分区 \(\Pi_\ell\)。动态调度需要用 time-expanded owner labels 处理：同一个标量乘法只能计入一个产品 owner，但输入复制和部分和迁移必须按边计费。

单个分区的投影边界是
\[
\partial(\Pi)=\sum_{S\in\Pi}
  (|\pi_A(S)|+|\pi_B(S)|+|\pi_C(S)|)
  -(mk+kn+mn).
\]
但多级边不能简单地把 \(\partial(\Pi_\ell)\) 相加，因为粗层已有的副本会在细层边界中再次出现。正确的嵌套分区目标使用投影和的逐边增量：
\[
X_A(\Pi)=\sum_{S\in\Pi}|\pi_A(S)|,
\quad X_B(\Pi)=\sum_{S\in\Pi}|\pi_B(S)|,
\quad X_C(\Pi)=\sum_{S\in\Pi}|\pi_C(S)|.
\]
令 \(\Pi_4=\{T\}\)，则带权目标是
\[
B_{\rm part,w}=\min_{\Pi_3\preceq\Pi_2\preceq\Pi_1}
\sum_{\ell=1}^{3} w_\ell\left[
\alpha_{\ell,A}(X_A(\Pi_\ell)-X_A(\Pi_{\ell+1}))
+\alpha_{\ell,B}(X_B(\Pi_\ell)-X_B(\Pi_{\ell+1}))
+\beta_{\ell,C}(X_C(\Pi_\ell)-X_C(\Pi_{\ell+1}))
\right].
\]
纯 aggregate volume 下所有 \(w\) 和数据类型成本相同，此式会 telescoping 到最细分区的边界；中间层只在带权、按层归一化或非对称成本下保留作用。

**已完成的第一证明目标（cut/Steiner lemma）**：在“经典、一次产品计算、复制按通信计费、初始输入只有一次、最终 \(C\) 归属固定”的条件下，固定三层 rooted hierarchy tree，对任意动态 owner labels 取每个数据项的需求叶集合。每条树边的 cut indicator 给出实际 word volume 下界；逐项 tree broadcast/reduction 达到它。正式陈述和有限枚举检查见 `docs/t3-arbitrary-schedule-steiner-theorem.md` 与 `experiments/check_t3_arbitrary_schedule_steiner.py`。

### 2. 把 phase/HBL 接到 cut/Steiner theorem

需要证明三件事：

1. 细层 owner group 的产品集合包含在粗层 owner group 中，即 \(\Pi_3\preceq\Pi_2\preceq\Pi_1\)；
2. 同一矩阵元素在不同收费边上的迁移可以按边分别计数，不因“跨两层的一次物理传输”而被错误合并；
3. 初始复制、最终归并和输出写回的项不会被投影边界重复计算。

这个任意嵌套分区下界现在已经在静态 owner-consistent 模型中写成并证明；Steiner 版本进一步不要求矩形 block，矩形 grid 只是一个可实现的受限子类。

### 3. 判断矩形化的适用范围

要回答的关键问题是：

> 对经典 GEMM 的投影边界，最优的嵌套分区是否总可以替换成同样层数、同样 owner 数的嵌套矩形块，而不增大边界？

研究顺序：

- 对纯 aggregate volume，记录 telescoping 后的最细 partition 问题；
- 对带权/非对称成本，比较一般 nested partition 与矩形 grid；
- 若发现反例，使用一般 nested-partition envelope，而不是把矩形化写成普适定理。

目前 \(2\times2\times2\) 的结果是：

```text
levels=(1, 2, 4) arbitrary_min=12 rectangular_min=12
levels=(2, 4, 8) arbitrary_min=24 rectangular_min=24
```

这只是有限证据，不能外推到一般维度。

另外，\(2\times2\times3\) 的两层穷举（owner 数为 2 和 4）检查了 46,200 条嵌套链，得到

```text
dims=(2, 2, 3) levels=(2,4) arbitrary_min=18 rectangular_min=18
```

对应脚本是 `experiments/check_nested_partition_223.py`。

在 $2\times2\times2$、$P=(8,4,2)$、边权 $(1,2,1)$ 下，任意 nested partition 的最优成本为 12，而矩形 grid chain 的最优成本为 16。这已经否定了非对称成本模型中的一般矩形化猜想；完整反例见 `docs/nested-partition-static-theorem.md`。

### 4. 接回物理容量与多级尺度（当前主缺口）

组合分区定理成立后，再把每一级的容量和处理器数接回去。当前采用
`docs/finite-capacity-phase-cut-envelope.md` 的联合 trace，而不是把两个
标量下界直接相加。对第 \(\ell\) 层，至少要同时保留三种量：

- phase/HBL 容量项，例如 \(\Omega(mnk/(P_\ell\sqrt{M_\ell}))\)；
- owner/replication 项，由 \(B_{\rm part}\) 或矩形 grid envelope 给出；
- 必需的输入输出项 \(\Omega(mk+kn+mn)\)。

不能把这些项未经证明直接相加。联合 trace 已给出一个总加载事件的可行域；
仍需对该可行域求出闭式或可证明的整数/连续 envelope，并说明哪些 schedule
达到它。最终形式可能类似
\[
Q_\ell\ge
\max\{Q^{\rm phase}_\ell,Q^{\rm owner}_\ell,Q^{\rm I/O}_\ell\}
\]
或在明确的静态、一次计算模型下得到可加式。三层以后推广为
\[
\Pi_L\preceq\cdots\preceq\Pi_1,
\qquad
Q\ge \sum_{\ell=1}^{L} w_\ell\,\Delta(\Pi_\ell,\Pi_{\ell+1}),
\]
其中 \(\Delta\) 是投影 incidence 的逐边增量；任意动态调度版本仍需单独验证。

### 5. 构造匹配算法

下界只有在匹配算法明确后才有研究价值。按难度递增：

1. 三层静态 \(a\times b\times c\) blocked SUMMA/2.5D/3D 调度；
2. 每层容量恰好达到 phase 项的 tiled GEMM；
3. 允许非对称边成本的带权复制和归并；
4. \(L\) 层递归 blocking；
5. 矩形 GEMM、SYRK/SYMM，以及允许 replication 或 recomputation 的模型。

每个算法都要记录：每层读写量、消息数、同步次数、初始复制假设、输出归并方式和峰值容量。只有上下界在同一模型、同一计费规则下匹配，才称为 tight。

## 判定标准与停止条件

- **成功定理**：任意调度 \(\Rightarrow\) 嵌套分区增量下界，并有相同模型下的 matching schedule。
- **当前已知边界**：静态 nested partition 已达到上述目标；非对称成本下矩形化失败，因此不能把 factor-chain envelope 当作普适对象。
- **应停止外推的情况**：如果动态复制、重算或自由初始复制让 partition boundary 无法对应通信事件，就把结论限定为静态 owner-consistent、一次产品计算模型，并把动态模型列为独立问题。


## 近期执行顺序

1. 对 `E-TRACE` 做 (2^3) 和 (3^3) GEMM 的整数 trace 搜索，测出 overlap correction；
2. 将有限容量 phase/HBL 项与 nested-partition/Steiner 增量项对齐；
3. 用多源 Steiner forest 处理 free replication，再对 recomputation 优化 compute-event assignment；
4. 在一般 nested partition 基础上再研究 SYRK/SYMM 等结构化 kernel；
5. 只把矩形 factor arrangement 作为可实现特例和实验平台。

仓库中的每一个脚本都应输出模型假设和检查结论，避免把有限穷举误写成普适证明，喵。
