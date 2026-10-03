# 多级嵌套通信下界：下一阶段研究计划

本文把下一阶段限定为一个可证伪、可逐步收紧的数学项目。目标不是立即宣称一个新的普适下界，而是确认：在经典 GEMM 的多级内存/处理器层次中，任意动态调度是否可以被一个嵌套分区问题刻画；若可以，再判断矩形处理器网格是否足以达到该分区问题的最优值。

## 当前已完成的基线

- 已固定三层模型：\(P_1\ge P_2\ge P_3\)，三条收费边分别是慢存储\(\leftrightarrow P_3\)、\(P_3\leftrightarrow P_2\)、\(P_2\leftrightarrow P_1\)。
- 已写出静态矩形网格的 ownership 下界，并验证其 leading term 是
  \[
  \\frac{mk}{ab}+\\frac{kn}{bc}+\\frac{mn}{ac}
  \]
  （每个处理器的平均量，边界修正为 \(O((mk+kn+mn)/P)\)）。
- 已用 Loomis--Whitney 恢复单层 phase 项
  \[
  \\Omega\\!\\left(\\frac{mnk}{P\\sqrt M}\\right),
  \]
  但这还不能把任意调度提升为嵌套矩形网格定理。
- 已建立任意分区的投影边界候选量，并在 \(2\\times2\\times2\) 上完成一层和三层穷举检查。

这些结果分别属于“证明了的受限模型”“局部几何检查”和“尚未完成的目标定理”，不能混写。

## 研究主线

### 1. 把任意调度转成嵌套分区

令产品集合为
\[
T=[m]\\times[k]\\times[n].
\]
对产品集合 \(S\\subseteq T\)，定义三种投影
\[
\\pi_A(S),\\quad \\pi_B(S),\\quad \\pi_C(S).
\]
对每个收费边，记录该边两侧 owner group 在时间窗口内共同负责的产品集合，得到分区 \(\Pi_\\ell\)。动态调度需要用 time-expanded owner labels 处理：同一个标量乘法只能计入一个产品 owner，但输入复制和部分和迁移必须按边计费。

目标定义是
\[
\\partial(\\Pi)=\\sum_{S\\in\\Pi}
  (|\\pi_A(S)|+|\\pi_B(S)|+|\\pi_C(S)|)
  -(mk+kn+mn),
\]
以及嵌套分区优化
\[
B_{\\rm part}=\\min_{\\Pi_3\\preceq\\Pi_2\\preceq\\Pi_1}
\\sum_{\\ell=1}^{3} w_\\ell\\partial(\\Pi_\\ell),
\]
其中 \(w_\\ell\) 是边的 word/message 成本权重。若成本是纯 word volume，取 \(w_\\ell=1\)；若每层字宽、消息启动或同步成本不同，保留权重。

**第一证明目标（partition boundary lemma）**：在“经典、一次产品计算、复制按通信计费、初始输入只有一次、最终 \(C\) 归属固定”的条件下，证明每个收费边的实际通信量不小于相应投影边界，减去明确写出的初始/最终项。这里必须区分：投影边界是组合量，通信量是事件量；两者之间的 owner-consistency 映射是证明核心。

### 2. 证明嵌套兼容与边可加性

需要证明三件事：

1. 细层 owner group 的产品集合包含在粗层 owner group 中，即 \(\Pi_3\\preceq\\Pi_2\\preceq\\Pi_1\)；
2. 同一矩阵元素在不同收费边上的迁移可以按边分别计数，不因“跨两层的一次物理传输”而被错误合并；
3. 初始复制、最终归并和输出写回的项不会被投影边界重复计算。

完成后得到的是一个**任意嵌套分区下界**。它仍然不等于当前的矩形 grid envelope，因为矩形分区只是所有分区的一小部分。

### 3. 检验并证明矩形化，或寻找反例

要回答的关键问题是：

> 对经典 GEMM 的投影边界，最优的嵌套分区是否总可以替换成同样层数、同样 owner 数的嵌套矩形块，而不增大边界？

研究顺序：

- 先枚举 \(2\\times2\\times2\)、\(2\\times2\\times3\) 和 \(3\\times3\\times3\) 的小规模分区；
- 对每个层数和 owner 数比较任意分区、嵌套分区、矩形 grid 分区的最优值；
- 若发现反例，优先给出最小反例并把普适目标改写为 \(B_{\\rm part}\)；
- 若长期未发现反例，再尝试用离散压缩（compression/shifting）、投影不增原理或三维等周不等式证明矩形化。

目前 \(2\\times2\\times2\) 的结果是：

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

### 4. 接回物理容量与多级尺度

组合分区定理成立后，再把每一级的容量和处理器数接回去。对第 \(\\ell\) 层，至少要同时保留三种量：

- phase/HBL 容量项，例如 \(\\Omega(mnk/(P_\\ell\\sqrt{M_\\ell}))\)；
- owner/replication 项，由 \(B_{\\rm part}\) 或矩形 grid envelope 给出；
- 必需的输入输出项 \(\\Omega(mk+kn+mn)\)。

不能把这些项未经证明直接相加。需要先说明哪些事件集合互不相交，或者给出带权 charging，使最终形式类似
\[
Q_\\ell\\ge
\\max\\{Q^{\\rm phase}_\\ell,Q^{\\rm owner}_\\ell,Q^{\\rm I/O}_\\ell\\}
\]
或在明确的静态、一次计算模型下得到可加式。三层以后推广为
\[
\\Pi_L\\preceq\\cdots\\preceq\\Pi_1,
\\qquad
Q\\ge \\sum_{\\ell=1}^{L} w_\\ell\\,\\partial(\\Pi_\\ell)-\\text{boundary terms},
\]
仍需单独验证任意调度版本。

### 5. 构造匹配算法

下界只有在匹配算法明确后才有研究价值。按难度递增：

1. 三层静态 \(a\\times b\\times c\) blocked SUMMA/2.5D/3D 调度；
2. 每层容量恰好达到 phase 项的 tiled GEMM；
3. 允许非对称边成本的带权复制和归并；
4. \(L\) 层递归 blocking；
5. 矩形 GEMM、SYRK/SYMM，以及允许 replication 或 recomputation 的模型。

每个算法都要记录：每层读写量、消息数、同步次数、初始复制假设、输出归并方式和峰值容量。只有上下界在同一模型、同一计费规则下匹配，才称为 tight。

## 判定标准与停止条件

- **成功定理**：任意调度 \(\\Rightarrow\) 嵌套分区下界；矩形化成立；再有调度达到同阶或同 leading constant 的上界。
- **有价值的部分结果**：任意分区下界成立，但矩形化失败；这会给出更一般的 \(B_{\\rm part}\) 定理和一个明确的非矩形反例。
- **应停止外推的情况**：如果动态复制、重算或自由初始复制让 partition boundary 无法对应通信事件，就把结论限定为静态 owner-consistent、一次产品计算模型，并把动态模型列为独立问题。

## 近期执行顺序

1. 完成 \(2\\times2\\times3\) 的一层/三层穷举，寻找最小非矩形反例；
2. 写出并审查 partition boundary lemma 的事件级证明；
3. 给出三层静态模型的正式 corollary，并与现有矩形 grid 公式逐项对齐；
4. 只在前三步没有逻辑缺口时，尝试一般矩形化猜想；
5. 最后再扩展到 \(L\) 层和非对称成本。

仓库中的每一个脚本都应输出模型假设和检查结论，避免把有限穷举误写成普适证明，喵。
