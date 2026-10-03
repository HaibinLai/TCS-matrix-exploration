# 并行矩阵乘法 I/O：探索日志 1

日期：2026-10-02  
主题：从 2022 memory-independent bound 走向 memory/multilevel 统一问题

## 1. 当前选定的问题

研究 classical rectangular matrix multiplication

\[
A_{m\times k}B_{k\times n}=C_{m\times n},\qquad m\ge n\ge k,
\]

在 \(P\) 个处理器上运行。每个处理器有本地内存 \(M\)，处理器间通信按 critical-path words 计；进一步考虑每个处理器内部存在多个容量

\[
M_1<M_2<\cdots<M_L
\]

的层级。

当前不是立即声称“解决多级下界”，而是先把已知两种下界放进同一张图，再找它们无法直接拼接的位置。

## 2. 2022 定理的可操作形式

令

\[
m=\max(n_1,n_2,n_3),\quad n=\operatorname{median}(n_1,n_2,n_3),\quad k=\min(n_1,n_2,n_3).
\]

Al Daas et al. 将单个负载均衡处理器需要访问的数据量转化为优化问题：

\[
\min_{x_1,x_2,x_3}x_1+x_2+x_3
\]

满足

\[
\left(\frac{mnk}{P}\right)^2\le x_1x_2x_3,
\]

以及单个矩阵访问的必要下界

\[
\frac{nk}{P}\le x_1,\qquad
\frac{mk}{P}\le x_2,\qquad
\frac{mn}{P}\le x_3.
\]

乘积约束来自 Loomis–Whitney；三个单独约束来自“一个矩阵元素最多参与多少次乘法”的计数。这个第二组约束正是长宽比很不平衡时改进旧结果的关键。

KKT 解给出三个区域：

\[
D(m,n,k,P)=
\begin{cases}
\dfrac{mn+mk}{P}+nk,&1\le P\le \dfrac{m}{n},\\[6pt]
2\sqrt{\dfrac{mnk^2}{P}}+\dfrac{mn}{P},
&\dfrac{m}{n}\le P\le \dfrac{mn}{k^2},\\[8pt]
3\left(\dfrac{mnk}{P}\right)^{2/3},
&P\ge \dfrac{mn}{k^2}.
\end{cases}
\]

在“起始只有一份输入、结束只有一份输出、计算或数据负载均衡”的模型中，通信下界写成

\[
Q_{\mathrm{MI}}
\ge
D(m,n,k,P)-\frac{mn+mk+nk}{P}.
\]

对于方阵 \(n\times n\)，这退化为

\[
Q_{\mathrm{MI}}
\ge 3\frac{n^2}{P^{2/3}}-3\frac{n^2}{P}.
\]

论文还给出 3D processor-grid、All-Gather 加 Reduce-Scatter 的算法达到这些常数；因此这不是只有 proof-side 的 bound。

来源：[arXiv HTML](https://arxiv.org/html/2205.13407v1)，尤其是优化问题、Theorem 3、Corollary 4 和 limited-memory 讨论。

## 3. 与 memory-dependent bound 的拼接

已有的两级本地内存下界，leading term 可写作

\[
Q_{\mathrm{MD}}
\gtrsim
\frac{2mnk}{P\sqrt M},
\]

在适用的内存与负载均衡条件下成立。于是对单个本地内存层级，一个自然的候选组合是

\[
Q(M)
\gtrsim
\max\left\{
\frac{2mnk}{P\sqrt M},
D(m,n,k,P)-\frac{mn+mk+nk}{P}
\right\}.
\]

对方阵，其 leading terms 是

\[
Q(M)
\gtrsim
\max\left\{
\frac{2n^3}{P\sqrt M},
3\left(\frac{n^3}{P}\right)^{2/3}
\right\}.
\]

两个项相等的交叉点满足

\[
M=\frac{4}{9}\frac{n^2}{P^{2/3}}.
\]

这与 2022 论文的 limited-memory 分析一致：在高并行区间，memory-dependent 项可能超过 memory-independent 项；而在较低并行区间，memory-independent 项已经支配。论文明确指出，3D 算法达到 memory-independent bound 需要足够临时空间；内存不足时，减少空间会增加 bandwidth。

## 4. 多级内存的候选定理

设每个处理器有层级容量

\[
M_1<M_2<\cdots<M_L,
\]

并令 \(Q_\ell\) 表示在层级 \(\ell\) 与下一层之间移动的 words。最保守、可逐层验证的候选下界是

\[
Q_\ell
\gtrsim
\max\left\{
\frac{2mnk}{P\sqrt{M_\ell}},
Q_{\mathrm{MI}}(m,n,k,P)
\right\},
\]

但这只能作为**候选形式**，不能直接当成已证明的 multilevel theorem。原因是：

1. \(Q_{\mathrm{MI}}\) 统计处理器之间的移动，而 \(M_\ell\) 统计处理器内部层级移动；两者不是同一条边。
2. 对每一级分别成立的下界不能自动相加；同一数据可能在多个层级被复用，或者一次上层传输触发多次下层访问。
3. 能达到 \(M_1\) 最优 tile 的 schedule，未必同时达到 \(M_2\) 或 HBM/DRAM 的最优 tile。
4. 3D replication、packing、fusion、prefetch 和异步 copy 会改变“一个 segment”应如何定义。

因此可行的正式目标应写成：证明每级单独下界，并构造一个 schedule 使

\[
Q_\ell=O(\mathrm{LB}_\ell)
\quad\text{for every }\ell,
\]

同时控制处理器间通信、临时空间和消息数。

## 5. 一个可证伪的研究猜想

### 猜想 M1：分层可组合性（受限版本）

对 classical rectangular GEMM，若：

- 每一级是理想 fully associative memory；
- 数据移动只沿相邻层级发生；
- 不允许压缩编码和近似计算；
- 每层 tile 可嵌套，且处理器间使用规则 3D grid；
- 输入和输出各只有一份初始/最终副本；

则存在一个分层递归 schedule，使每一级的通信量达到

\[
\Theta\!\left(
\max\left\{
\frac{mnk}{P\sqrt{M_\ell}},
Q_{\mathrm{MI}}(m,n,k,P)
\right\}
\right)
\]

的阶；若要求 leading constants 同时 tight，则需要额外的 tile 对齐条件。

这个猜想很具体，也容易被反例推翻：只要找到某种 \((m,n,k,P,M_1,M_2)\) 使所有嵌套 schedule 至少有一个层级多出多项式或固定常数因子，就说明简单的“逐级 max”不够。

### 猜想 M2：对称核的分层降常数

对 SYRK/SYMM，2024/2025 的三角分块已经在 sequential 和 distributed-memory 模型给出 tight bound。下一步可以问：三角迭代空间在多级内存中是否存在一个同时继承对称性常数下降的嵌套 schedule，还是某一级必须重新支付接近 GEMM 的重复读取代价？

来源：[Symmetric Matrix Computations](https://arxiv.org/abs/2409.11304)。

## 6. 第一轮可做的证明任务

### 任务 A：先做方阵、两级本地内存

固定 \(m=n=k=N\)，证明或复核

\[
Q\ge \max\left\{
\frac{2N^3}{P\sqrt M},
3\frac{N^2}{P^{2/3}}-3\frac{N^2}{P}
\right\}
\]

在明确的输入/输出副本和内存条件下成立，并标出两个项的支配区域。

### 任务 B：检查 3D schedule 的空间需求

对 processor grid \(p_1\times p_2\times p_3\)，写出：

- 每个处理器的 A/B/C 初始块；
- All-Gather 后的局部 A/B 投影；
- Reduce-Scatter 前的临时 D；
- 各项随 \(p_1,p_2,p_3\) 的大小。

然后验证达到 memory-independent bound 的网格是否要求

\[
M=\Omega\left(\left(\frac{N^3}{P}\right)^{2/3}\right)
\]

量级的临时空间。

### 任务 C：加入第二个本地层级

选择 \(M_1\) 为 shared/register 级、\(M_2\) 为 HBM 级，先不考虑真实 bank conflict。对嵌套 tile 做一个小规模整数搜索，记录每个 tile 方案的：

- \(Q_1\)：register/shared ↔ HBM 的元素移动；
- \(Q_2\)：HBM ↔ host 或 global 的元素移动；
- processor communication；
- 临时空间。

目标是找出“每一级单独最优但无法同时最优”的最小反例。

## 7. 当前判断

目前最有研究价值的 gap 不是重新证明 2022 的一般并行下界，而是：

> **把 2022 的矩形、aspect-ratio-aware、tight-constant 结果，与有限本地内存和多级内存的嵌套 schedule 统一起来，并确定这种统一是否存在。**

这个问题承接了已知定理，同时保留了清晰的理论失败条件：模型、复制、临时空间或层级之间的非可组合性都可能成为真正的新结果。

## 8. 参考入口

- [Al Daas et al. 2022: Tight Memory-Independent Parallel Matrix Multiplication Communication Lower Bounds](https://arxiv.org/abs/2205.13407)
- [Al Daas et al. 2024/2025: Communication Lower Bounds and Optimal Algorithms for Symmetric Matrix Computations](https://arxiv.org/abs/2409.11304)
- [Kwasniewski et al. 2019: Red-blue pebbling revisited / COSMA](https://arxiv.org/abs/1908.09606)
- [Smith et al. 2017: A Tight I/O Lower Bound for Matrix Multiplication](https://arxiv.org/abs/1702.02017)

## 9. 任务 A 结果：方阵两级模型

固定方阵规模为 \(N\times N\)，每个处理器本地内存为 \(M\)。在 2022 年的 one-copy input/output 和 load-balanced 模型下，memory-independent bound 的完整形式为

\[
Q_{\mathrm{MI}}\ge 3\frac{N^2}{P^{2/3}}-3\frac{N^2}{P}.
\]

有限内存的 leading term 为

\[
Q_{\mathrm{MD}}\ge \frac{2N^3}{P\sqrt M}.
\]

因此可使用

\[
Q\ge \max\{Q_{\mathrm{MI}},Q_{\mathrm{MD}}\}
\]

作为两种已知下界的联合表达，但它只有在分别满足两种模型假设时才成立；它不是一个新的独立定理。

若只比较 leading terms，交叉条件为

\[
\frac{2N^3}{P\sqrt M}=3\frac{N^2}{P^{2/3}}
\quad\Longleftrightarrow\quad
M=\frac49\frac{N^2}{P^{2/3}}.
\]

所以：

- \(M<\frac49N^2P^{-2/3}\) 时，memory-dependent 项更大；
- \(M>\frac49N^2P^{-2/3}\) 时，memory-independent 项更大；
- 在交叉附近，不能只用“3D 一定最优”或“2D 一定最优”的口号，需要检查临时空间和通信实现。

小规模数值核对脚本位于 `work/work_verify_parallel_bounds.py`。它只验证公式的支配关系，不是定理证明，也不模拟网络或 cache。

## 10. 任务 B 结果：3D processor-grid 的空间需求

对一般 \(n_1\times n_2\) 乘 \(n_2\times n_3\)，令 processor grid 为

\[
p_1\times p_2\times p_3,
\qquad p_1p_2p_3=P.
\]

2022 算法的一个处理器在 All-Gather 后需要访问的三类主要数据规模为

\[
S_A=\frac{n_1n_2}{p_1p_2},
\qquad
S_B=\frac{n_2n_3}{p_2p_3},
\qquad
S_D=\frac{n_1n_3}{p_1p_3}.
\]

其中 \(D\) 是本地乘法产生、之后要通过 Reduce-Scatter 合并的临时结果。最终输出归属的本地块规模约为

\[
S_C=\frac{n_1n_3}{P},
\]

初始输入分片也约为总输入大小除以 \(P\)。因此峰值本地空间至少要容纳

\[
M_{\mathrm{peak}}
\gtrsim
S_A+S_B+S_D
\]

再加上本地输入/输出分片、packing buffer 和通信库临时空间。

对方阵且取平衡网格

\[
p_1=p_2=p_3=P^{1/3},
\]

有

\[
S_A=S_B=S_D=\frac{N^2}{P^{2/3}},
\qquad
M_{\mathrm{peak}}\gtrsim 3\frac{N^2}{P^{2/3}}.
\]

这与 memory-independent 通信下界的 leading term 同阶。由此得到一个重要的实际限制：达到 3D memory-independent 常数的算法需要 \(\Theta(N^2/P^{2/3})\) 级别的临时空间；如果只有 \(\Theta(N^2/P)\) 的最低存储，就不能直接使用这个 3D schedule，必须牺牲 bandwidth、增加分阶段或采用 2.5D trade-off。

这也解释了为什么“memory-independent bound tight”与“在任意有限内存上都可达到”是两个不同命题。2022 论文明确指出，3D 算法在有限内存下可能需要增加 bandwidth。

## 11. 当前最小反例搜索计划

下一步不先声称多级定理，而是枚举小规模整数参数：

\[
P\in\{8,27,64,125\},
\quad p_1p_2p_3=P,
\quad M_1<M_2.
\]

对每个 processor grid 计算

\[
(S_A,S_B,S_D),
\quad
M_{\mathrm{peak}},
\quad
Q_{\mathrm{MI}},
\quad
Q_{\mathrm{MD}}\(M_1\),Q_{\mathrm{MD}}(M_2).
\]

需要寻找的反例形状是：某个 grid 在 \(M_1\) 上达到局部最优，但其 \(M_2\) traffic 比该层单独下界高出固定因子；或者相反。若不存在小规模反例，再考虑构造嵌套 tile 的上界证明。

## 12. 小规模 processor-grid 枚举结果

对整数网格枚举 \(p_1p_2p_3=P\)，以

\[
S_A=\frac{n_1n_2}{p_1p_2},
\quad
S_B=\frac{n_2n_3}{p_2p_3},
\quad
S_D=\frac{n_1n_3}{p_1p_3}
\]

最小化 \(S_A+S_B+S_D\)，得到以下现象：

- 方阵 \((1024,1024,1024)\)、\(P=64\) 时，唯一最优平衡网格为 \((4,4,4)\)，三个工作块均为 \(65536\)。
- 矩形 \((1024,256,64)\)、\(P=64\) 时，最优整数网格为 \((16,4,1)\)，三个工作块均为 \(4096\)。这等价于按矩阵三个维度的比例分配 processor-grid 轴。
- 更瘦的矩形 \((4096,256,16)\) 在 \(P=16\) 时最优网格为 \((16,1,1)\)，说明小并行度和长宽比会把最优网格退化成 1D；随着 \(P\) 增大，再逐渐进入 2D 区域。

这与 2022 论文的三段式区域相符：小 \(P\) 时有单独投影约束，较大 \(P\) 时逐渐恢复近似立方的投影平衡。当前枚举还没有找到“同一层级的最小峰值空间网格与通信下界网格产生渐近冲突”的反例；它只覆盖整数、规则 3D grid 和静态块，不足以支持多级可组合性猜想。

枚举脚本位于 `work/enumerate_grids.py`。

## 13. 新的解析线索：processor-grid 优化与 KKT 三段式是同一个问题

对 processor grid，先忽略整数和 \(p_i\ge1\) 的边界。由

\[
p_1p_2p_3=P
\]

以及

\[
S_A=\frac{n_1n_2}{p_1p_2},
\quad
S_B=\frac{n_2n_3}{p_2p_3},
\quad
S_D=\frac{n_1n_3}{p_1p_3},
\]

可将总工作集写成

\[
S_A+S_B+S_D
=\frac{n_2n_3p_1+n_1n_3p_2+n_1n_2p_3}{P}.
\]

令 \(a=n_1,b=n_2,c=n_3\)。在约束 \(p_1p_2p_3=P\) 下，拉格朗日条件给出

\[
bc\,p_1=ac\,p_2=ab\,p_3=t.
\]

因此连续最优解为

\[
p_1^*=\left(\frac{a^2P}{bc}\right)^{1/3},
\qquad
p_2^*=\left(\frac{b^2P}{ac}\right)^{1/3},
\qquad
p_3^*=\left(\frac{c^2P}{ab}\right)^{1/3}.
\]

此时

\[
S_A=S_B=S_D
=\left(\frac{abc}{P}\right)^{2/3},
\]

总量为

\[
3\left(\frac{abc}{P}\right)^{2/3},
\]

正是 2022 下界的第三个区域。

当某个 \(p_i^*<1\) 时，必须把它固定为 1，再优化剩下两个维度；这会产生第二个区域。若第二个维度也触及 1，就得到第一个区域。于是：

- 2022 论文中的投影变量 \(x_i\) 可以解释为每个处理器的矩阵投影大小；
- 3D processor-grid 的 \(p_i\) 是达到这些投影的构造性参数；
- 三个 aspect-ratio 区域既来自 lower-bound KKT 的 active constraints，也来自 processor-grid 优化中的 \(p_i\ge1\) active constraints。

这说明一个可行的证明路线是：先把“连续 processor-grid 上界”完整推导出来，再证明整数网格 rounding 只引入可控的常数/边界误差。它可能成为把 2022 lower-bound proof 和 constructive algorithm proof 放在同一优化框架中的简化 lemma。

对例子 \((a,b,c)=(1024,256,64),P=64\)，公式给出

\[
(p_1^*,p_2^*,p_3^*)=(16,4,1),
\]

与整数枚举的最优网格一致。

## 14. 对多级问题的修正判断

这个解析结果暂时没有产生最小反例，反而显示：在规则 3D grid、静态块和单一工作集指标下，通信最优和峰值工作集最优往往由同一个 active-set 结构决定。因此，多级 gap 可能不在 processor-grid 本身，而在以下机制：

1. 同一个 3D grid 在不同内存层级需要不同的 tile 形状；
2. All-Gather/Reduce-Scatter 的通信库 buffer 破坏理想工作集估计；
3. packing 和 layout transform 在不同层级重复发生；
4. 非整除尺寸、任意处理器数和不规则边界使 rounding 误差累积；
5. latency 和 bandwidth 的最优 processor-grid 不一致。

下一步应把模型从“每处理器静态工作集”扩展到“嵌套 tile + 每级传输次数”，否则只能反复得到单级 2022 结构的不同写法。

## 15. 嵌套 tile 模型的第一版

把每个 processor 的 3D macro-subproblem 写成

\[
a=\frac{n_1}{p_1},qquad
b=\frac{n_2}{p_2},qquad
c=\frac{n_3}{p_3}.
\]

处理器间 3D algorithm 产生的主要 macro 工作集正好是

\[
H(p_1,p_2,p_3)=ab+bc+ac.
\]

处理器内部再用容量为 \(M_t\) 的 fast tier 做 \(a\times b\) 乘 \(b\times c\)。忽略边界和常数时，局部 tier 的 classical GEMM I/O 可写成

\[
Q_t^{\mathrm{local}}
=\Omega\left(ab+bc+ac+\frac{abc}{\sqrt{M_t}}\right).
\]

由于

\[
abc=\frac{n_1n_2n_3}{P},
\]

leading compute-dependent term

\[
\frac{abc}{\sqrt{M_t}}
=\frac{n_1n_2n_3}{P\sqrt{M_t}}
\]

与 processor-grid 的形状无关；而 scan/projection 项就是同一个 \(H(p)\)，也正是网络 3D grid 优化要最小化的量。

这给出一个暂时重要的正面结果：在理想化规则模型中，若每一级只看到相同的 macro-subproblem、没有额外 packing/replication 代价，那么各层级的 leading lower bound 可能是可组合的，且同一个连续最优 grid 同时最小化各级的形状项。

但是这个结论只覆盖“每个 processor 的 macro-subproblem 能够作为一个整体放在该层级的慢内存中”的情况。若

\[
M_t < H(p),
\]

就必须沿 \(b\) 或其他维度分 panel；此时：

- \(ab\) 和 \(bc\) 的 panel 会被重复读取；
- \(ac\) 的 partial output 需要保留或分批写回；
- 处理器间的 All-Gather/Reduce-Scatter 可能与 panel schedule 交错；
- 网络通信量不再只由一次 \(H(p)\) 决定。

因此真正的多级问题不是简单地把 \(M_t\) 代入
\(n_1n_2n_3/(P\sqrt{M_t})\)，而是证明当某一级无法容纳整个 macro-subproblem 时，panel 重复和跨层级同步的最小代价。

### 一个可继续证明的受限命题

若存在某个 processor grid \(p\) 使每一级慢内存都满足

\[
M_t\ge H(p)+O\left(\frac{n_1n_2n_3}{P\sqrt{M_{t-1}}}\right),
\]

则可以先在各 processor 之间完成一次 3D 数据分发，再在每个 processor 内递归执行局部 tiled GEMM；在这个受限模型中，网络层和本地层的 leading communication 可以分别按

\[
H(p),qquad
\frac{n_1n_2n_3}{P\sqrt{M_t}}
\]

核算。

这个命题的难点不是下界，而是证明一个具体 schedule 能同时满足所有层级的容量和生命周期约束。若条件失败，就进入真正的 panel/recompute/replication trade-off。

## 16. Macro-capacity 检查结果

对规则 3D grid，定义

\[
H(p)=\frac{n_1n_2}{p_1p_2}+\frac{n_2n_3}{p_2p_3}+\frac{n_1n_3}{p_1p_3}.
\]

对固定 \((n_1,n_2,n_3,P)\)，若本地慢内存 \(M_2\ge H_{\min}\)，至少存在一个 grid 能把一次 3D macro-subproblem 保存在该层级；若 \(M_2<H_{\min}\)，任何规则 3D grid 都必须 panelize 或重复分发。

小规模检查：

| dimensions | (P) | (H_{\min}) | 最优 grid |
|---|---:|---:|---|
| \((4096,4096,4096)\) | 64 | 3,145,728 | \((4,4,4)\) |
| \((1024,256,64)\) | 64 | 12,288 | \((16,4,1)\) |
| \((4096,256,16)\) | 16 | 73,728 | \((16,1,1)\) |

例如方阵 \(4096\)、\(P=64\) 时，\(M_2=2,359,296<H_{\min}\)，所以无法把 3D macro-subproblem 一次性保存在该层；这提供了一个明确的 panel/repetition 区域。检查脚本位于 `work/check_macro_capacity.py`。

这还没有给出 panel 区域的 tight bound，但把开放问题缩小为：在 \(M_2<H_{\min}\) 时，给定一个 active-set processor grid，沿哪一个迭代维度切 panel 才能最小化

\[
\text{重复的 }A/B\text{ 传输}
+\text{partial-}C\text{ 写回}
+\text{重新进行的 processor communication}?
\]

## 17. Panel 区域的修正模型

上一版把每个 panel 的 partial-\(C\) reduction 都算作一次处理器间通信，这个假设过强。若慢层能够保存完整的 partial output，partial-\(C\) 可以在本地跨 panel 累加，最后只做一次 Reduce-Scatter。因此普通 panelization 本身不会推出 \(a^3/t\) 的网络通信爆炸。

固定方形 processor macro-subproblem：

\[
A_0,B_0,C_0\in\mathbb{R}^{a\times a},
\qquad a=\frac{N}{P^{1/3}}.
\]

沿归约维切 panel 宽度 \(t\le a\)。每个 panel 需要

\[
A_{\mathrm{panel}}:a\times t,
\quad
B_{\mathrm{panel}}:t\times a,
\quad
C_{\mathrm{partial}}:a\times a.
\]

若

\[
a^2+2at\le M_2,
\]

则可以让 \(C_{\mathrm{partial}}\) 常驻慢层，在所有 \(a/t\) 个 panel 完成后再做一次归约。此时一个具体 3D schedule 的网络流量 leading term 约为

\[
Q_{\mathrm{net}}^{\mathrm{panel}}
\lesssim
\frac{a}{t}(2at)+a^2
=2a^2+a^2
=3a^2,
\]

与一次性 gather A/B、最后 reduce C 的量级相同；panel 宽度只改变本地慢层与更快层之间的流量。

本地更快层容量为 \(M_1\) 时，每个 panel 的局部 GEMM I/O leading term 约为

\[
\frac{2a^2t}{\sqrt{M_1}},
\]

乘以 \(a/t\) 个 panel 后得到

\[
Q_{M_1}^{\mathrm{local}}
\approx
\frac{2a^3}{\sqrt{M_1}},
\]

这与 panel 宽度在 leading term 上抵消。由此得到一个已修正的结论：

> 当 partial-\(C\) 能驻留在慢层时，panelization 主要改变层内 I/O，不必增加 processor-to-processor communication 的 leading term。

真正可能产生新的跨层级通信下界的区域是

\[
M_2<a^2,
\]

即连完整 partial output 都无法驻留。此时必须对输出维度也分块，或者把 partial sums 写回更慢层；若不同 processor 持有同一输出块的贡献，就可能需要多轮 reduction、recomputation 或额外 replication。

### 修正后的可证伪问题

在以下受限模型中寻找 lower bound：

- 不允许额外复制；
- 每个输出块的 partial sums 不能全部驻留在当前慢层；
- 每轮 reduction 只能合并当前驻留的输出 tile；
- 允许重新安排 A/B panel，但不允许用压缩编码表示 partial sums。

问题是是否必然有一个依赖于

\[
\frac{a^2}{M_2}
\]

的额外跨处理器 reduction 代价。当前不能把它写成 \(a^3/t\) 的定理；需要先精确定义 output tile 生命周期和 reduction 树。

这次修正推翻了上一版的一个过强候选，而把研究焦点收窄到“partial output 无法驻留”这一真正的边界。`work/panel_model.py` 已改为核对修正后的 schedule：当 partial-C 可驻留时，网络 leading term 保持为一次 gather 加一次 reduce；它不作为 lower-bound 证明。

## 18. 文献核查后的修正：多级内存并非从未研究

本轮进一步检索发现，不能把“多级矩阵乘法通信”整体称为未研究问题：

- Aggarwal–Alpern–Chandra–Snir 的 1987 Hierarchical Memory Model 已对多级内存中的矩阵乘法给出 tight upper/lower bounds，但它是单机 HMM，按内存访问代价函数建模，不是今天的 GPU + distributed-memory + topology-aware 模型。
- Vitter–Shriver 1994 的 parallel hierarchical multilevel memories 工作明确给出并行层次内存模型下矩阵乘法的 optimal algorithms；其模型是多个并行 memory hierarchies，在 base memory level 进行 hierarchy 间通信。
- Grigori–Jacquelin–Khabou 2013 的 HCP 工作把每层的 volume 和 messages lower bounds 推广到层次化平台，但主体算法是 LU/QR；论文当时明确指出，针对超过两级层次平台的算法和下界仍很少。

因此当前更准确的 gap 表述是：

> 经典 HMM 和早期 hierarchical-platform 研究已经证明了某些多级模型中的最优性；尚未核实是否存在一个同时覆盖现代 distributed-memory/GPU 层次、矩形 GEMM、tight constants、replication、latency 和实际 topology 的统一 theorem。

这也改变了本项目的研究策略：先把模型与 1987/1992 的 HMM/parallel-hierarchical 模型对照，再把 2022 的 aspect-ratio-aware parallel bound 放进去，确认我们研究的是模型扩展，而不是重复声称“第一个多级矩阵乘法下界”。

参考：

- [Aggarwal et al., A Model for Hierarchical Memory (1987)](https://doi.org/10.1145/28395.28428)
- [Vitter–Shriver, Algorithms for Parallel Memory II: technical report (1992); journal version (1994)](https://cs.brown.edu/research/pubs/techreports/reports/CS-92-05.html)
- [Grigori–Jacquelin–Khabou, Multilevel communication optimal LU and QR (2013)](https://arxiv.org/abs/1303.5837)
- [HCP paper full text and per-level lower-bound model](https://eprints.maths.manchester.ac.uk/2122/1/isc_camera_ready.pdf)

## 19. HCP 与 2022 单层模型的对齐

HCP 模型的关键参数是：

- 每层的子节点数为 \(P_i\)，从第 \(i\) 层向上的节点数为
  \[
  P_i^*=\prod_{j=i}^{L}P_j;
  \]
- 第 \(i\) 层一个 compute node 的聚合内存为
  \[
  M_i=M_1\prod_{j=1}^{i-1}P_j;
  \]
- 第 \(i\) 层通信 volume 为 \(W_i\)，message count 为 \(S_i\)，aggregation capacity 为 \(\phi_i\)；
- 在 regular communication pattern 下，不同层的 volume 满足论文中的递推关系，且高层消息由低层节点聚合后发送。

HCP 给出的抽象 lower-bound 形式是

\[
W_i=\Omega\left(\frac{\#\mathrm{flops}}{\sqrt{M_i}}\right),
\qquad
S_i=\Omega\left(\frac{W_i}{\phi_i}\right).
\]

它的优点是能表达 NUMA、node、drawer、network 等层级及 message aggregation；限制是论文中的具体矩阵乘法表达主要使用单层几何 bound 的推广，未给出 2022 那种对任意矩形 aspect ratio 的三段 tight constants。

2022 模型则假设：

- 总共有 \(P\) 个处理器；
- fully connected network；
- 关注 critical-path words；
- 本地内存可视作无限大以得到 memory-independent bound；
- 输入和输出各只有一份；
- 通过 Loomis–Whitney + 单矩阵访问约束，得到三段式 \(D(m,n,k,P)\)。

因此，不能直接把 HCP 的

\[
\Omega\left(\frac{\#\mathrm{flops}}{\sqrt{M_i}}\right)
\]

当成 2022 的 memory-independent bound。对方阵，前者在 \(M_i\approx n^2/P_i^*\) 时给出约 \(n^2/\sqrt{P_i^*}\) 的 2D 型尺度；而 2022 的大并行 memory-independent 项是

\[
3\frac{n^2}{(P_i^*)^{2/3}},
\]

对应 3D iteration-space partition。二者描述的是不同内存/复制假设下的边界。

### 统一定理的候选形态

把第 \(i\) 层视为拥有 \(P_i^*\) 个参与者、每个参与者聚合内存 \(M_i\) 的 macro-machine。对矩形 GEMM，可以尝试证明 per-level critical-path volume 满足

\[
W_i\ge
\max\left\{
\frac{2n_1n_2n_3}{P_i^*\sqrt{M_i}},
D(n_1,n_2,n_3,P_i^*)-
\frac{n_1n_2+n_2n_3+n_1n_3}{P_i^*}
\right\},
\]

并将 message lower bound 写为

\[
S_i\ge \frac{W_i}{\phi_i}.
\]

这只是候选形式。要变成 theorem，必须补充：

1. 第 \(i\) 层的输入/输出副本如何计数；
2. \(W_i) 是每个 level-(i\) node 的 critical path volume，还是该层总 volume；
3. replication 是否允许跨 level；
4. HCP 的 aggregation relation 是否保持在 3D replication 和 Reduce-Scatter 下；
5. 不同层的 lower bounds 能否由同一个 recursive schedule 同时达到。

### 方阵两级 sanity check

若只看一个外层级别、\(P_i^*=P\)，并令

\[
M_i=\Theta\left(\frac{n^2}{P}\right),
\]

memory-dependent 项为

\[
\Theta\left(\frac{n^3}{P\sqrt{n^2/P}}\right)
=\Theta\left(\frac{n^2}{\sqrt P}\right),
\]

这与经典 2D distributed-memory communication scale 一致。若允许足够 replication，使 3D memory-independent regime 生效，则候选第二项为

\[
\Theta\left(\frac{n^2}{P^{2/3}}\right).
\]

所以同一层的选择不是“公式冲突”，而是由 \(M_i\)、复制和初始/最终数据布局决定属于 2D memory-dependent 还是 3D memory-independent regime。

HCP 文献来源：

- [HCP model definitions and hierarchy parameters](https://eprints.maths.manchester.ac.uk/2122/1/isc_camera_ready.pdf)
- [HCP per-level volume/message lower bounds](https://eprints.maths.manchester.ac.uk/2122/1/isc_camera_ready.pdf)
- [2022 rectangular memory-independent bound](https://arxiv.org/html/2205.13407v1)

## 20. 再次收窄 gap：递归多级 GEMM 已有经典基线

进一步核对通信最优线性代数文献后，发现“递归 tiling 同时适配多个内存层级”本身不是新的观察：

- 对 sequential matrix multiplication，把每一级内存切成 fast/slow 两部分，分别应用两级下界；递归 blocked multiplication 可以同时达到各相邻层级的 bandwidth lower bounds。
- 类似的递归思想也被用于 hierarchical parallel processors：每个大节点内部再视为一个并行处理器，继续递归分解。这个方向在通信最优 Cholesky/QR/LU 文献中已经被作为层次化算法基线讨论。
- 因此，本项目如果只证明“递归 tiling 在多级内存中达到每级 \(\Theta(\mathrm{flops}/\sqrt{M_i})\)”，理论新颖性会很弱。

当前更窄、也更可能有价值的问题是：

1. **矩形 tight constants**：把 2022 年按 \(m,n,k,P\) 分三段的 memory-independent constants 推到每一个 HCP level，而不是只保留 \(\Theta\) 阶。
2. **3D replication + hierarchy aggregation**：同时允许每层不同的 replication factor 和 aggregation capacity \(\phi_i\)，证明 per-level volume/message lower bounds 以及同一 recursive schedule 的 tightness。
3. **任意层级处理器数**：处理 \(P_i\) 不整除矩阵维度、active-set 从 3D 退化到 2D/1D、以及整数 grid rounding 对 leading constant 的影响。
4. **异构 GPU/CPU 层级**：HCP 原始模型明确抽象掉了 GPU/multi-GPU 异构处理单元；需要新的计算/通信模型才能讨论 HBM、shared memory、register fragment、NVLink/PCIe 的联合 bound。

### 已知基线与拟研究对象

| 对象 | 已有状态 | 本项目可研究的增量 |
|---|---|---|
| 顺序多级 GEMM | 递归 blocked tiling 已有经典最优性基线 | 重新核对常数、layout 和 latency 细节 |
| 单层矩形 parallel GEMM | 2022 tight memory-independent constants | 作为每级 theorem 的核心组件 |
| 层次化 LU/QR | HCP 与 ML-CAQR/ML-CALU 有 per-level model/algorithms | 将相同结构转回 GEMM，并补齐矩形/3D replication |
| 现代 GPU 多级 tiling | 大量工程优化论文，但通常没有 universal lower bound | 建立可验证的 hardware-aware model |
| HCP + 2022 的统一 | 尚未在已检索文献中看到完整的 rectangular tight-constant theorem | 当前最清晰的理论切口 |

参考入口：

- [Communication-optimal parallel and sequential Cholesky decomposition](https://arxiv.org/abs/0902.2537)
- [Communication-optimal recursive algorithms / CARMA technical report](https://www2.eecs.berkeley.edu/Pubs/TechRpts/2012/EECS-2012-205.pdf)
- [HCP hierarchical platform model](https://eprints.maths.manchester.ac.uk/2122/1/isc_camera_ready.pdf)
- [2022 tight rectangular parallel lower bounds](https://arxiv.org/abs/2205.13407)

## 21. HCP 数值 sanity check

取一个三层示例：每个 node 有 8 个 core，每个 drawer 有 8 个 node，共 8 个 drawer；因此

\[
(P_1,P_2,P_3)=(8,8,8),
\qquad
(P_1^*,P_2^*,P_3^*)=(512,64,8).
\]

若每个 core 的本地内存为 \(M_1=32768\) words，则 HCP 聚合内存为

\[
(M_1,M_2,M_3)=(32768,262144,2097152).
\]

把 2022 方阵 leading terms 作为候选 per-level bound：

\[
Q_{\mathrm{MD},i}=\frac{2N^3}{P_i^*\sqrt{M_i}},
\qquad
Q_{\mathrm{MI},i}=3\frac{N^2}{(P_i^*)^{2/3}},
\]

对 \(N=4096\) 得到：

| level | \(P_i^*\) | \(M_i\) | MD candidate | MI candidate | 较大项 |
|---:|---:|---:|---:|---:|---|
| 1 | 512 | 32,768 | 1,482,910 | 786,432 | MD |
| 2 | 64 | 262,144 | 4,194,304 | 3,145,728 | MD |
| 3 | 8 | 2,097,152 | 11,863,283 | 12,582,912 | MI |

这些数值只用于检查量纲和 regime 转换：它们是每个相应层级 node 的 critical-path 候选量，不是把各层直接相加后的总通信量。真正的 HCP 成本还要乘上该层的 \(\beta_i\)，并用 \(\phi_i\) 将 volume 转换为 message count。

脚本位于 `work/hcp_bound_sanity.py`。

## 22. 层级间 active-set 转换：同一个 GEMM 在不同层次不一定处于同一维度区域

为了把上一节的方阵 sanity check 推到矩形情形，取

\[
(m,n,k)=(4096,1024,256),
\qquad
(P_1^*,P_2^*,P_3^*)=(512,64,8),
\]

并令各层聚合内存为

\[
(M_1,M_2,M_3)=(32768,262144,2097152).
\]

这个矩形问题的两个分界点是

\[
\frac mn=4,
\qquad
\frac{mn}{k^2}=64.
\]

将 2022 年矩形 memory-independent 候选式逐层代入，得到：

| level | \(P_i^*\) | active region | \(D_i\) | \(D_i-\mathrm{compulsory}_i\) | \(2mnk/(P_i^*\sqrt{M_i})\) |
|---:|---:|:---:|---:|---:|---:|
| 1 | 512 | 3D | 49,152 | 38,400 | 23,170 |
| 2 | 64 | 2D/3D boundary | 196,608 | 110,592 | 65,536 |
| 3 | 8 | 2D | 895,016 | 206,888 | 185,364 |

这里的 \(D_i\) 是最小总数据访问量候选值，减去 compulsory input/output 项后才是通信量候选值。对每一层，如果暂时把 memory-dependent 与 memory-independent 两种来源都纳入，候选 leading volume 可以写成

\[
\widehat Q_i
 =
 \max\left\{
 \frac{2mnk}{P_i^*\sqrt{M_i}},
 D_i-\frac{mn+mk+nk}{P_i^*}
 \right\}.
\]

这张表暴露出一个比单层公式更具体的层级问题：最内层已经在 3D 区域，中间层处在 2D/3D 分界点，最外层则退化为 2D。因而不能假定一个固定的三维 processor grid 在每个层级都保持同样的 active set。递归算法需要在层级边界上处理至少一种变化：

1. 改变每一级的有效 replication/grid factor；
2. 让某个维度在外层退化为 1，并在内层重新展开；
3. 或证明一次固定布局虽然不是每一级的局部最优，却仍能在 HCP 的加权总成本下达到同阶甚至 tight constant。

这也是把单层 2022 定理直接“逐层套用”时必须补上的兼容性条件。逐层取最大值并不能自动推出一个可实现的多层算法，因为各层可能要求不同的数据复制和归约路径。

### 分界点连续性检查

在 \(P=m/n=4\) 处，1D 和 2D 表达式都给出

\[
D=1{,}572{,}864,
\qquad
D-\mathrm{compulsory}=196{,}608.
\]

在 \(P=mn/k^2=64\) 处，2D 和 3D 表达式都给出

\[
D=196{,}608,
\qquad
D-\mathrm{compulsory}=110{,}592.
\]

因此分段式本身在两个 active-set 边界连续；真正尚未解决的是：当不同 HCP 层级跨过这些边界时，是否存在一个同时满足各层数据布局、复制限制、归约容量和消息聚合限制的 schedule。

复现实验脚本为 `work/level_bound_compare.py`。它只做公式代入、边界连续性和 regime 标注，不把候选式误写成已经证明的 HCP tight theorem。

## 23. 近年文献更新：紧下界继续向结构化 kernel 和联合通信扩展

截至 2026 年 10 月，检索到的最直接后续进展主要不是重新替代 2022 年的通用矩形 GEMM theorem，而是把“下界 + 达界算法”的方法扩展到更具体的 kernel 或更丰富的通信模型。

### 23.1 2024：对称矩阵计算的并行紧下界

Al Daas、Ballard、Grigori、Kumar、Rouse 和 Verite 的 2024 论文研究了三个 BLAS-3 对称 kernel：

- SYRK：\(AA^T\)；
- SYR2K：\(AB^T+BA^T\)；
- SYMM：一个输入矩阵具有对称结构的矩阵乘法。

论文在 sequential 和 distributed-memory parallel 两种模型中都给出通信下界，并构造达到下界的算法。证明不再直接使用普通 GEMM 的三面 Loomis--Whitney 计数，而是使用适合对称访问的几何不等式，再解带约束的非线性优化问题；算法则采用三角块划分。

这说明 2022 年之后“紧下界”的推进方向之一，是为结构化计算 DAG 重新计算可达工作量，而不是只把普通 GEMM 的结果换一个符号。对本项目最有用的启发是：如果 HCP 层级中的某一层利用对称性、三角存储或 fused update，普通 GEMM 的 \(D(m,n,k,P)\) 不能直接当作该层的 tight bound。

来源：[Communication Lower Bounds and Optimal Algorithms for Symmetric Matrix Computations](https://arxiv.org/abs/2409.11304)。

### 23.2 2025：非对称内存下的 horizontal + vertical 联合下界

Zhu、Hua 和 Jin 的 2025 论文研究 distributed-memory parallel model 中的 asymmetric memory，并把两类代价放在同一个目标里：

- horizontal communication：处理器之间的数据移动；
- vertical communication：主存与 cache/本地内存层之间的数据移动。

论文指出，在 read-write 对称内存中，可以直接组合水平通信最优与垂直通信最优的算法；在 NVM 一类读写代价不对称的模型中，两者不能同时最优，于是作者给出 joint-communication lower bound 和达到它的 JOMMA 算法。这个结果与当前 HCP 方向很接近，但目标函数仍是特定的联合成本，并不等价于已经解决了任意 \(L\)-level HCP 的 per-level volume/message tightness。

来源：[Joint-Communication Optimal Matrix Multiplication with Asymmetric Memories](https://doi.org/10.1007/s11390-023-3489-y)。该文发表于 *Journal of Computer Science and Technology* 40(3), 2025, pp. 835--854。

### 23.3 2026 的邻近进展：下界作为其他并行算法的标尺

2026 年的并行 Jacobi/SVD 工作把 2D 与 2.5D 矩阵乘法的带宽/延迟下界作为对照，研究一个更复杂的迭代算法能否同时达到这些标尺。它不是新的 GEMM 下界定理，但显示出当前研究问题已经从“是否存在 GEMM 下界”转向“不同算法的多个通信目标能否同时达到”。这与本日志中的 HCP 问题完全同构：volume、message、latency 和 arithmetic work 可能要求不同的布局。 来源：[Minimizing the Arithmetic and Communication Complexity of Jacobi's Method: Part Two -- Parallel Algorithms](https://arxiv.org/abs/2608.28952)。

### 23.4 当前 gap 的更准确表述

因此，现在不应把研究问题写成“证明并行矩阵乘法的第一个多层下界”。更准确的表述是：

> 在任意矩形 \(m\times n\) 乘 \(n\times k\)、层级处理器乘积 \(P_i^*\)、层级聚合内存 \(M_i\)、每层消息聚合容量 \(\phi_i\) 和可选复制约束下，是否能给出一个同时对每一级 volume 与 message 都 tight 的 HCP 定理，并构造一个跨 active-set 区域切换仍然可实现的统一 schedule？

这个问题需要至少同时处理：

1. 2022 矩形 GEMM 的 1D/2D/3D 分段常数；
2. HCP 每层的 \(M_i\)、\(P_i^*\)、\(\phi_i\) 与成本权重；
3. 不同层级可能处于不同 active set（上一节的数值例子）；
4. 复制、初始/最终布局和归约树之间的兼容性；
5. 如果 kernel 有对称、三角或 fused 结构，重新建立对应几何不等式。

## 24. 一个可实现性小实验：逐层最优 grid 是否可以嵌套

为了避免把“每层都有局部最优值”误当成“存在一个跨层 schedule”，我又做了一个有限枚举：对每个 \(P_i^*\) 枚举整数三维 grid

\[
p_{i,1}p_{i,2}p_{i,3}=P_i^*,
\]

以

\[
H_i=
\frac{mn}{p_{i,1}p_{i,2}}
 +\frac{nk}{p_{i,2}p_{i,3}}
 +\frac{mk}{p_{i,1}p_{i,3}}
\]

作为局部 3D macro-volume 指标，并额外要求外层 grid 的每个坐标整除内层对应坐标。对上一节的例子，枚举结果为：

| level | \(P_i^*\) | 局部最优 grid | \(H_i^{\min}\) |
|---:|---:|:---:|---:|
| 1 | 512 | \((32,8,2)\) | 49,152 |
| 2 | 64 | \((16,4,1)\) | 196,608 |
| 3 | 8 | \((4,2,1)\) 或 \((8,1,1)\) | 917,504 |

其中

\[
(32,8,2)\ \succeq\ (16,4,1)\ \succeq\ (4,2,1)
\]

逐坐标满足整除关系，因此这个例子存在“每一级局部最优且可嵌套”的 grid chain。对 \(m,n,k\) 取若干个 2 的幂、共 90 个满足 \(m\ge n\ge k\) 的矩形样例，在相同 \(P^*=(512,64,8)\) 下也没有找到 grid-level 的嵌套反例。

这个结果只能说明一个很窄的事实：在规则整数 grid 和 \(H_i\) 这个局部指标下，active-set 切换不必然破坏嵌套。它没有处理初始布局、复制内存、归约树、消息聚合、非整除尺寸，也没有证明 volume 与 message 同时达到下界。下一步应把搜索扩大到非 2 的幂尺寸和带 \(\phi_i\) 的归约成本；如果出现反例，它会比单纯的连续优化更直接地指出 theorem 需要增加的假设。

脚本为 `work/nested_grid_compatibility.py`。


## 25. 非 2 的幂尺寸的嵌套反例：局部最优 grid 不一定能同时实现

把上一节的枚举扩大到非 2 的幂矩阵尺寸后，找到了一个最小的诊断性反例。取

\[
(m,n,k)=(97,53,17),
\qquad
(P_1^*,P_2^*,P_3^*)=(120,24,6).
\]

对每一级单独最小化

\[
H_i=
\frac{mn}{p_{i,1}p_{i,2}}
+\frac{nk}{p_{i,2}p_{i,3}}
+\frac{mk}{p_{i,1}p_{i,3}},
\qquad
p_{i,1}p_{i,2}p_{i,3}=P_i^*,
\]

得到唯一的局部最优 grid：

| level | \(P_i^*\) | 独立最优 grid | \(H_i^{\min}\) |
|---:|---:|:---:|---:|
| 1 | 120 | \((10,6,2)\) | 243.217 |
| 2 | 24 | \((6,4,1)\) | 714.292 |
| 3 | 6 | \((3,2,1)\) | 1,857.000 |

但是 \(6,4,1\) 不是 \(10,6,2\) 的逐坐标因子，因此三个独立最优 grid 不能组成嵌套链。仍然存在 162 条可嵌套链；其中按 \(\sum_i H_i\) 最好的链是

\[
(6,4,5)\ \succeq\ (6,4,1)\ \succeq\ (3,2,1),
\]

其总 \(H\) 为 2885.517，而逐层独立最优值之和为 2814.508，局部指标的额外开销约为

\[
\frac{2885.517}{2814.508}-1\approx 2.52\%.
\]

这个例子改变了上一节的判断：active-set 转换并不只是理论上的可能困难；即使只看整数 grid 和最简单的宏块访问量，也可能出现“每层局部最优不可同时实现”的离散不相容性。代价目前只有 \(2.52\%\)，不能据此声称存在普适的常数损失界；它只是说明整数 rounding 和嵌套约束必须进入正式定理。

为了把消息维度也放进记录，给三层设置一个仅用于诊断的聚合容量

\[
(\phi_1,\phi_2,\phi_3)=(16,8,4)\quad\text{words/message}.
\]

用 2022 矩形 memory-independent 候选通信量 \(Q_i\) 计算 \(Q_i/\phi_i\)，三层分别处于 3D、3D、2D 区域，并得到：

| level | region | \(Q_i\) candidate | \(\phi_i\) | \(Q_i/\phi_i\) candidate |
|---:|:---:|---:|---:|---:|
| 1 | 3D | 178.755 | 16 | 11.172 |
| 2 | 3D | 389.628 | 8 | 48.704 |
| 3 | 2D | 570.238 | 4 | 142.560 |

这里的 \(Q_i/\phi_i\) 只是把 volume 下界转换为 message-count 下界的模型检查，不是对具体归约实现的精确消息计数。它说明即使 volume 的 grid rounding 开销很小，外层层级的 message 约束仍可能成为主导项；因此正式目标应至少同时优化

\[
\text{volume},
\qquad
\text{messages}=\text{volume}/\phi_i,
\qquad
\text{nested-layout feasibility}.
\]

脚本为 `work/nested_grid_counterexample.py`。下一步应搜索：非整除矩阵尺寸、不同 \(\phi_i\) 比例，以及允许某一级使用非局部最优 grid 后，是否能在加权 volume/message 目标下得到更好的全局嵌套 schedule。


## 26. volume 与 message-sensitive 目标会选择不同的嵌套 schedule

在上一节的非幂次反例上，进一步把 \(H_i\) 当作一次 3D collective 的 per-process volume proxy，并定义一个仅用于诊断的加权目标：

\[
J(\mathcal G)
=
\sum_i w_i H_i(g_i)
+
\sum_i \mu_i\frac{H_i(g_i)}{\phi_i}.
\]

其中 \(g_i\) 是第 \(i\) 层的 grid，\(\phi_i\) 是可聚合的 words/message；真实实现还会有 collective tree、同步和拓扑项，因此 \(J\) 不是一个已证明的 HCP 成本函数。

对

\[
(m,n,k)=(97,53,17),
\qquad
(P_1^*,P_2^*,P_3^*)=(120,24,6),
\]

所有 162 条嵌套链中，单纯最小化总 volume 的选择是

\[
\mathcal G_{\mathrm{vol}}
=
((6,4,5),(6,4,1),(3,2,1)),
\]

其三层 \(H_i\) 为

\[
(314.225,\ 714.292,\ 1857.000),
\qquad
\sum_i H_i=2885.517.
\]

现在设置中间层的聚合容量较差：

\[
(\phi_1,\phi_2,\phi_3)=(1,2,1),
\qquad
w_i=0,
\qquad
\mu_i=1.
\]

此时最优嵌套链变成

\[
\mathcal G_{\mathrm{msg}}
=
((15,4,2),(3,4,2),(3,2,1)),
\]

对应

\[
H_i=(253.275,\ 815.875,\ 1857.000),
\qquad
\sum_i H_i/\phi_i=2518.213.
\]

volume-optimal 链的相同 message proxy 为 2528.371，因此 message-sensitive 选择虽然增加了总 volume（2926.150 对比 2885.517），却降低了聚合受限的目标。

这个小实验给出一个更具体的研究警告：如果 theorem 只优化 words，那么它可能选择一个在 message/latency 模型下并不优的 nested grid；反过来，若优先压低 message count，也可能牺牲 volume。因而多层 tightness 更自然的形式不是一个单标量公式，而是一个带

\[
(\text{volume},\ \text{messages},\ \text{latency},\ \text{layout-feasibility})
\]

约束的 Pareto lower-bound 或多目标定理。

脚本为 `work/weighted_nested_schedule.py`。它当前明确把 \(H_i/\phi_i\) 标为 proxy，并没有把该诊断升级为真实消息复杂度结论。


## 27. 嵌套约束的 overhead 可能明显大于前一个例子

为了避免把前一节的 \(2.52\%\) 误解成普遍现象，又固定搜索了另一组非幂次实例：

\[
(m,n,k)=(385,69,69),
\qquad
(P_1^*,P_2^*,P_3^*)=(132,66,6).
\]

逐层独立优化得到：

| level | \(P_i^*\) | 独立最优 grid | \(H_i^{\min}\) |
|---:|---:|:---:|---:|
| 1 | 132 | \((22,2,3)\) 或 \((22,3,2)\) | 1,799.750 |
| 2 | 66 | \((11,2,3)\) 或 \((11,3,2)\) | 2,806.000 |
| 3 | 6 | \((6,1,1)\) | 13,616.000 |

独立最优值之和是 18,221.750。81 条可嵌套链中，最优的一条为

\[
(33,2,2)
\succeq
(33,1,2)
\succeq
(3,1,2),
\]

其总 \(H=21,246.250\)，相对独立最优值的 overhead 为

\[
\frac{21,246.250}{18,221.750}-1
\approx 16.60\%.
\]

这仍然不是 universal lower bound，只是一个可重复的 witness。但它已经足以否定“grid rounding 只产生很小常数损失”的未经证明假设。正式研究需要回答：

1. overhead 是否存在只依赖 processor hierarchy 的上界；
2. 它是否随矩阵 aspect ratio、层级数量或 \(P_i/P_{i+1}\) 增长；
3. 允许非局部最优 grid 后，volume/message 的 Pareto frontier 是否仍有可证明的常数近似。

复现实验脚本为 `work/search_nested_overhead.py`。


## 28. 固定 hierarchy 下的 aspect-ratio 扫描

为了区分“某个尺寸 witness”与“aspect ratio 的系统性效应”，把三个矩阵乘积写成

\[
x=mn,
\qquad z=mk,
\qquad y=nk.
\]

在 \(m\ge n\ge k\) 下有 \(x\ge z\ge y>0\)。对固定 grid \(g=(p_1,p_2,p_3)\)，宏块通信 proxy 是线性的：

\[
H_g
=
\frac{x}{p_1p_2}
+
\frac{z}{p_1p_3}
+
\frac{y}{p_2p_3}.
\]

因此可以令 \(x=1\)，在二维区域

\[
1\ge z/x\ge y/x>0
\]

上扫描嵌套最优值与逐层独立最优值的比值，而不必枚举所有实际矩阵尺寸。

对 hierarchy

\[
(P_1^*,P_2^*,P_3^*)=(132,66,6)
\]

进行 250×250 网格扫描，得到的最大观测比值为约

\[
1.17875,
\qquad
(z/x,y/x)\approx(1,0.152).
\]

这个区域对应 \(n\approx k\)，而 \(m\) 大约是 \(6.6n\)。取整数 witness

\[
(m,n,k)=(657,100,100),
\]

得到

\[
\frac{H_{\mathrm{nested}}}{H_{\mathrm{independent}}}
\approx 1.17865,
\]

最优嵌套链仍是

\[
(33,2,2)
\succeq
(33,1,2)
\succeq
(3,1,2).
\]

这给出两个研究线索：

1. overhead 的极值可能集中在 \(x\approx z\) 或 \(z\approx y\) 这样的 aspect-ratio 边界，而不是一般内部点；
2. 对固定 processor hierarchy，\(H_g\) 是 \(x,z,y\) 的线性函数，独立最优和嵌套最优都是有限个线性函数的下包络。因而可以尝试把 overhead 上界化约为有限个 polyhedral region 上的线性分式优化，而不是依赖随机尺寸实验。

当前扫描是数值证据，不是 supremum 证明；网格分辨率为 0.004，且只针对一个 hierarchy。脚本为 `work/scan_aspect_ratio_overhead.py`。


## 29. 一个精确的 overhead witness：(303/257)

上一节的扫描在 \(z/x=1\) 附近出现峰值。令

\[
z/x=1,
\qquad t=y/x.
\]

在 \(t\approx 5/33\) 的邻域，逐层独立最优 grid 的候选值为

\[
(22,2,3),
\qquad
(11,2,3),
\qquad
(6,1,1),
\]

其中前两个 grid 的两个末维交换版本具有相同值。对应的独立总 volume proxy 是

\[
I(t)=
\left(\frac{5}{132}+\frac{t}{6}\right)
+\left(\frac{5}{66}+\frac{t}{6}\right)
+\left(\frac13+t\right)
=
\frac{59}{132}+\frac{4t}{3}.
\]

两条竞争性的嵌套链为

\[
\mathcal G_A=((33,2,2),(33,1,2),(3,1,2)),
\]

和

\[
\mathcal G_B=((66,1,2),(66,1,1),(6,1,1)).
\]

它们的 proxy 分别为

\[
A(t)=\frac{19}{33}+\frac{5t}{4},
\qquad
B(t)=\frac{17}{44}+\frac{5t}{2}.
\]

解 \(A(t)=B(t)\) 得到

\[
t=\frac{5}{33}.
\]

在这个交叉点，穷举所有整数 grid 后确认独立最优和嵌套最优分别为

\[
I\left(\frac{5}{33}\right)=\frac{257}{396},
\qquad
A\left(\frac{5}{33}\right)=\frac{101}{132},
\]

所以 overhead 精确为

\[
\frac{A(5/33)}{I(5/33)}
=
\frac{303}{257}
\approx 1.178988.
\]

这个 aspect ratio 可以由整数矩阵

\[
(m,n,k)=(660,100,100)
\]

精确实现，因为 \(z/x=k/n=1\)，\(y/x=k/m=5/33\)。该实例的最优嵌套链是 \(\mathcal G_A\)，独立最优值与嵌套最优值的比值正好为 \(303/257\)。

这仍然不是对固定 hierarchy 的全局 supremum 证明，但它把数值观察提升成了一个精确的有限枚举 witness，并指出 overhead 峰值可能来自两个不同嵌套 active set 的交叉。下一步可以沿同一方法枚举所有候选链的线性函数，尝试求出固定 hierarchy 的 exact piecewise-rational upper envelope。

脚本为 `work/exact_aspect_ratio_witness.py`。


## 30. \(z/x=1\) 边界上的 exact envelope 已经可以求完

为了验证上一节的精确 witness 不是边界上的局部峰值，我对固定 hierarchy

\[
(P_1^*,P_2^*,P_3^*)=(132,66,6)
\]

完整枚举了：

- 每一级所有整数 grid 的线性函数 \(a+bt\)；
- 所有满足逐坐标整除的嵌套 chain；
- \(t=y/x\in[0,1]\) 上所有两两交点。

在 \(z/x=1\) 时，每一个 grid 的 proxy 都是 \(a+bt\)，因此 independent envelope 和 nested envelope 在每个 breakpoint 区间内都是 affine 函数。两个 affine 函数之比在区间内单调，所以只需检查所有 breakpoint 端点即可得到精确最大值。

枚举结果：

| 项目 | 结果 |
|---|---:|
| 嵌套 chain 数 | 81 |
| breakpoint 数 | 300 |
| 区间数 | 299 |
| 边界上的最大 overhead | \(303/257\approx1.178988\) |
| 最大点 | \(t=5/33\) |

因此，\(303/257\) 是该 hierarchy 在 \(z/x=1\) 这条边界上的 exact maximum，而不只是一个抽样 witness。最大点左右两侧的 active nested line 分别是

\[
B(t)=\frac{17}{44}+\frac{5t}{2},
\qquad
A(t)=\frac{19}{33}+\frac{5t}{4},
\]

它们在 \(t=5/33\) 交叉；independent envelope 在这一带保持

\[
I(t)=\frac{59}{132}+\frac{4t}{3}.
\]

这给出了一个可推广的证明模板：对固定 processor hierarchy，将二维 aspect-ratio domain 划分成有限个 polyhedral cells，在每个 cell 中确定 independent/nested 的 active linear functions，再对线性分式求极值。当前只完成了 \(z/x=1\) 的一维边界，完整二维 exact envelope 仍待处理。

脚本为 `work/exact_boundary_envelope.py`。


## 31. 固定 hierarchy 的完整二维 aspect-ratio 域：最大值仍为 \(303/257\)

进一步对归一化域

\[
\mathcal D=\{(z,y):0\le y\le z\le1\}
\]

做了完整的二维 exact arrangement。这里 \(x=mn\) 被归一化为 1，\(z=mk/x\)，\(y=nk/x\)。步骤是：

1. 对每个 independent level 的每个 grid，精确检查其 lower-envelope 区域是否与 \(\mathcal D\) 相交；
2. 对所有嵌套 chain 做同样的半平面可行性检查；
3. 只保留实际可能 active 的 affine lines；
4. 枚举这些 equality lines 与三角域边界的所有交点；
5. 在每个 arrangement vertex 上计算
   \[
   R(z,y)=\frac{N(z,y)}{I(z,y)},
   \]
   其中 \(I\) 是逐层 independent lower envelope，\(N\) 是 nested lower envelope。

每个 cell 内 \(I,N\) 都是 affine 函数，而正分母下的线性分式在多面体上的极值出现在顶点，因此这一步对固定 hierarchy 是有限的 exact 搜索。

对

\[
(P_1^*,P_2^*,P_3^*)=(132,66,6)
\]

得到：

| 项目 | 结果 |
|---|---:|
| 嵌套 chain 数 | 81 |
| 实际可能 active 的 independent lines | \(24,16,8\) |
| 实际可能 active 的 nested lines | 32 |
| equality lines | 920 |
| 三角域 arrangement vertices | 76,391 |
| 完整二维域最大 overhead | \(303/257\approx1.178988\) |
| 最大点 | \((z,y)=(1,5/33)\) |

因此，对于这个固定 hierarchy，\(303/257\) 不只是 \(z/x=1\) 边界上的最大值，也是整个二维 aspect-ratio 域的最大值。换句话说，当前 witness 已经排除了该 hierarchy 下所有其他连续 aspect ratio 的更大 overhead。

这还没有给出任意 hierarchy 的 universal bound；但它提供了一个可推广的实验/证明框架：先对每个 hierarchy 做 exact active-line pruning，再把最大值问题化成有限个 arrangement vertices 上的线性分式比较。

脚本为 `work/exact_2d_pruned.py`。完整运行约需几十秒，结果已用 exact rational arithmetic 验证。


## 32. 三组 hierarchy 的完整二维 exact 结果

将 `exact_2d_pruned.py` 参数化后，又对两个不同的 processor hierarchy 完成了同样的二维 exact arrangement。结果都把最大值定位在 `z=1` 边界，但 overhead 数值不同：

| hierarchy $P^*$ | nested chains | arrangement vertices | exact maximum | maximizer $(z,y)$ |
|---|---:|---:|---:|---:|
| $(132,66,6)$ | 81 | 76,391 | $303/257\approx1.178988$ | $(1,5/33)$ |
| $(56,28,4)$ | 54 | 16,515 | $345/302\approx1.142384$ | $(1,17/70)$ |
| $(210,42,6)$ | 81 | 129,618 | $978/877\approx1.115165$ | $(1,1/6)$ |

例如第二组 hierarchy 的 exact optimum 为

$$
I=\frac{151}{140},
\qquad
N=\frac{69}{56},
\qquad
\frac{N}{I}=\frac{345}{302}.
$$

第三组则为

$$
I=\frac{877}{1260},
\qquad
N=\frac{163}{210},
\qquad
\frac{N}{I}=\frac{978}{877}.
$$

这些结果暂时支持两个判断：

1. 嵌套 rounding overhead 不是由单一 universal 常数描述的；它依赖 processor hierarchy 的因子结构。
2. 在目前测试的 hierarchy 中，最大值都落在 `z=1`（即 $n=k$）边界，但这只是三个实例的证据，不能推广成定理。

脚本现在支持 `--pstars p1 p2 p3` 参数，可复用同一套 exact active-line pruning 和 arrangement 搜索。


## 33. 更大的 hierarchy-dependent witness：\(537/449\)

在结构化扫描中，继续扩大 processor hierarchy 的因子范围后，边界候选超过了 \(303/257\)。hierarchy

$$
(P_1^*,P_2^*,P_3^*)=(351,117,9)
$$

的因子比例是

$$
P_1^*/P_2^*=3,
qquad
P_2^*/P_3^*=13.
$$

对这个 hierarchy 做完整二维 exact arrangement，得到：

| 项目 | 结果 |
|---|---:|
| 嵌套 chain 数 | 54 |
| 实际 active independent lines | \(16,10,5\) |
| 实际 active nested lines | 25 |
| equality lines | 475 |
| arrangement vertices | 19,729 |
| 全二维域最大 overhead | \(537/449\approx1.195991\) |
| 最大点 | \((z,y)=(1,1/9)\) |

最大点的 exact lower-envelope 值为

$$
I=\frac{449}{1053},
qquad
N=\frac{179}{351},
qquad
\frac{N}{I}=\frac{537}{449}.
$$

它可以由整数矩阵尺寸

$$
(m,n,k)=(81,9,9)
$$

实现，因为 \(z/x=k/n=1\)，\(y/x=k/m=1/9\)。

作为对照，之前验证过的 hierarchy 给出：

| hierarchy | exact maximum |
|---|---:|
| \((132,66,6)\) | \(303/257\approx1.178988\) |
| \((56,28,4)\) | \(345/302\approx1.142384\) |
| \((210,42,6)\) | \(978/877\approx1.115165\) |
| \((351,117,9)\) | \(537/449\approx1.195991\) |

因此，当前证据更支持这样的表述：嵌套 grid overhead 由 processor hierarchy 的整数因子结构决定，尤其可能受到相邻层级比例（这里出现因子 13）的影响；还不能把它压缩成与 hierarchy 无关的固定常数。

批量发现脚本为 `work/scan_boundary_hierarchies.py`，完整二维验证仍使用 `work/exact_2d_pruned.py --pstars 351 117 9`。


## 34. 一个可能逼近 $117/85$ 的 hierarchy family

沿着 factor-13 witness 继续变化，考虑

$$
(P_1^*,P_2^*,P_3^*)=(27q,9q,9),
$$

其中 $q$ 是大于 3 的素数，并固定 aspect-ratio 点

$$
z=1,
qquad y=1/9.
$$

对 $q=29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101,127,149,199$ 的完整整数 grid 枚举都得到同一个有理函数：

$$
R(q)=\frac{117q+90}{85q+270}.
$$

例如：

| $q$ | exact ratio |
|---:|---:|
| 13 | $537/449\approx1.195991$ |
| 17 | $693/565\approx1.226549$ |
| 29 | $3483/2735\approx1.273492$ |
| 37 | $4419/3415\approx1.293997$ |
| 199 | $3339/2455\approx1.359674$ |

在 $q\ge29$ 的 active-line pattern 中，independent 三层选择为

$$
(q,3,9),
qquad
(q,3,3),
qquad
(9,1,1),
$$

而 nested 最优 chain 为

$$
(9,3,q)
\succeq
(9,1,q)
\succeq
(9,1,1).
$$

它们分别给出

$$
I(q)=\frac{85}{243}+\frac{10}{9q},
qquad
N(q)=\frac{13}{27}+\frac{10}{27q},
$$

从而

$$
\frac{N(q)}{I(q)}
=\frac{117q+90}{85q+270}
\longrightarrow
\frac{117}{85}\approx1.376471.
$$

对 $q=29$，完整二维 exact arrangement 仍然把最大值定位在 $(z,y)=(1,1/9)$，结果为 $3483/2735$。因此这不只是边界下界：至少在 $q=29$ 这个实例上，二维域的全局最大值也已验证。

目前需要谨慎表述：有限的素数测试和 active-line 公式支持一个渐近 family，但还没有完成“对所有素数 $q\ge29$ 的完整二维 universal proof”。如果该 family 的 active-line 不等式可以对所有 $q\ge29$ 证明，那么任何 hierarchy-independent 的 nested-grid constant overhead 上界都至少必须达到 $117/85$。

脚本为 `work/family_prime_q.py`；$q=29$ 的完整二维验证使用 `work/exact_2d_pruned.py --pstars 783 261 9`。


## 35. $q$-family 的 endpoint certificate：可严格推出 $117/85$ 下界

上一节的 family 不只是经验拟合。对素数 $q>3$，$27q$、$9q$ 和 9 的 divisor pattern 固定；在选定点 $(z=1,y=1/9)$ 上，每个 grid 的 proxy 都可以写成

$$
A+\frac{B}{q}.
$$

我对所有 independent grid 和所有嵌套 chain 做了符号枚举，并检查目标线与每个竞争线在两个端点

$$
q=29,
qquad q\to\infty
$$

上的比较。因为差值对 $1/q$ 是线性的，只要两个端点都满足，整个 $q\ge29$ 区间就满足。

检查结果：

- independent 三层目标线分别为
  $$
  \frac{1}{243}+\frac{4}{9q},
  \qquad
  \frac{1}{81}+\frac{2}{3q},
  \qquad
  \frac13;
  $$
- 对所有 independent 竞争 grid，端点不等式违反数为 0；
- nested 目标 chain
  $$
  (9,3,q)\succeq(9,1,q)\succeq(9,1,1)
  $$
  的总 proxy 为
  $$
  \frac{13}{27}+\frac{10}{27q};
  $$
- 对所有 nested 竞争 chain，端点不等式违反数也为 0。

因此，对每一个素数 $q\ge29$，在 $(z=1,y=1/9)$ 这个合法 aspect ratio 点上，至少有

$$
R(q)=\frac{117q+90}{85q+270}.
$$

令 $q\to\infty$，得到严格的 family lower-bound conclusion：如果有人试图证明一个对所有 processor hierarchies 都成立的 multiplicative nested-grid overhead 上界 $C$，那么必有

$$
C\ge\frac{117}{85}\approx1.376471.
$$

这里的结论是 universal upper bound 的必要条件，不声称 $117/85$ 本身就是 tight universal constant，也不声称每个 $q$ 的全二维最大值都必须位于 $(z=1,y=1/9)$。

脚本为 `work/prove_q_family.py`，输出显示 independent 和 nested 的 endpoint comparison violations 均为 0。


## 36. 更强的具体 family：$45/31$ 极限

固定

$$
(P_1^*,P_2^*,P_3^*)=(30q,15q,15),
$$

其中 $q$ 为素数，并取 aspect-ratio 点 $(z=1,y=1/15)$。对所有 $q\ge101$ 的竞争线做 endpoint certificate，目标 independent grid 为

$$
(q,5,6),
qquad
(q,3,5),
qquad
(15,1,1),
$$

目标 nested chain 为

$$
(15,2,q)
\succeq
(15,1,q)
\succeq
(15,1,1).
$$

符号枚举结果为

$$
I(q)=\frac{31}{150}+\frac{9}{10q},
qquad
N(q)=\frac{3}{10}+\frac{7}{30q},
$$

因此

$$
R(q)=\frac{N(q)}{I(q)}
=\frac{45q+35}{31q+135}
\longrightarrow
\frac{45}{31}\approx1.451613.
$$

endpoint comparison 在 $q=101$ 和 $q\to\infty$ 两端对所有 independent/nested 竞争线均无违反。对应的 $q=101$ hierarchy 是

$$
(P_1^*,P_2^*,P_3^*)=(3030,1515,15),
$$

完整二维 exact arrangement 得到全域最大值

$$
\frac{2290}{1633}\approx1.402327
$$

且最大点确实是 $(z,y)=(1,1/15)$。

这已经严格把 hierarchy-independent overhead 上界的必要下界从 $117/85$ 提高到

$$
C\ge\frac{45}{31}.
$$

更一般地，固定 $P_1^*/P_2^*=2$、令 $P_3^*=p$ 并取 $q\to\infty$ 时，若同样的 active pattern 对某个素数 $p$ 成立，形式上会得到

$$
R_p(q)\to\frac{3p}{2p+1}\to\frac32.
$$

第 37 节进一步给出了素数 $p$-family 的统一一维 endpoint certificate；这里的 $p=15$ 仍然保留作为较强的具体二维 witness。

脚本为 `work/prove_p15_q_family.py`；完整二维验证使用 `work/exact_2d_pruned.py --pstars 3030 1515 15`。

## 37. 素数 $p$-family：从数值猜想升级为一维 witness 定理

把上一节的模式限制到素数 $p$，考虑

$$
(P_1^*,P_2^*,P_3^*)=(2pq,pq,p),
$$

其中 $p,q$ 是不同素数，并在 $(z,y)=(1,1/p)$ 处比较。候选 active pattern 为

$$
\begin{aligned}
\text{independent:}&\quad (q,2,p),\ (q,1,p),\ (p,1,1),\\
\text{nested:}&\quad (p,2,q)\succeq(p,1,q)\succeq(p,1,1).
\end{aligned}
$$

把每条线写成 $A+B/q$ 后，候选 pattern 给出

$$
I_p(q)=\frac{3}{p}+\frac{3}{2p^2}
 +\frac{3/2+2/p}{q},
$$

以及

$$
N_p(q)=\frac{9}{2p}+\frac{7}{2pq}.
$$

因此候选比值为

$$
R_p(q)=
\frac{p(9q+7)}{(6p+3)q+3p^2+4p}
\longrightarrow
\frac{3p}{2p+1}
\xrightarrow[p\to\infty]{}\frac32.
$$

而且对有限的 $p,q$，该 family 从下方逼近 $3/2$，因为

$$
\frac32-R_p(q)
=
\frac{9q+9p^2-2p}
{2\big((6p+3)q+3p^2+4p\big)}>0.
$$

脚本 `work/check_prime_p_family.py` 对 $q=1009$ 和

$$
p\in\{3,5,7,11,13,17,19,23,29,31,37,41,43,47\}
$$

逐条枚举全部独立 grids 和全部 nested chains。每个样本的 independent 与 nested endpoint comparison violations 都为 0，且枚举得到的精确比值与上式一致。例如：

| $p$ | exact $R_p(1009)$ | 极限 $3p/(2p+1)$ |
|---:|---:|---:|
| 5 | $2840/2087$ | $15/11$ |
| 11 | $24992/17507$ | $33/23$ |
| 19 | $43168/29803$ | $19/13$ |
| 31 | $70432/48427$ | $31/21$ |

作为二维 sanity check，`work/exact_2d_pruned.py --pstars 174 87 3` 对 $(p,q)=(3,29)$ 完整枚举 aspect-ratio 三角域，得到最大值

$$
\frac{67}{54}
$$

且最大点为 $(z,y)=(1,1/3)$；这个值与 $R_3(29)$ 完全一致。对 $(p,q)=(5,29)$ 和 $(11,29)$ 的完整二维枚举也分别得到 $335/263$ 与 $737/602$，最大点同样位于 $(1,1/p)$。

进一步对固定 $q=101$ 的 $(p,q)=(3,101),(5,101),(7,101),(11,101)$ 做完整二维 exact arrangement，最大值分别为

$$
\frac{229}{180},\quad
\frac{1145}{857},\quad
\frac{1603}{1180},\quad
\frac{2519}{1844},
$$

都与 $R_p(101)$ 一致，且最大点均为 $(z,y)=(1,1/p)$。这继续支持该 family 的二维 global-max 猜想，但仍不是对任意 $p,q$ 的符号证明。

现在可以把第一项缺口补上。脚本 `work/prove_prime_p_family.py` 对 $2pq$、$pq$、$p$ 的全部 square-free factor assignments 做符号枚举：独立 grids 数量为 $(27,9,3)$，nested chains 数量为 $27$。每条比较线都形如

$$
D(q)=A(p)+\frac{B(p)}{q}.
$$

只需检查 $q=\infty$ 和辅助端点 $q=p$。令 $t=1/p$，两个端点差值都是次数不超过 $3$ 的多项式；脚本在 $t\in[0,1/3]$ 上用两个区间的 exact Bernstein coefficients 证明所有差值均不为正。于是对所有不同素数

$$
p\ge3,\qquad q>p,
$$

在这个 aspect-ratio 点上，目标 independent grids 确实分别达到三层最小值，目标 nested chain 确实达到 nested 最小值。这里的 $q=p$ 只是 affine comparison 的辅助端点，不是要求把两个素数取相等。

因此可以严格推出：若 $C$ 是一个对所有 hierarchy 和 aspect ratios 都成立的 hierarchy-independent multiplicative overhead 常数，则

$$
C\ge R_p(q)=
\frac{p(9q+7)}{(6p+3)q+3p^2+4p}
$$

对所有不同素数 $p\ge3,q>p$ 都成立。先对固定 $p$ 取无穷多个素数 $q\to\infty$，再令素数 $p\to\infty$，得到严格必要条件

$$
\boxed{C\ge\frac32}.
$$

这已经不是 conjectural family，而是一个 **固定 aspect-ratio witness 的下界定理**。它仍然没有说明 $3/2$ 是最优上界：可能存在更大的 hierarchy overhead；也没有证明这个点是完整二维域中的 global maximizer。下一步应分别研究“是否有 $C>3/2$ 的更强 family”和“能否构造统一的 $C=3/2$ 上界”。

## 38. 2025 文献补充：fast/nested bilinear algorithms 的下界工具

继续核查 2022 之后的并行紧下界工作时，找到一篇与 Strassen-like 分支直接相关的 2025 期刊论文：Caleb Ju、Yifan Zhang、Edgar Solomonik，**Communication Lower Bounds for Nested Bilinear Algorithms via Rank Expansion of Kronecker Products**，*Foundations of Computational Mathematics* 25(1), 55--101, DOI [10.1007/s10208-023-09633-8](https://doi.org/10.1007/s10208-023-09633-8)。

它的贡献不是改写 2022 年 classical rectangular GEMM 的 memory-independent theorem，而是：

- 用 rank expansion 处理由 Kronecker product 嵌套得到的 bilinear algorithms；
- 给出 memory hierarchy 或 processor 间 communication lower bounds；
- 应用于 nested Toom--Cook、Strassen 以及部分对称 tensor contraction。

限制也很关键：该框架只适用于不重复计算同一个 DAG node 的执行。因此它补强的是 fast/nested bilinear algorithms 的 **no-recomputation** 分支；允许 recomputation 的 tight parallel bound 仍然是另一个问题。

到目前为止，并行紧下界的主线可以更准确地分成三条：

1. **classical dense GEMM**：2022 年的 rectangular、memory-independent、tight constants theorem；
2. **structured kernels**：2023--2025 的 SYRK/SYR2K/SYMM/Multi-TTM，把对称性或张量结构纳入几何不等式和 matching algorithm；
3. **fast/nested bilinear algorithms**：2025 年 rank-expansion/Kronecker-product 方法，继续推进 Strassen-like 的层级和处理器通信下界。

这一区分会避免把“新的特定算法类下界”误报成“普通 GEMM 主定理被替换”。

## 39. 文献核查修正：1994 年已有一种 parallel multilevel-memory 最优结果

继续沿着“多级内存是否从未被 tight 分析”这条线检索时，发现一个必须补入历史脉络的早期结果：Vitter 与 Shriver，**Algorithms for Parallel Memory, II: Hierarchical Multilevel Memories**，*Algorithmica* 12 (1994), 148--169。

该文定义了 $P$ 个并行的 hierarchical memories，层级之间的访问按统一的 access-cost function 计价，层级之间在 base-memory level 发生通信；作者对标准 square matrix multiplication 给出 matching upper/lower bounds，并明确声称在 P-HMM 与 P-BT 两种模型中达到 optimality。来源：[论文 PDF](https://ittc.ku.edu/~jsv/Papers/ViS94.sorting_hierarchical.pdf)。

这个结果会修正本日志早先过宽的 gap 表述，但并不消除当前问题，原因是模型不同：

1. 它的矩阵乘法是标准 square MM，当前日志研究的是 rectangular GEMM 及 2022 年的 aspect-ratio active sets；
2. 它把多级内存访问折叠进统一 access-cost function，且论文明确指出其 lower bound 忽略 hierarchy 之间的 network communication；
3. 它没有分析当前的 processor-grid divisibility、每层独立最优 grid 与 nested grid chain 之间的 multiplicative overhead；
4. 它也不提供现代 HBM/L2/shared/register、messages、replication 和 2022 tight memory-independent constants 的联合定理。

所以“多级内存从未被研究”是错误的；更准确的 gap 是：**在 rectangular GEMM、现代 parallel communication 计数和嵌套 processor-grid 兼容性约束下，是否能把各层的 tight bound 与同一个可实现 schedule 统一起来。** 这个修正版 gap 与第 37 节的 $C\ge3/2$ witness 是兼容的：前者是模型/算法层面的文献缺口，后者是当前嵌套-grid 代理模型中的新下界。

## 40. 有限范围的反例搜索：目前没有发现超过 $3/2$ 的边界实例

为了检验第 37 节的下界是否可能很快被更大的 family 超过，新增批量扫描脚本 `work/batch_boundary_scan.py`。它对任意满足

$$
P_1>P_2>P_3,qquad P_2\mid P_1,qquad P_3\mid P_2
$$

的三层 hierarchy，在 $z/x=1$ 边界上批量计算 $t=y/x\in[0,1]$ 的 lower envelopes；近似阶段采用 101 个 $t$ 点，候选再交给原有 exact breakpoint 枚举。

固定随机种子、抽取 $500$ 个层级、限制 $P_1\le1500$ 后，全部样本都成功完成近似评估；精确复核的最高值为

$$
\frac{679}{499}\approx1.360721,
$$

对应 hierarchy $(1498,749,7)$、最大点 $t=1/7$。扫描没有发现超过 $3/2$ 的边界反例，但它只覆盖有限随机样本、只覆盖 $z/x=1$，因此不能证明上界。它的主要用途是确认：在小规模任意因子层级中，较大的 overhead 仍然沿着“含大素数因子”的 family 出现，而不是来自普通小整数 hierarchy。

## 41. 2026 新模型：low-bandwidth rounds 下的矩形 MM 下界

文献检索还发现 Gupta、Suomela、Vahidi 的 2026 预印本 **Rectangular Matrix Multiplication in the Low-Bandwidth Model**。该模型有 $n$ 台机器，每轮每台机器只能发送和接收一个 $O(\log n)$-bit 消息；输入均衡分布，目标是每台机器最终得到指定的输出部分。论文研究

$$
\langle n,d,n\rangle,
\qquad
\langle d,n,d\rangle,
$$

两种矩形乘法，并同时给出 upper bounds、unconditional lower bounds 和 conditional lower bounds。对于 $\langle n,d,n\rangle$，论文报告了 $d\le\sqrt n$ 区间内的 $\Theta(d\sqrt n)$ 结果，以及在更大 $d$ 区间的不同复杂度；这体现出与普通 congested-clique 或 word-volume 模型不同的 phase transition。

这篇工作应放在研究矩阵中，但不能直接替代 2022 年的 parallel word-volume theorem：它的复杂度单位是 communication rounds 和每轮 bit budget，而不是 critical-path words/messages。它对本项目的启发是，矩形 aspect-ratio 的 active-set 现象并不只出现在 processor-grid volume 优化中，在受限带宽的 round 模型中也会产生新的分区；未来可以研究这两种模型是否存在可比较的 regime map。

来源：[Gupta–Suomela–Vahidi, arXiv:2606.04652](https://arxiv.org/abs/2606.04652)。

## 42. 当前 checkpoint：下界已证实，上界仍待证明

本轮重新运行了 `work/prove_prime_p_family.py` 和全部 Python 工具的语法检查。结果是：独立 processor-grid 枚举为 27 个，嵌套链枚举为 27 个，132 个端点多项式证书全部通过；证明域为素数 $p\ge3$、$q\ge p$，并使用 $t=1/p\in[0,1/3]$。因此，固定 aspect-ratio witness 家族严格给出

$$
C\ge \frac32
$$

作为该 nested-grid proxy 模型中任何统一乘法 overhead 常数的必要条件。这个结论不依赖浮点扫描，也不声称 $3/2$ 是上界。

同时，`work/batch_boundary_scan.py` 对 500 个有限层级做了 $z/x=1$ 边界扫描，并对候选进行 exact rational re-evaluation。最高样本为

$$
(P_1,P_2,P_3)=(1498,749,7),\qquad \frac{679}{499}\approx1.360721,
$$

仍低于 $3/2$。这只能作为有限范围的反例搜索证据，不能排除二维 aspect-ratio 域或更大层级中的 $C>3/2$ 家族。

下一步分成两个互相独立的证明任务：

1. 对一般素数家族，证明 $(z,y)=(1,1/p)$ 是完整二维 arrangement 的 global maximizer，而不只是边界 witness；
2. 在同一 nested-grid proxy 中尝试构造 $C=3/2$ 的统一上界，或自动搜索 $C>3/2$ 的新因子族。

只有第 1 项和第 2 项都完成后，才能把当前的“必要下界 $C\ge3/2$”升级为 tight constant 结论。

## 43. 扩大反例搜索：最高候选仍低于 $3/2$

为检验第 42 节的有限搜索是否受范围影响，将随机可整除层级从 500 个扩大到 2,500 个，取 $P_1\le5000$，并把边界采样间隔设为 $1/200$。2,499 个层级成功完成近似评估；最高的 12 个候选全部交给 exact boundary evaluator 复核。

最高候选为

$$
(P_1,P_2,P_3)=(3546,1773,9),
\qquad
R_{\partial}=\frac{2670}{1903}\approx1.403048,
\qquad t=\frac{y}{x}=\frac19.
$$

该层级的完整二维 exact arrangement 也已运行：共有 54 条 nested chains，独立 lower-envelope active counts 为 $(25,10,5)$，nested active count 为 25，枚举 38,420 个 arrangement vertices 后，最大值仍为

$$
\frac{2670}{1903}
$$

且位置仍是 $(z,y)=(1,1/9)$。因此这次搜索没有发现超过 $3/2$ 的边界或二维反例；它仍然只是有限范围证据，不能代替统一上界证明。

## 44. 2025--2026 原始论文检索：补充模型边界

针对“这些年是否出现了新的并行紧下界”重新检索 arXiv、作者版本和期刊记录后，得到三条需要分开的结果：

1. **low-bandwidth sparse MM（Gupta 等，SIROCCO 2025）**：在每轮每机只能收发一个 $O(\log n)$-bit 消息的模型中，uniformly sparse 算法改进到 $O(d^{1.832})$ rounds，并扩展到 row/column/average-sparse 等结构。它是算法轮数进展，不能当作 dense GEMM 的 universal tight lower bound。
2. **symmetric tensor extension（Al Daas 等，2025）**：对三阶对称张量沿两个 mode 乘同一向量，给出 parallel communication lower bound 和 matching algorithm。它说明 geometric/HBL 方法继续向结构化张量扩展，但没有改变普通矩形 GEMM 的主定理。
3. **coded/private batch MM（IEEE TIT 2026）**：研究下载率、随机性和隐私的 converse/achievability。其通信对象是服务器下载量和信息泄露约束，不是处理器间 words/messages，因此应放在相邻的信息论模型，而不是本项目的 machine data-movement 表中。

因此，截至本轮检索，仍没有发现一篇在 **普通 dense rectangular GEMM、distributed-memory word volume、一般 aspect ratios** 上取代 2022 tight memory-independent theorem 的新结果。新增工作主要改变了算子结构或通信模型，而不是把主定理推广到一个严格更一般的机器通信模型。

## 45. 素数族二维 global-max 的扩大 exact 检验

为把第 37 节的一维 witness 与二维 global-max 猜想分开验证，新增脚本 `work/check_prime_p_global.py`，直接调用 exact rational arrangement enumeration。它对

$$
p\in\{3,5,7,11,13,17\},
\qquad
q\in\{29,31,53,71,101\},
\qquad q>p
$$

的全部 30 个组合逐一检查。每个案例都满足：

- exact maximum 位于 $(z,y)=(1,1/p)$；
- maximum 等于
  $$
  R_p(q)=\frac{p(9q+7)}{(6p+3)q+3p^2+4p};
  $$
- independent lower envelopes 的 active counts 恒为 $(16,8,3)$；
- nested lower envelope 有 16 条 active lines；
- 每个案例的顶点枚举规模约为 4,470--4,900。

这 30 个 exact checks 强烈支持一般素数族的二维 global-max 猜想，并显示 active-set 组合在参数范围内保持稳定。不过它们仍然是有限参数验证；要成为定理，还需要证明 active-set 稳定性以及所有 arrangement vertices 的参数不等式。

## 46. 新的解析结果：素数族边界最大值定理

在完整二维证明之前，可以先严格解决边界 $z=x$。令 $t=y/x\in[0,1]$，并取

$$
(P_1^*,P_2^*,P_3^*)=(2pq,pq,p),
\qquad q>p\ge3,
$$

其中 $p,q$ 为不同素数。对一个 grid $g=(a,b,c)$，边界上的单层 proxy 为

$$
H_g(t)=\frac{1}{ab}+\frac{1}{ac}+\frac{t}{bc}
      =\frac{b+c+ta}{abc}.
$$

对 $2pq$ 的所有因子分配，按 $a\in\{1,2,p,q,2p,2q,pq,2pq\}$ 分类；直接比较 $b+c+ta$ 可得 independent lower envelope 的第一层为

$$
f_1(t)=\begin{cases}
\frac1{pq}+t,&0\le t\le\frac1{pq},\\
\frac3{2pq}+\frac t2,&\frac1{pq}\le t\le\frac1q,\\
\frac{p+2}{2pq}+\frac{t}{2p},&\frac1q\le t\le1.
\end{cases}
$$

对 $pq$ 和 $p$ 两层同样比较得到

$$
f_2(t)=\begin{cases}
\frac2{pq}+t,&0\le t\le\frac1q,\\
\frac{p+1}{pq}+\frac tp,&\frac1q\le t\le1,
\end{cases}
\qquad
f_3(t)=\frac2p+t.
$$

因此 $I(t)=f_1(t)+f_2(t)+f_3(t)$ 分成三个区间：

$$
I_A=\frac3{pq}+\frac2p+3t,
\quad
I_B=\frac7{2pq}+\frac2p+\frac52t,
\quad
I_C=\frac{3p+4}{2pq}+\frac2p+\left(1+\frac3{2p}\right)t.
$$

接下来只需使用三个合法的 nested chains：

$$
\begin{aligned}
\mathcal C_A&=((2pq,1,1),(pq,1,1),(p,1,1)),\\
\mathcal C_B&=((pq,1,2),(pq,1,1),(p,1,1)),\\
\mathcal C_C&=((p,2,q),(p,1,q),(p,1,1)).
\end{aligned}
$$

它们给出的 numerator upper bounds 分别为 $I_A$、$I_B$ 和

$$
N_C(t)=\frac{7q+4}{2pq}+\left(1+\frac3{2q}\right)t.
$$

在 $[0,1/(pq)]$ 和 $[1/(pq),1/q]$ 上，$mathcal C_A,mathcal C_B$ 直接给出 $N/I\le1$。在 $[1/q,1/p]$ 上使用 $mathcal C_B$，其上界 $I_B/I_C$ 的导数符号由

$$
\frac{3\big(5p^2+2p-7+4q(p-1)\big)}{4p^2q}>0
$$

决定；在 $[1/p,1]$ 上使用 $mathcal C_C$，其上界 $N_C/I_C$ 的导数符号由

$$
-\frac{3(q-p)\big((2p+7)q+3p+4\big)}{4p^2q^2}<0
$$

决定。因此边界比值在 $t=1/p$ 达到最大。第 37 节的 endpoint certificate 又保证 $\mathcal C_C$ 在该点确实是 nested minimum，于是得到严格边界定理

$$
\boxed{
\max_{0\le t\le1}\frac{N(1,1,t)}{I(1,1,t)}
=R_p(q)
=\frac{p(9q+7)}{(6p+3)q+3p^2+4p}
}.
$$

`work/check_prime_p_boundary_theorem.py` 对前述 30 个参数组合逐项验证了这些公式；进一步加入更接近 $q=p$ 的素数对和更大的参数后，共完成 161 个 exact boundary cases。现在尚未解决的部分被准确收窄为：证明从边界 $z=x$ 向三角域内部移动不会产生更大的 ratio；边界最大值本身已经不再只是数值猜想。

## 47. 二维缺口的具体化：径向单调性猜想

把归一化 aspect ratios 写成

$$
(x,z,y)=(1,s,st),\qquad 0\le s,t\le1.
$$

边界定理已经解决 $s=1$。一个足以推出完整二维上界的更强命题是：对固定 $t$，

$$
F_{p,q}(s,t)=\frac{N(1,s,st)}{I(1,s,st)}
$$

关于 $s$ 单调不减。若该命题成立，则

$$
F_{p,q}(s,t)\le F_{p,q}(1,t)\le R_p(q),
$$

从而边界定理自动推广到整个三角域。

新增诊断脚本 `work/check_prime_radial_monotonicity.py`，在 $(s,t)$ 的 exact rational 网格上逐点检查相邻 $s$ 值。默认的 30 个 $(p,q)$ 组合、步长 $1/40$ 全部通过；另选更大的 $p,q$ 和步长 $1/80$ 的 24 个组合也全部通过。没有发现负的径向增量。

这仍然不是证明。下一步应利用 $H_g(1,s,st)=c/P+s(b+ta)/P$ 的形式，按 active grid 组合证明每个可行 cell 上 ratio 导数非负；当前数值检查显示真正需要处理的 active combinations 远少于完整 2-D arrangement。

## 48. 一个严格的二维内部区域：$t\le1/q$ 时 overhead 恰为 1

径向分析可以先解决一个非边界区域。对固定 grid $g=(a,b,c)$，在

$$
(x,z,y)=(1,s,st)
$$

下有

$$
H_g(1,s,st)=\frac{c}{abc}+s\frac{b+ta}{abc},
$$

它关于 $s$ 是仿射函数。

在 (2pq) 这一层：

- 当 $0\le t\le1/(pq)$ 时，边界 $s=1$ 的 lower envelope 由 $(2pq,1,1)$ 达到；
- 当 $1/(pq)\le t\le1/q$ 时，边界 $s=1$ 的 lower envelope 由 $(pq,2,1)$ 达到。

对任意竞争 grid，$s=0$ 时其 cost 不小于候选 grid，因为此时只剩 $c/(abc)=1/(ab)$，而候选的 $c=1$。$s=1$ 时的不等式正是第 46 节已经证明的边界 envelope 不等式。由于差值关于 $s$ 仿射，两个端点成立就推出整个 $s\in[0,1]$ 成立。

同理，在 $pq$ 层，当 $t\le1/q$ 时 $(pq,1,1)$ 对所有 $s$ 都是 independent minimizer；在 $p$ 层 $(p,1,1)$ 对所有 $(s,t)$ 都是 minimizer。

于是：

$$
\begin{cases}
((2pq,1,1),(pq,1,1),(p,1,1)),&0\le t\le1/(pq),\\
((pq,2,1),(pq,1,1),(p,1,1)),&1/(pq)\le t\le1/q,
\end{cases}
$$

分别是合法 nested chains，并且逐层达到 independent minima。因此得到严格结论

$$
\boxed{
F_{p,q}(s,t)=\frac{N(1,s,st)}{I(1,s,st)}=1
\quad\text{for all }0\le s\le1,\ 0\le t\le1/q.
}
$$

这把完整二维未决区域进一步收窄到 $t\ge1/q$。真正的 overhead 只能出现在第二个矩阵维度已经足够大、使得 $pq$ 层的独立最优 grid 转向 $(q,p,1)$ 之后。

## 49. 修正后的二维多面体证书：叠加 nested lower envelope

这一节先记录一次重要的验证修正。初版脚本把三角域的一条约束方向写反，实际检查了
$0\le s\le u\le1$；同时它要求同一条 nested chain 覆盖整个 independent cell，这个要求
也过强，因为 nested minimum 本身可以在一个 independent cell 内切换。初版的 9-cell 与
固定两类 chain 结论因此全部作废，不能继续作为证据使用。

现版 `work/check_prime_three_halves_cells.py` 使用正确域

$$
0\le u\le s\le1,\qquad (x,z,y)=(1,s,u),
$$

并将 independent lower envelope 与所有合法 nested chains 的 lower envelope 叠加。对
$g=(a,b,c)$、$abc=P$，代价仍是仿射函数

$$
H_g(1,s,u)=\frac{c}{P}+s\frac{b}{P}+u\frac{a}{P}.
$$

交换论证把 independent 候选限制到 $a\ge b\ge c$，三层候选数为 $(5,2,1)$。对每个
independent candidate 组合，再对每条 nested chain 加入

$$
H_{\mathcal C}\le H_{\mathcal C'}\qquad\text{for every legal }\mathcal C',
$$

从而得到 nested lower-envelope subregion。在每个非空 subregion 上，
$H_{\mathcal C}-\tfrac32 I$ 是仿射函数，只需检查其顶点；这是连续域上的精确有理数
证书，而不是采样点检查。

修正后的结果：

- 每个参数有 10 个非空 independent cells，active candidate 数仍为 $(5,2,1)$；
- 每个参数产生 84 个非空 nested subregions；
- 默认 30 组参数全部通过；
- 扩展到 $p\in\{3,5,\ldots,47\}$、$q$ 列表覆盖的 161 组参数后，仍全部通过；
- 例如此前暴露问题的 $(p,q)=(5,53)$ 也通过，说明修正后的证书没有继承初版的假阳性。

这仍然是逐参数证书，不是对所有 $p<q$ 的统一定理。下一步应按 $q\ge2p$ 与
$p<q<2p$ 符号化 10 个 independent cell 的代表、84 类 nested subregion 的合并模式，
再证明每类仿射差值的系数在 $p\ge3,q>p$ 下非正。一个更现实的中间目标是先证明
这 84 个 subregions 其实只对应少量对称的 chain-line 模式。

可复现实验：

```text
python -m py_compile work/check_prime_three_halves_cells.py
python work/check_prime_three_halves_cells.py
# checked=30 exact 3/2 cell certificates

python work/check_prime_three_halves_cells.py --p 3 5 7 11 13 17 19 23 29 31 37 41 43 47 \\
  --q 5 7 11 13 17 19 23 29 31 37 41 43 47 53 59 71 101 197
# checked=161 exact 3/2 cell certificates
```

## 50. Nested envelope 的规模：27 条 chain 压缩为 16 条 active lines

虽然三层 $(2pq,pq,p)$ 一共有 27 条合法 nested chains，但在正确三角域上做 nested
lower-envelope 过滤后，每个测试参数只留下 16 条 active affine lines。对 $(p,q)=(5,53)$，
这 16 条 line 的系数只由以下六类表达式组合而成：

$$
A=\frac1p+\frac{3}{2pq},\quad
B=\frac1p+\frac1{2q},\quad
C=\frac12,\quad
D=1+\frac{3}{2q},\quad
E=\frac52,\quad
F=3.
$$

例如出现 $(A,A,F)$、$(A,B,E)$、$(A,C,D)$ 及其若干坐标排列。不同参数的 active line
集合数量保持为 16（已检查 $(3,29),(5,53),(11,13),(11,101)$），而每个参数的 84 个
nonempty nested subregions 来自这些 lines 与 10 个 independent cells 的交叠。

这给出更可行的符号化路线：先证明 active line 模板在 $q\ge2p$ 和 $p<q<2p$ 两个
参数区间内稳定，再逐模板证明

$$
L_{\mathrm{nested}}(s,u)-\frac32L_{\mathrm{independent}}(s,u)\le0
$$

在相应交集多边形的顶点成立。这样可以把“27 条 chain 的全局最小值”压缩成有限个
参数化模板；目前这一步仍未完成。

## 51. 16 条 active chain 的符号模板

进一步按实际 grid 三元组，而不是只看 affine line 系数，提取出一个稳定的 16-chain
模板。令 $\mathcal T_{p,q}$ 为以下 chain 的集合，每个括号内依次对应
$(2pq,pq,p)$ 三层：

$$
\begin{aligned}
&((1,2pq,1),(1,pq,1),(1,p,1)),\\
&((2,p,q),(1,p,q),(1,p,1)),
  ((2,q,p),(1,q,p),(1,1,p)),
  ((2,pq,1),(1,pq,1),(1,p,1)),\\
&((p,2,q),(p,1,q),(p,1,1)),
  ((p,q,2),(p,q,1),(p,1,1)),
  ((p,2q,1),(p,q,1),(p,1,1)),\\
&((2p,1,q),(p,1,q),(p,1,1)),
  ((2p,q,1),(p,q,1),(p,1,1)),\\
&((q,2,p),(q,1,p),(1,1,p)),
  ((q,p,2),(q,p,1),(1,p,1)),
  ((q,2p,1),(q,p,1),(1,p,1)),\\
&((2q,p,1),(q,p,1),(1,p,1)),\\
&((pq,1,2),(pq,1,1),(p,1,1)),
  ((pq,2,1),(pq,1,1),(p,1,1)),
  ((2pq,1,1),(pq,1,1),(p,1,1)).
\end{aligned}
$$

新脚本 `work/check_prime_active_chain_templates.py` 对每个参数重新构造 independent 与
nested lower-envelope 的交集，验证实际 active chain 集合是否恰好等于
$\mathcal T_{p,q}$。默认的 30 组参数全部得到 `active=16 template_match=True`，其中同时
包含 $q<2p$ 与 $q>2p$ 的情形；进一步加入接近 $q=p$ 的参数后共检查 42 组，仍全部通过。
这表明参数化证明可以先只处理这 16 个模板，而不必从
27 条合法 chain 逐条展开；但“模板稳定”目前仍是 exact regression 结论，还没有写出
$p,q$ 符号不等式证明。

## 52. 非模板 chain 的全域仿射支配

16-chain 模板之外还有 11 条合法 nested chain。对任意两条 chain，代价差是 $(s,u)$
上的仿射函数；因此一条模板 chain 在三角域

$$
0\le u\le s\le1
$$

上支配另一条 chain，只需在三个顶点 $(0,0),(1,0),(1,1)$ 检查差值非正。
脚本 `work/check_prime_chain_dominance.py` 对每个参数逐条检查 11 条非模板 chain，询问
是否存在一条 16-chain 模板在整个三角域上支配它。默认 30 组参数和加入 $q$ 接近 $p$
的边界后的 42 组参数均得到：

```text
chains=27 template=16 domination=True
checked=42 affine chain-dominance cases
```

进一步把 $p,q$ 都取自 $\{3,5,\ldots,97\}$，对所有 $p<q$ 的 276 组参数运行同一
检查，得到 `checked=276 affine chain-dominance cases`。这使“16-chain reduction”成为
当前最稳定的经验结构，但仍需把表中的逐行 corner inequalities 写成正式参数证明。

这比“active line regression”更强：如果能把这 11 个支配关系写成 $p\ge3,q>p$ 下的
简单代数不等式，就可先严格证明 nested lower envelope 只需考虑 16 条模板，再处理
independent cell 与这 16 条 line 的交集。当前仍缺少这一步的全参数符号证明，但未决问题
已经从 27 条 chain 的组合搜索缩小为 11 个支配关系。

## 53. 11 个非模板 chain 的候选通用支配引理

令 $r=1/p$、$t=1/q$、$v=rt$，则 $0<t<r\le1/3$。把 27 条合法 chain 按三层
$(2pq,pq,p)$ 枚举后，16 条模板之外的 11 条恰好是：

$$
\begin{array}{c|c}
\text{被支配 chain} & \text{支配模板}\\ \hline
((1,1,2pq),(1,1,pq),(1,1,p)) & ((1,2pq,1),(1,pq,1),(1,p,1))\\
((1,2,pq),(1,1,pq),(1,1,p)) & ((2,p,q),(1,p,q),(1,p,1))\\
((1,p,2q),(1,p,q),(1,p,1)) & ((2,p,q),(1,p,q),(1,p,1))\\
((1,2p,q),(1,p,q),(1,p,1)) & ((2,p,q),(1,p,q),(1,p,1))\\
((1,q,2p),(1,q,p),(1,1,p)) & ((2,p,q),(1,p,q),(1,p,1))\\
((1,2q,p),(1,q,p),(1,1,p)) & ((2,p,q),(1,p,q),(1,p,1))\\
((1,pq,2),(1,pq,1),(1,p,1)) & ((2,pq,1),(1,pq,1),(1,p,1))\\
((2,1,pq),(1,1,pq),(1,1,p)) & ((2,p,q),(1,p,q),(1,p,1))\\
((p,1,2q),(p,1,q),(p,1,1)) & ((p,2,q),(p,1,q),(p,1,1))\\
((q,1,2p),(q,1,p),(1,1,p)) & ((p,2,q),(p,1,q),(p,1,1))\\
((2q,1,p),(q,1,p),(1,1,p)) & ((p,2,q),(p,1,q),(p,1,1))
\end{array}
$$

对每一行，支配模板减去被支配 chain 的差值是 $(s,u)$ 的仿射函数。三个顶点的差值
只会落入以下几类：

$$
-3+r+\frac32v,\quad
-\frac52+\frac52r,\quad
-\frac32+\frac32r+\frac32t-kv\ (k=2,3),
$$

$$
-\frac r2,\quad -\frac r2+\frac v2,\quad
-\frac t2,\quad -\frac t2+\frac v2,
$$

以及

$$
-1-\alpha t+\frac52r+\beta\frac v2,
\qquad \alpha\in\{\tfrac32,2\},\ \beta\in\{0,1\}.
$$

这些量在 $0<t<r\le1/3$ 下都非正：前几组直接由 $r\le1/3$、$v\le r^2$ 得到；中间
一组满足 $-\frac32+\frac32r+\frac32t\le-\frac12$；最后一组使用
$\frac52r+\frac12r^2\le\frac89<1$。脚本
`work/prove_prime_chain_dominance_symbolic.py` 已逐行生成 11 组 corner forms，并输出
`checked=11 symbolic dominance rows`。因此在当前素因子枚举模型下，16-chain reduction
已经有一个不依赖素数性的 $p\ge3,q>p$ 代数证明；剩余未决部分是 16 条模板与 independent
envelope 交集上的 $3/2$ 上界，而不是 nested chain 的组合爆炸。

## 54. 用 16-chain reduction 重跑 $3/2$ certificate

新增 `work/check_prime_three_halves_reduced.py`，不再枚举 27 条 chain，而是直接使用已经
约化后的 16 条模板，重新叠加 independent 与 nested lower envelopes。默认 30 组参数全部
得到 10 个 independent cells、84 个 nested subregions 和 `certificate=True`：

```text
checked=30 reduced 3/2 cell certificates
```

这一步确认前面的 16-chain reduction 与二维 $3/2$ 证书可以独立串接；后续的主要工作已
集中到 16 条模板的参数化 cell 几何，而不是再处理被支配的 11 条 chain。

## 55. 三条平均 nested chain 给出素数族的统一 $3/2$ 上界

现在可以绕开 10 个 independent cells 和 84 个 nested subregions。仍用

$$
(x,z,y)=(1,s,u),\qquad 0\le u\le s\le1,
$$

并令 $r=1/p,t=1/q,v=rt$。取三条合法 nested chains：

$$
\begin{aligned}
\mathcal A&=((p,2,q),(p,1,q),(p,1,1)),\\
\mathcal B&=((p,q,2),(p,q,1),(p,1,1)),\\
\mathcal C&=((pq,1,2),(pq,1,1),(p,1,1)).
\end{aligned}
$$

它们的 affine costs（系数顺序为常数、$s$、$u$）分别为

$$
L_A=\left(\frac52r,\ r+2v,\ 1+\frac32t\right),
$$

$$
L_B=\left(r+2v,\ \frac32r,\ 1+\frac32t\right),
\qquad
L_C=\left(r+2v,\ r+\frac32v,\ \frac52\right).
$$

令 $\bar L=(L_A+L_B+L_C)/3$，则

$$
\boxed{
\bar L=\left(\frac32r+\frac43v,\ \frac76(r+v),\ \frac32+t\right).
}
$$

因为 nested minimum 不超过任意平均值，$N\le\bar L$。另一方面，independent minimum
可以限制到 $a\ge b\ge c$ 的 sorted factor grids。第一层 $2pq$ 的候选 affine lines 为

$$
\begin{array}{c|ccc}
g & 1/(ab) & 1/(ac) & 1/(bc)\\ \hline
(q,p,2)&v&t/2&r/2\\
(q,2p,1)&v/2&t&r/2\quad(q\ge2p)\\
(2p,q,1)&v/2&r/2&t\quad(p<q<2p)\\
(2q,p,1)&v/2&t/2&r\\
(pq,2,1)&v/2&v&1/2\\
(2pq,1,1)&v/2&v/2&1
\end{array}
$$

第二层只需 $(q,p,1)$ 与 $(pq,1,1)$，对应 lines $(v,t,r)$ 和 $(v,v,1)$；第三层是
$(p,1,1)$，对应 $(r,r,1)$。对这 5 个第一层候选、2 个第二层候选，以及两种
$q/(2p)$ 排序区间，逐一计算

$$
\Delta=\bar L-\frac32(L_{2pq}+L_{pq}+L_p).
$$

每个 $\Delta$ 都是 $(s,u)$ 的 affine function。新脚本
`work/prove_prime_three_halves_average.py` 检查 20 个组合在 $(0,0),(1,0),(1,1)$ 三个
顶点的差值，并用 $0<t<r\le1/3$、$v=rt$ 给出非正上界，输出：

```text
checked=20 symbolic average certificates
```

因此，对任意 odd primes $3\le p<q$，这个三层 hierarchy family 满足

$$
N_{p,q}(s,u)\le\bar L(s,u)\le\frac32 I_{p,q}(s,u)
\qquad(0\le u\le s\le1).
$$

第 12 节的 witness 给出同一族上的必要下界
$R_p(q)\to3/2$（先令 $q\to\infty$，再令 $p\to\infty$），所以该特定 hierarchy family
的全域 overhead supremum 已确定为

$$
\boxed{\sup_{\substack{3\le p<q\\p,q\ \mathrm{prime}}}\sup_{0\le u\le s\le1}\frac{N_{p,q}(s,u)}{I_{p,q}(s,u)}=\frac32.}
$$

这个结论的范围是 $(P_1,P_2,P_3)=(2pq,pq,p)$ 的素数构造；它还不是任意三层
processor hierarchy 的 universal $3/2$ 定理。

## 56. 用动态规划扫描一般复合层次的边界与若干二维核验

为避免直接枚举所有 nested chains，新增 `work/scan_boundary_dp.py`。在边界
$z/x=1, t=y/x\in[0,1]$ 上，每个 grid 是一条 affine line；脚本先对每个外层 grid
合并兼容的内层 partial chains，再做 lower-envelope pruning，最后精确枚举所有 line
交点。这样可以系统扫描

$$
(P_1,P_2,P_3)=(p_3r_2r_1,p_3r_2,p_3),\qquad p_3,r_1,r_2\ge2,\quad P_1\le240
$$

的 1382 个整除层次。边界扫描的最大值为

$$
(230,115,5):\quad \frac{535}{427}\approx1.2529274,
\qquad t=\frac15.
$$

其后是 $(222,111,3)$ 的 $5/4$ 和 $(186,93,3)$ 的 $143/115$；所有扫描实例都低于
$3/2$。对前六个候选再用 `work/exact_2d_pruned.py` 做完整二维 arrangement 核验，最大值
仍由 $(230,115,5)$ 在 $(z,y)=(1,1/5)$ 取得，且为同一个精确比值 $535/427$；其余五个
候选也与边界结果一致。

这不是一般层次的证明，因为扫描只覆盖 $P_1\le240$ 的整数整除族，也没有覆盖任意
非整除 processor counts 或更多层级。但它给出两个可操作线索：

1. 当前高比值样本仍集中在 $z/x=1$ 的边界，支持优先证明“最坏 aspect-ratio 在边界”这一
   单调性引理；
2. 复合因子并未在小规模搜索中产生超过 $3/2$ 的反例，下一步应把动态规划 envelope
   写成可归纳的兼容格证明，而不是继续盲目扩大枚举。

## 57. 近期文献核对：并行紧下界已经推进到“联合通信”和结构化 kernel

补查到两条与当前问题直接相关、且比 2022 年主定理更接近现代层次架构的路线。

1. Zhu、Hua、Jin 的 **Joint-Communication Optimal Matrix Multiplication with
   Asymmetric Memories**（JCST 40(3), 2025，
   [DOI 页面](https://doi.org/10.1007/s11390-023-3489-y)）把水平通信（处理器间）与垂直
   通信（主存/缓存）放进同一个目标。在对称内存中可以分别最优后组合；在非对称内存中两者
   存在 trade-off，并给出匹配 joint lower bound 的 JOMMA 算法。它是目前最接近本日志
   “多级/跨层联合下界”的直接工作，但模型仍是一个主存—缓存垂直层和分布式处理器层，
   不是任意 $L$ 级 nested hierarchy 的 universal theorem。

2. Al Daas、Ballard、Grigori、Kumar、Rouse、Verite 的 **Communication Lower Bounds and
   Optimal Algorithms for Symmetric Matrix Computations**（arXiv:2409.11304；后发表于
   ACM TOPC 12(2), 2025）把几何不等式加约束优化的方法扩展到 SYRK、SYR2K、SYMM，并在
   sequential 与 distributed-memory parallel 两种模型中给出 tight lower bounds 和
   matching algorithms。它说明“紧下界 + 最优算法”的框架已能系统处理结构化 BLAS-3
   kernel，但并没有解决一般 GEMM 的多层兼容性。

因此，当前文献缺口可以更精确地表述为：已有单层 parallel memory-independent bound、
单层 memory-dependent bound、结构化 kernel bound，以及二层 joint-communication bound；
仍缺少对任意 $L\ge3$ 层、允许跨层复用与复制的统一紧下界及 matching schedule。这个缺口
与本日志中的 hierarchy envelope 问题是同一个方向。

## 58. 四层 hierarchy 的首轮实验

新增 `work/scan_multilevel_boundary_dp.py`，把三层动态规划推广到任意层数：对每个外层
grid 保存所有兼容内层 partial-chain lines 的 lower envelope，再逐层合并。对四层整除族

$$
(P_1,P_2,P_3,P_4)=(p_0r_1r_2r_3,p_0r_1r_2,p_0r_1,p_0),
$$

在 $P_1\le80$ 的 109 个层次上做了精确 $z/x=1$ 边界扫描。最高值为

$$
(56,28,14,2):\quad \frac{803}{721}\approx1.11373,
\qquad y/x=\frac{36}{77}.
$$

所有四层样本均远低于 $3/2$。这说明“层数增加必然放大 nested/independent overhead”并
没有在小规模边界实验中出现；但它仍只是边界证据，不能推导多层 universal bound。下一步
需要：(i) 比较四层 partial-envelope 的活跃线数，寻找可归纳的状态压缩；(ii) 再检验非整除
或不规则 processor counts；(iii) 将二维 arrangement 证书扩展到更多四层候选。

## 59. 四层二维 arrangement 的精确核验

新增 `work/exact_multilevel_2d.py`，把二维域的半平面可行性、partial-chain pruning 和
arrangement vertex 枚举推广到任意层数。它先在每个兼容状态上保留确实出现在
$0\le y\le z\le1$ lower envelope 的 affine lines，再对所有 active equality lines 与三条
域边界求交；由于每个 cell 上 $N/I$ 是两个 affine functions 的比值，极值只需检查这些
vertices。

脚本先与已有三层精确 verifier 在 $(30,15,3)$ 上得到完全相同的最大值 $13/12$，再核验
四层候选：

```text
(56, 28, 14, 2): 803/721 = 1.113730929... at (z,y)=(1,36/77)
(80, 40, 20, 4): 226/205 = 1.102439024... at (z,y)=(1,1/4)
(60, 20, 10, 2): 83/76 = 1.092105263... at (z,y)=(1,1/2)
```

因此目前四层最高样本的二维最大值仍准确落在 $z=1$ 边界；这强化了边界单调性作为下一
个解析引理的优先级，但没有替代对任意层数的证明。

## 60. 五层 hierarchy 的边界与二维核验

五层扫描（`work/scan_multilevel_boundary_dp.py --levels 5 --limit 64`）检查了 11 个整除
层次，最高边界比值为

$$
(48,24,12,6,2):\quad \frac{53}{51}\approx1.0392157,
\qquad y/x=\frac12.
$$

随后用 `work/exact_multilevel_2d.py` 做全二维精确 arrangement。该实例保留 70 条最终
nested active lines、995008 个 arrangement vertices，最大值仍为 $53/51$，位置为
$(z,y)=(1,1/2)$。随着层数增加，overhead 在这些整除样本中继续下降，但 active-line
数量增长很快；这使“状态压缩 + 边界归纳”成为比直接 arrangement 更现实的证明路线。
对最高五层样本，partial states 的统计（从内层到外层）为
`(states,total,max)=(45,45,1),(30,72,3),(18,102,9),(9,120,22),(3,98,43)`；最终全局
nested envelope 只剩 70 条线。这给出了一个可量化的状态压缩目标：证明每层 active-line
数只按因子分解复杂度增长，而不是按完整 chain 数增长。

## 61. 六层边界趋势

继续运行 `scan_multilevel_boundary_dp.py --levels 6 --limit 128`，检查 13 个六层整除
层次。最高值为

$$
(96,48,24,12,6,2):\quad \frac{329}{317}\approx1.03785,
\qquad y/x=\frac12.
$$

其余非平凡样本均不超过 $93/91\approx1.02198$；多个层次在 $y/x=0$ 处恰好达到比值
1。三至六层的边界数据呈现一个稳定趋势：当前最大 overhead 出现在三层，增加层数后
反而下降。这是经验规律，不应直接当作 universal theorem，但它把“最坏层数是否为三”
列为一个新的可证伪猜想。

## 62. 随机层级抽样对“层数单调性”的修正

新增 `work/sample_multilevel_boundary.py`，固定 seed=20261003、每层 10 个样本、
$P_1\le300$，用同一 exact boundary evaluator 抽取乘法因子序列。一次可复现实验输出：

```text
levels=3 checked=10 best=484/443 = 1.092550790
levels=4 checked=10 best=438/401 = 1.092269327
levels=5 checked=10 best=1164/1063 = 1.095014111
levels=6 checked=10 best=77/74 = 1.040540541
```

这修正了“层数增加后比值严格下降”的直觉：局部随机样本中五层可以略高于某些三层或
四层样本；但它仍远低于已知三层极值 $535/427$。因此目前只能保留较弱猜想：在给定
总规模和因子约束下，三层可能产生全局最坏 overhead；层数单调性本身没有证据。

## 63. 凸包加速与复合 $p$ 三层族的新高值

新增 `work/scan_multilevel_boundary_hull.py`，用按斜率排序的 exact monotone hull 替代一维
line envelope 的两两交点枚举。它与原始 $O(n^2)$ pruner 在 $(30,15,3)$、$(230,115,5)$
和五层样本上给出相同的 exact ratio。借此把三层整除扫描扩大到 $P_1\le1000$ 的 11217
个层次，最高边界值变为

$$
(954,477,9)=(2\cdot9\cdot53,9\cdot53,9):\quad
\frac{726}{535}\approx1.3570093,\qquad y/x=\frac19.
$$

对 $(2pq,pq,p)$ 但允许复合 $p$ 的专门脚本
`work/scan_composite_p_family.py` 又检查了 $p\le100,q\le1000$ 的 15000 个 $(p,q)$ 对。
最高样本是 $p=99,q=997$，比值 $14817/10034\approx1.4766793$；取同一 $p=99$、更大
的 $q=10007$ 时比值升到约 $1.49087$。这说明复合因子的 divisor structure 会改变有限
参数公式，但仍把该族的极限推向 $3/2$，没有发现超过 $3/2$ 的证据。

## 64. $p=99$ 复合族的解析 endpoint certificate

新增 `work/prove_composite_p_q_witness.py`。对

$$
(P_1,P_2,P_3)=(198q,99q,99),\qquad (z,y)=(1,1/99),
$$

在 $q_0=997$ 处枚举所有 162 个 independent grids 和 162 条合法 nested chains，并把每个
cost 写成 $A+B/q$。目标 grids 是 $(q,11,18)$、$(q,9,11)$、$(99,1,1)$；目标 nested
chain 是 $((99,2,q),(99,1,q),(99,1,1))$。脚本在 $q=q_0$ 与 $q=\infty$ 两个 endpoint
都验证目标不大于所有 competitor，输出 `certificate=True`。

因此对所有更大的素数 $q\ge997$，有精确公式

$$
I(q)=\frac{199q+2277}{6534q},\qquad
N(q)=\frac{9q+7}{198q},\qquad
\frac{N(q)}{I(q)}=\frac{297q+231}{199q+2277}.
$$

其极限为 $297/199\approx1.4924623$；例如 $q=10007$ 时约为 $1.49087$。这把复合因子
导致的高 overhead 从数值搜索提升为可复核的解析 witness，同时仍低于 $3/2$。

## 65. 自动发现的复合 $p$ endpoint 规律

新增 `work/discover_composite_certificates.py`，在固定 $q_0=997$ 处自动选择
$t=1/p$ 的 independent/nested minimizers，并检查 $q_0$ 与 $q=\infty$ 两端。对
$3\le p\le100$ 的 49 个奇数 $p$，全部通过 endpoint certificate，且极限统一为

$$
\lim_{q\to\infty}R_p(q)=\frac{3p}{2p+1}.
$$

偶数 $p$ 中 48/49 个也通过了某个因子结构相关的 endpoint 公式，只有 $p=100$ 在
$q_0=997$ 时目标 independent line 尚未稳定。这个结果把原先的“素数平方自由族”推广为
强证据：奇数复合 $p$ 并不改变 $3p/(2p+1)$ 的渐近形式，只改变 $1/q$ 修正项；真正的
普适 $3/2$ 下界可以沿奇数复合 $p\to\infty$ 的方向继续构造和证明。

## 66. 奇数 $p$ 的渐近机制（待形式化为一般引理）

endpoint 数据揭示了一个比“素数 witness”更一般的结构。固定奇数 $p$，取 $q\to\infty$
且 $q\nmid 2p$，在 $t=y/x=1/p$ 处，independent envelope 的极限候选可取

$$
(q,1,2p),\qquad(q,1,p),\qquad(p,1,1),
$$

给出

$$
I_\infty(p)=\frac{3}{p}+\frac{3}{2p^2}.
$$

nested envelope 的候选 chain $((p,2,q),(p,1,q),(p,1,1))$ 给出 $9/(2p)$。对奇数 $p$
的数值 endpoint certificate 显示其它 q-placement 不会更低，因此极限统一为

$$
R_\infty(p)=\frac{3p}{2p+1}.
$$

下一步是把“q 位于第一/第二/第三坐标”的三种情况分别化成关于 $p$ 的整数不等式；这
可能给出任意奇数复合 $p$ 的正式渐近引理，而不再依赖逐个 endpoint enumeration。

## 67. 奇数 $p$ 渐近 witness 的正式证明

这一引理现在可以直接证明。固定任意奇数整数 $p\ge3$，令 $q$ 取不整除 $2p$ 的素数并令
$q\to\infty$。在 $t=y/x=1/p$ 处，若 grid $g=(a,b,c)$ 的总处理器数为 $P=abc$，则

$$
H_g(1,1/p)=\frac{b+c+a/p}{P}.
$$

对 independent envelope：在 $P=2pq$ 时，若 $q$ 位于第一坐标 $a=q\alpha$，极限成本为
$\alpha/(2p^2)$，最小值由 $\alpha=1$ 达到；若 $q$ 位于第二或第三坐标，极限至少为
$1/(2p)$，更大。故第一层极限为 $1/(2p^2)$。同理第二层 $P=pq$ 的极限为 $1/p^2$。
第三层满足

$$
\min_{abc=p}\frac{b+c+a/p}{p}=\frac3p,
$$

因为 $a=p,b=c=1$ 达到 3，而 $a<p$ 时 $bc>1$ 从而 $b+c\ge3$。于是

$$
I_\infty(p)=\frac3p+\frac3{2p^2}.
$$

对 nested envelope，$q$ 在前两层必须位于同一坐标。若它位于第二或第三坐标，则前两层
极限至少为 $1/(2p)+1/p$，再加第三层的 $3/p$ 已得到 $9/(2p)$。若它位于第一坐标，
写第二层的 q-free 因子为 $r$、第三层第一坐标为 $d\mid r$。前两层至少贡献
$3r/(2p^2)$，第三层写成 $(d,b_3,c_3)$、$b_3c_3=p/d$ 后，乘以 $p$ 的总成本至少为

$$
\frac{3r}{2p}+b_3+c_3+\frac d p.
$$

若 $d=p$，该量为 $9/2$；若 $p/d=3$，则 $b_3+c_3\ge4$ 且 $r\ge d$；若 $p/d\ge5$（因 $p$
为奇数，商也是奇数），则 $b_3+c_3\ge6$。三种情况都不小于 $9/2$。因此

$$
N_\infty(p)=\frac9{2p},qquad
\lim_{q\to\infty}\frac{N}{I}=\frac{3p}{2p+1}.
$$

这给出了任意奇数复合 $p$ 的正式渐近 witness；令奇数 $p\to\infty$ 即得到普适 overhead
常数至少为 $3/2$，不需要把 $p$ 限制为素数或平方自由数。
`work/check_odd_p_asymptotic.py` 对 $3\le p\le100$ 的 49 个奇数做了 exact endpoint sanity
check，输出 `checked=49 odd-p endpoint formula cases`。

## 68. 固定 witness 点的有限-$q$ $3/2$ 上界

在上一节的 witness 点 $(z,y)=(1,1/p)$，可以去掉 $q\to\infty$ 假设。对任意奇数 $p\ge3$
和素数 $q>p$，令 $t=1/p$。因为

$$
H_{(a,b,c)}=\frac{b+c+a/p}{abc},
$$

按 $q$ 所在坐标分类可得三层 independent minima 的统一下界

$$
I(p,q)\ge \frac3p+\frac3{2p^2}+\frac3{pq}=:L(p,q).
$$

例如第一层在 $q$ 位于 $a$ 时有
$H\ge1/(2p^2)+1/(pq)$；若位于 $b/c$，常数项已经足够大。第二层同理有
$H\ge1/p^2+2/(pq)$；第三层恒有 $H\ge3/p$。

合法 nested chain

$$
((p,2,q),(p,1,q),(p,1,1))
$$

的成本为

$$
U(p,q)=\frac9{2p}+\frac7{2pq}.
$$

直接计算

$$
\frac32L(p,q)-U(p,q)=\frac9{4p^2}+\frac1{pq}>0,
$$

于是该固定 aspect-ratio 点上有 $N\le U\le\frac32 I$。新增
`work/prove_boundary_point_three_halves.py` 对 $p\le99$ 的奇数和 $q\le127$ 的所有 787
个参数对做了 exact check。这个结果不是完整二维或完整边界定理，但严格覆盖了产生
$3/2$ 必要下界的同一 witness 点。

## 69. 大复合参数的二维快速定位：\(p=99,q=997\)

为检查复合族的最大有限参数是否仍落在同一条边界上，新增了
`work/exact_multilevel_2d.py --float-locator`。它先用浮点数枚举二维 arrangement 的候选
交点，再对浮点扫描得到的最优点用 `Fraction` 精确回代；这适合定位候选点，但不等同于
逐个精确验证全部候选顶点。

对

$$
(P_1,P_2,P_3)=(197406,98703,99)=(2\cdot99\cdot997,99\cdot997,99)
$$

输出为

```text
float locator ratio 1.4766792904125972
exact winner (z,y)=(1,1/99)
I=100340/3257199, N=4490/98703
points=6206137
partial stats ((162,162,1),(54,128,3),(18,100,8))
```

精确回代的比值为

$$
\frac{N}{I}=\frac{14817}{10034}\approx1.4766792904,
$$

与边界扫描和复合族 endpoint 证书一致。这个实验强化了“高 overhead witness 位于
\(y/x=1/p\) 边界”的猜想，也显示大参数二维 arrangement 已经达到数百万候选点；后续若要
把它升级为定理，需要对浮点定位出的 winning cell/顶点做精确可行性与全局支配验证，或
发展不依赖显式 arrangement 的符号 envelope 证明。

## 70. 2022--2024 并行紧下界文献核查（截至 2026-10-03）

针对“这些年是否出现了新的并行紧下界”做了定向检索。当前能确认的主线不是一个新的
通用 GEMM 多层定理，而是把紧常数、非对称内存和结构化核逐步补齐：

1. **Al Daas–Ballard–Grigori–Kumar–Rouse (2022)**：`Tight Memory-Independent Parallel Matrix
   Multiplication Communication Lower Bounds`。结果针对并行经典矩阵乘法的 memory-independent
   项，按矩阵 aspect ratio 分三种情形给出紧常数，并给出达到这些常数的并行算法。这填补的是
   distributed-memory 的强 scaling / 输入输出规模项，不是任意多层层次结构的统一定理。
   见 <https://arxiv.org/abs/2205.13407>。
2. **Al Daas et al. (2023, SIAM Journal on Matrix Analysis and Applications)**：`Communication Lower Bounds and
   Optimal Algorithms for Multiple Tensor-Times-Matrix Computation`。它把 HBL/几何不等式和约束
   非线性优化用于 Multi-TTM，并构造逻辑处理器网格达到并行下界；这是 tensor contraction 的
   紧结果，说明方法可以超越 GEMM，但不直接解决 GEMM 的 arbitrary multilevel 问题。
   见 <https://doi.org/10.1137/22M1510443>。
3. **Al Daas et al. (2024)**：`Communication Lower Bounds and Optimal Algorithms for Symmetric
   Matrix Computations`。对 SYRK、SYR2K、SYMM 同时给出 sequential 和 distributed-memory
   lower bounds，并用 triangular block partitioning 达到下界；这是结构化矩阵输入带来的新
   紧下界，而不是普通 GEMM 的新统一公式。见 <https://arxiv.org/abs/2409.11304>。
4. **Zhu–Hua–Jin (2024 accepted)**：`Joint-Communication Optimal Matrix Multiplication with
   Asymmetric Memories`。研究并行矩阵乘法中不同处理器拥有非对称内存时的 joint-communication
   下界，并给出匹配算法；它把“总通信量”与“各节点内存不均衡”耦合起来，仍属于单层并行
   通信模型。见 <https://doi.org/10.1007/s11390-023-3489-y>。

定向检索没有发现 2025--2026 年已经取代上述结果的“任意 \(L\ge3\) 层、允许跨层复用与复制、
同时对每一级 word/message/synchronization 都紧”的一般矩阵乘法定理。这个结论是检索范围内的
文献状态判断，不是对所有预印本的完备排除；因此后续应继续检查作者主页、DBLP 和 arXiv
更新。当前最清晰的研究缺口仍是：把 2022 的并行 memory-independent 紧常数、2024 的
非对称内存/结构化核结果，统一到可证明可达的 multilevel communication profile。

## 71. 精确 lower-envelope overlay：把大实例验证从“定位”升级为“全局证书”

浮点定位之后，新增 `work/exact_overlay_2d.py`。核心做法是：对三个 independent lower
envelope 和一个 nested lower envelope，先用有理数提取真正活动的 equality edge segment；
再只枚举这些边段的端点及跨 envelope 的交点。因为每个 overlay cell 上的
$N/I$ 是正分母下的 affine-fractional 函数，最大值必在 cell vertex 达到，所以这组候选
点足以完成 exact global check。

交叉验证结果：

```text
(30,15,3)       13/12
(56,28,14,2)    803/721
(80,40,20,4)    226/205
(60,20,10,2)    83/76
(48,24,12,6,2)  53/51
```

这些结果与原始全 arrangement 验证一致；最后一个实例的原始枚举很慢，而 overlay 只需
29 个候选点。

更大的复合实例

$$
(P_1,P_2,P_3)=(197406,98703,99)
$$

现在可以完全用 Fraction 验证：

```text
exact overlay ratio 14817/10034 = 1.4766792904125972
at (z,y)=(1,1/99)
I=100340/3257199, N=4490/98703
overlay points=74, active segments=167
```

因此原先的“浮点定位 + 精确回代”已升级为该参数的 exact global-max certificate；此前的
6206137 个 arrangement 候选点只是朴素枚举规模，不能再视为必要的证明成本。下一步可以
把 active-segment 提取推广成参数化的符号模板，从单个 $p=99$ 证书走向整个复合 $p$ 族。

## 72. $p=99$ 活动边段的参数稳定性

用 exact overlay 对同一复合族再检查两个更大的素数 $q$：

```text
q=10007:  R=297231/199367  ≈1.4908736150,  (z,y)=(1,1/99)
q=100003: R=14850561/9951437≈1.4923031719,  (z,y)=(1,1/99)
```

两个实例都得到完全相同的 `overlay points=74`、`active segments=167` 和 partial-envelope
统计。这与 endpoint certificate 给出的

$$
R(q)=\frac{297q+231}{199q+2277}
$$

一致，并为“$p=99$ 的活动集合在 $q\ge997$ 稳定”的参数化证明提供了额外实验依据；目前
仍需把这一稳定性从有限样本提升为对所有素数 $q\ge997$ 的符号不等式。

## 73. Overlay 算法的交叉验证

除前述五个基准实例外，又对

```text
(12,6,3), (18,6,3), (24,12,6), (36,18,6),
(40,20,10), (42,21,7), (54,27,9), (20,10,2)
```

与旧版全 arrangement 精确算法做了逐项比对。8 个实例的最大比值全部一致；其中
$(42,21,7)$ 和 $(54,27,9)$ 存在多个比值为 1 的最大点，所以两种算法返回的代表点不同，
但最优值相同。这说明 overlay 方法的目标是完整恢复 global maximum value，而不要求在
非唯一最大值时返回同一个顶点。

## 74. $p=99$ envelope-cover 的参数化稳定性证书

新增 `work/prove_p99_envelope_stability.py`，令 $u=1/q$。对任意素数 $q\ge997$，每个 grid
line 的三个系数都是 $u$ 的仿射函数。脚本取 $q_0=997$ 时的 active lines，并对每个
P1/P2/P3 grid line 以及每条 nested line 搜索一个 active dominator。

若 $D$ 是 candidate 与 dominator 的差值，则固定 $u$ 后它对 $(z,y)$ 是 affine function，
所以在域顶点 $(0,0),(1,0),(1,1)$ 取最小值；固定这些顶点后它对 $u$ 是 affine function，
所以只需检查 $u=0$ 与 $u=1/997$。exact check 输出：

```text
independent[0] total=162 active=56 uncovered=0
independent[1] total=54  active=24 uncovered=0
independent[2] total=18  active=10 uncovered=0
nested          total=162 active=51 uncovered=0
certificate=True for every prime q>=q0 at the envelope-cover level
```

这证明了：对整个素数尾部 $q\ge997$，所有 envelope 都可由同一组有限 active-line cover
描述；尚未完成的是在这组参数化 envelope 上证明哪个 overlay vertex 始终最大，以及由此
推出 $R(q)=(297q+231)/(199q+2277)$ 的全参数定理。

## 75. $p=99$ ratio-level 的部分参数化证书

新增 `work/check_p99_ratio_candidate_family.py`，在 $u=1/q$ 下把 $q_0=997$ 的 167 条活动
边段写成符号 equality lines，生成其 overlay 候选点，并对每个在 $q_0$ 可见的候选点选择
稳定的 envelope branch。目标边界比值写成

$$
R_*(u)=\frac{297+231u}{199+2277u}.
$$

脚本得到 2110 个符号候选表达式，其中 1292 个在 $q_0$ 位于域内，994 个的 envelope
branch 在 $q=997$ 与 $q=100003$ 间保持一致。对这 994 个候选，使用 SymPy 的精确有理
root-isolation 检查 $R_*(u)-R_{candidate}(u)$ 在 $u\in[0,1/997]$ 上的符号，输出：

```text
stable 994 bad endpoint 0
exact sign bad 0
certificate=True for the q0-visible candidate family
```

这是 ratio-level 的新证据，但仍明确是部分证书：它还没有证明 active-line cover 在整个参数区间
不会产生新的 equality edge，也没有把所有潜在的非-$q_0$ 可见候选纳入。因此当前结论仍应
表述为“固定活动边段候选族已通过符号支配检查”，而不是完整的 $q\ge997$ global-ratio
定理。

## 76. 固定 cover 上的 edge-template 扫描

新增 `work/scan_p99_edge_templates.py`，不比较数值 equality 系数，而是比较活动线的 pair
identity，从而消除 $q$ 缩放造成的表面差异。对

$$
q=997,1009,10007,100003,10^6
$$

对应的 $u=1/q$（其中 $10^6$ 只作为有理参数采样）逐层提取固定 envelope cover 的活动
边对，结果完全一致：

```text
independent[0] 60 edge pairs
independent[1] 29 edge pairs
independent[2] 12 edge pairs
nested         51 edge pairs
changed levels=[] at every sampled u>0
```

这个扫描支持 $u\in(0,1/997]$ 内 edge topology 不变；$u=0$ 是极限退化点，单独出现更少的
边对，不影响有限素数 $q$。它与第 39 节的 994 个 ratio 候选结合后，剩余的证明任务已经
缩小为：用符号事件排除替代有限采样，或直接证明这 60/29/12/51 个 edge-pair 模板在整个
开放区间保持可行。

## 77. Edge 端点的退化结构

为准备符号 edge-persistence 证明，检查了 $q_0=997$ 的活动边段端点。端点并非一般位置：
P1/P2/P3/nested 的非角点端点数分别为 112、41、13、76，而且每个端点通常同时满足多条
line equality；例如 P1 的一个端点最多有 56 个 active-line 支持关系。

这说明不能简单为每个端点指定唯一的“第三条约束”并沿参数延拓；必须先按 equality-line
几何类型去重，再处理多重共点的分支。这个退化现象解释了为什么直接的三线事件枚举会产生
大量伪事件，也把下一步证明策略限定为：使用 pair-identity 的边段覆盖和多重共点的统一
符号不等式，而不是逐端点追踪单一支撑线。

## 78. 奇数复合 $p$ 的 exact global-overlay 扫描

新增 `work/scan_odd_p_exact_overlay.py`，对固定素数 $q=997$ 的奇数 $p$ 直接运行 exact
lower-envelope overlay。13 个参数全部在 $(z,y)=(1,1/p)$ 达到 global maximum：

```text
p=  3  R=2245/1748       ≈1.28432494
p=  9  R=13470/9503      ≈1.41744712
p= 15  R=22450/15521     ≈1.44642742
p= 21  R=31430/21551     ≈1.45840100
p= 25  R=56125/38354     ≈1.46334150
p= 27  R=40410/27593     ≈1.46450187
p= 33  R=49390/33647     ≈1.46788718
p= 35  R=78575/53449     ≈1.47009299
p= 45  R=33675/22858     ≈1.47322600
p= 49  R=44002/29851     ≈1.47405447
p= 63  R=94290/63887     ≈1.47588711
p= 77  R=345730/234151    ≈1.47652583
p= 99  R=14817/10034      ≈1.47667929
```

这些包含大量复合因子的 $p$，且全部复现 $y/x=1/p$ 边界最大结构；比值随 $p$ 增大逼近
$3/2$。这是目前对“奇数复合 $p$ 的二维 global-max 边界猜想”最完整的一组 exact 证据，
但仍是有限参数扫描，不替代一般 $p,q$ 的符号证明。

## 79. 全部奇数 $p\le99$ 的 exact global 检查

将 `work/scan_odd_p_exact_overlay.py` 默认范围扩展为全部奇数
$3\le p\le99$，固定 $q=997$，共 49 个参数。每个实例的 exact overlay global maximizer
都严格位于

$$
(z,y)=(1,1/p).
$$

没有发现二维内部点、其它边界点或超过 $3/2$ 的异常。最大有限参数仍是
$p=99$：

$$
R=\frac{14817}{10034}\approx1.47667929.
$$

这次扫描覆盖所有奇数复合因子结构，而不是只抽取代表性 $p$；它显著加强了“奇数 $p$ 的
二维 global-max 位于 $y/x=1/p$”猜想，但仍然是有限 $p,q$ 的 exact 证据。

## 80. 第二个大 $q$：全部奇数 $p\le99$ 的复核

将同一 49 个奇数 $p$ 扫描重复到 $q=10007$。49/49 的 exact global maximizer 仍为
$(z,y)=(1,1/p)$；最大值仍由 $p=99$ 给出，

$$
R=\frac{297231}{199367}\approx1.490873615.
$$

$q=997$ 与 $q=10007$ 两组结果没有发现新的二维最大点或超过 $3/2$ 的案例。这说明边界
结构不是单个 $q$ 的偶然现象，并为后续 $q$ 参数化证明提供了第二个完整横截面。

## 81. 奇数族的有限-$q$ 公式模式

`discover_composite_certificates.py --p-max 99 --q0 997` 对 97 个 $p$ 找到 endpoint
证书；其中全部 49 个奇数 $p$ 的 witness chain 都给出同一个 nested 仿射式

$$
N_p(q)=\frac9{2p}+\frac7{2pq}.
$$

independent 项的常数部分也统一为

$$
I_{p,0}=\frac3p+\frac3{2p^2},
$$

但 $1/q$ 系数依赖 $p$ 的因子结构。这解释了为什么所有奇数 $p$ 的极限比值统一为
$3p/(2p+1)$，而有限 $q$ 的精确比值会随复合因子分配显著变化。结合两组完整二维扫描，
当前可记录的统一猜想是：

$$
\max_{0\le y\le z\le1}\frac{N}{I}
=\frac{N_p(q)}{I_p(q)}
\quad\text{at }(z,y)=(1,1/p),
$$

其中 $I_p(q)$ 的有限修正项需要按 divisor structure 分类证明。

## 82. divisor-structure 公式的 exact 验证

定义

$$
\sigma(n)=\min_{d\mid n}\left(\frac1d+\frac1{n/d}\right).
$$

新增 `work/check_odd_p_boundary_formula.py`，将 discover 得到的全部 49 个奇数 $p\le99$
endpoint lines 与下面的公式逐项比较：

$$
I_p(q)=\underbrace{\frac3p+\frac3{2p^2}}_{I_0(p)}
+\frac{\sigma(2p)+\sigma(p)}q,
\qquad
N_p(q)=\frac9{2p}+\frac7{2pq}.
$$

输出 `checked=49 odd-p divisor-formula cases`。其中 $σ(2p)$ 和 $σ(p)$ 分别记录 P1/P2 中
把 q 放在第一坐标时的最优 q-free 因子分配；这解释了复合 $p$ 的有限-$q$ 修正项为何不同。
该公式目前是 endpoint 族的 exact verified pattern，下一步是证明 q-placement 在一般奇数
$p$、足够大素数 $q$ 下确实由这些分配取得。

## 83. 奇数族 endpoint 公式的有限-$q$ 阈值推导

新增 `work/derive_odd_p_threshold.py`，把 $(z,y)=(1,1/p)$ 处的每条 grid line 和兼容
chain 写成

$$
H(q)=A+\frac{B}{q},
$$

其中 $q$ 是大于 $p$ 的素数。脚本对每个奇数 $3\le p\le99$ 枚举 endpoint 的全部
independent/nested 竞争项，精确解出目标项压过每个竞争项所需的整数阈值 $Q^*(p)$，并
取 independent 与 nested 两侧阈值的最大值。共检查 49 个奇数，最大的阈值为

$$
\max_{p\le99,\ p\text{ odd}} Q^*(p)=891,
$$

由 $p=99$ 达到；因此实验所用的 $q_0=997$ 已经严格超过所有这批 endpoint 证书的阈值。
例如 $p=81$ 的阈值为 729，$p=99$ 的阈值为 891。该计算把“足够大的 $q$”具体化为
可复核的有限比较，并支持前面的 divisor-structure 公式在 $q\ge Q^*(p)$ 时成立。

这一步仍然只证明了 endpoint witness 族的参数稳定性：它没有排除二维区域中随 $q$ 新出现
的 envelope edge，也没有单独证明 $(1,1/p)$ 是全局 ratio 最大点。因此下一步仍需把 endpoint
阈值证书与二维 overlay 的全局支配证明接起来。

## 84. 文献 checkpoint：截至 2026-10-03 的研究空白

子 agent 对 2022 之后的论文做了定向核查，报告保存在
`work/agent_reports/literature_gap.md`。目前能确认的进展是：Multi-TTM、SYRK/SYR2K/SYMM
把 HBL/几何不等式和 matching algorithm 扩展到结构化 kernel；JOMMA 把 horizontal 与
vertical communication 以及非对称读写成本合并到一个两级 joint objective；SFC-CA GEMM
在若干一层/两层 regime 匹配已有下界；overlap 工作讨论时间最优条件而非新的 word-volume
下界。

历史上也有 HCP 等特定层次化平台的多级通信下界和算法，因此“完全没有 multilevel bound”
是不准确的。更精确的 gap 是：目前没有看到同时适用于 classical GEMM、任意 $L\ge3$、
允许 replication/recomputation/跨层驻留并给出逐层 tight communication vector 的普适定理。

因此当前三层 overlay 不是重复已知定理，但也不能把它误写成已有论文的结论；下一步应明确
写成“新模型 + exact evidence + 待证 theorem”。

## 85. 四层 exact boundary 扫描与 retreat 计算资源

用 `work/scan_multilevel_boundary_hull.py` 的 Fraction-exact lower-envelope hull，在本地
复核了四层 hierarchy：

```text
limit=48:  35 hierarchies, max 226/207  ≈ 1.09178744
limit=72:  93 hierarchies, max 803/721  ≈ 1.11373093
```

随后把同一脚本和依赖复制到 `retreat` CPU 机运行：

```text
limit=120:  284 hierarchies, max 1331/1165 ≈ 1.14248927
limit=240: 1148 hierarchies, max 1137/916  ≈ 1.24126638
```

limit=240 的最大实例为 $(228,114,57,3)$，最大点参数为 $t=1/3$；所有已扫描实例都
没有超过 $3/2$。这不是多层下界证明，但把当前反例搜索从 93 个层级扩大到 1148 个 exact
层级，并说明 CPU 资源足够支持更大范围的系统搜索。下一步要记录每个实例的 independent
与 nested witness，而不是只保留最大 ratio，以便区分“ratio 小”与“逐层可兼容”。
## 86. p=99 topology-event 诊断：证明路线进一步收窄

新增 `work/scan_p99_topology_events.py`，对 p=99 的 fixed active-line cover 做参数
$u=1/q$ 的事件枚举。复核命令为 `PYTHONPATH=work python work/scan_p99_topology_events.py`，
输出：

```text
pair-domain unique polynomials = 258 (degree 1: 257)
triple determinant polynomials = 6356 (degree 1: 5980, degree 2: 375)
roots in (0,1/997): boundary 11, triple 205
actual active events = 0
```

这里 `actual events=0` 表示在候选根处，交点没有同时位于 aspect domain 内并改变对应
envelope owner；一次根筛选使用 Fraction exact，二次根目前使用数值过滤，因此这仍是强诊断
而非最终 Sturm 证书。若把 375 个 quadratic roots 用代数数区间和 Sturm 判号补齐，就能
把 p=99 的 fixed-cover 稳定性推进到完整的 topology lemma，再接 ratio-level sign proof。

## 89. 一般奇数 endpoint 公式：阈值定理与最小失败例

`work/agent_reports/odd_p_endpoint.md` 给出了 endpoint 处的一个可证 lemma：当
$P_k=kpq$、$k\in\{1,2\}$ 且 $q$ 只出现在一个 processor-grid 坐标时，每条 grid/chain
cost 都是 $A+B/q$。因此 divisor-structure 目标线一旦压过有限竞争集，就对所有更大的
$q$ 保持最优；`derive_odd_p_threshold.py` 对 $p\le99$ 的 49 个奇数给出最大阈值
$Q^*=891$。

这也发现了一个重要边界：divisor 公式不能写成所有 $q>p$ 都成立。最小测试失败为
$(p,q)=(9,11)$：实际 independent cost 为 $400/891$，而 divisor target 线不是最优；
nested cost 为 $53/99$，实际 ratio 为

$$
R=\frac{477}{400}=1.1925.
$$

因此正确的 theorem 形状必须带显式 crossing threshold $q\ge Q^*(p)$；endpoint 公式本身
仍未解决二维 global maximizer 问题。

## 88. p=99 quadratic event 的 Sturm 修正与 exact 结果

`work/check_p99_quadratic_sturm.py` 已修正 SymPy `count_roots` 对区间端点的计数问题：原先
报告的 4 个“区间根”实际上全部是 $u=0$ 的端点退化。修正后输出为：

```text
quadratic_unique=375, source_triples=523
sturm_roots_open_interval=0, endpoint_polys=4
certificate=True
```

四个端点多项式均满足 `at0=True, atu0=False`，且在 $u=0$ 的交线方向退化为
`parallel_or_coincident`；不存在 $(0,1/997)$ 内的 quadratic triple-concurrence root。
因此 p=99 fixed active-line cover 的 topology 稳定性现在有了完整的 Sturm root-count 证书，
但 $u=0$ 退化端点仍需和 ratio-level sign proof 单独拼接，不能直接把完整 p=99 theorem
写成已完成。

## 87. 反例搜索周期的可审计结果

`work/agent_reports/counterexample_search.md` 汇总了本轮 CPU 扫描：三层 limit=500 共 4107
个 hierarchy，最大 $1075/823\approx1.30620$；`retreat` 上三层 limit=1000 共 11217 个，
最大 $726/535\approx1.35701$，位于 $(954,477,9)$、$t=1/9$。composite family
$p\le30,q\le300$ 的 1556 个 endpoint 参数中最大为 $16525/11426\approx1.44626$，位于
$(p,q)=(25,293)$。四层 limit=480 在 `retreat` 上检查 4077 个 hierarchy，最大
$2275/1776\approx1.28097$，位于 $(460,230,115,5)$、$t=1/5$。

本轮没有找到反例，但这些结果只适用于当前 $H$ proxy、坐标整除型 nested chain 和边界
$z/x=1$；它们不能替代完整二维或实际 message-volume theorem。可保留的受限命题是：若
各层 independent optimum 能选成坐标逐层整除的兼容链，则 nested overhead 恰为 1；额外
开销来自 envelope breakpoint 附近的兼容性损失。
## 90. p=99 ratio-level wrapper 通过

新增 `work/check_p99_ratio_all_u.py`，把正参数区间的 994 个 symbolic candidate sign checks
和 $u=0$ 的退化 overlay 合并运行。命令
`PYTHONPATH=work python work/check_p99_ratio_all_u.py` 输出：

```text
positive_u_candidates 994
positive_u_exact_sign_failures 0
u0_edge_counts (4, 4, 12, 28)
u0_overlay_points 12 segments 48
u0_best_ratio 297/199 at (1,1/99)
certificate=True
```

结合 quadratic Sturm 证书、linear event 的 exact owner-gap scan 和固定 active-cover，当前
p=99 已经形成一个接近完整的参数化 global-ratio certificate。还需把“无 active event 则
candidate branches 覆盖所有正 $u$ overlay vertices”写成正式 combinatorial-continuity lemma，
以及把 $u=0$ 的退化情况单独纳入定理陈述；因此目前仍标记为 proof certificate nearly closed，
而不是已发表意义上的最终 theorem。
## 91. p=99 固定参数的证明桥梁已闭合（计算证书层面）

第三轮新增 `work/check_p99_linear_events.py`，并复核 `work/check_p99_quadratic_sturm.py`：

```text
active_vertex_events 0
parallel_roots 57 active_pair_parallel_roots 0
positive_u_identity_roots 0
active_linear_triple_events 0
quadratic_unique 375 sturm_roots_open_interval 0
```

再加上 `work/check_p99_ratio_all_u.py` 的 994 个正 $u$ candidate exact sign checks 和
$u=0$ 的 exact overlay，当前计算证书支持以下固定参数结论：对所有素数 $q\ge997$，

$$
\max_{0\le y\le z\le1}\frac{N(z,y)}{I(z,y)}
=\frac{297q+231}{199q+2277},
$$

最大点为 $(z,y)=(1,1/99)$。这已经超出有限扫描，达到固定 $p=99$ 的参数化定理级证据；
正式写作仍需把“无 active topology event $⇒$ overlay cell complex 不变”的组合拓扑 lemma
单独陈述，并明确该结论只覆盖固定 $p=99$，不是一般奇数 $p$ 或任意多层 theorem。
## 92. 一般素数 p 的 endpoint 公式符号证明

`work/prove_prime_p_family.py` 对素数 p 的 endpoint 竞争做了 132 个 Bernstein exact
polynomial checks，`prove_prime_chain_dominance_symbolic.py` 对 11 个非模板 compatible
chain 做了符号支配检查。结果是对所有 $p\ge3$ 的素数和 $q>p$：

$$
I_p(q)=\frac3p+\frac3{2p^2}+\frac{3/2+2/p}{q},
\qquad
N_p(q)=\frac9{2p}+\frac7{2pq},
$$

并得到 endpoint ratio

$$
R_p(q)=\frac{p(9q+7)}{(6p+3)q+3p^2+4p}.
$$

这一步把 prime-p endpoint 结论从数值扫描升级为一般符号证明；它仍然不等于二维
global-max 定理，复合 p 也仍需 divisor-structure 分类。
## 93. p=3 probe: endpoint stable on prime q, fixed-cover candidate for q>=67

本轮继续用 CPU 级 exact enumeration 完成了小素数 $p=3$ 的三层 probe。直接 exact
overlay 检查了小于 300 的全部 60 个 prime $q$，都由
$(z,y)=(1,1/3)$ 取得最大值，且等于

\[
R_3(q)=\frac{27q+21}{21q+39}.
\]

但 composite $q$ 的 divisor structure 会破坏这个表达式：$q=44$ 的 exact 最大值是
$311/299$，而 endpoint expression 给出 $403/321$。因此不能把 prime-$q$ 观察写成
所有整数 $q>p$ 的定理。

更关键的是，anchor 需要精确选择。早期辅助脚本的 floor bug 曾产生 $2/87$ 和 $2/141$，
这些数值已撤销。修正 symbolic replacement 后，$q_0=29,47,61$ 都有同一个 active
triple event $u=1/66$、位置 $(z,y)=(0,0)$；取 $q_0=67$ 后，exact quadratic Sturm
scan（31 个 unique determinants）和 linear event scan 都没有 active event，ratio
candidate 的 54 个分支也全部通过 exact sign check。因此 p=3 现在有一个与 p=99 同型的
fixed-cover 证书候选，覆盖目标为 prime $q\ge67$。`prove_p3_envelope_stability.py` 对全部
27/9/3 independent grids 与 27 条 nested chains 给出 uncovered=0；随后 54 个 ratio
branches 通过 exact sign check。仍需把 continuity lemma 写成正式证明。

可复现记录见 `work/agent_reports/p3_probe.md`，脚本为
`work/check_p3_quadratic_sturm.py`、`work/check_p3_linear_events.py` 和
`work/p3probe/check_p3_ratio_candidate_family.py`。
## 94. Corrected symbolic pipeline extends the fixed-cover certificate to p=3,5,7

审计后修正了 topology 辅助脚本中含 anchor prime 的 reciprocal replacement：若 grid
含有 $q_0$ 因子，$1/(d q)$ 必须写成 $u/d$，不能使用整数 floor。修正后以 $q_0=67$
重新检查 $p=3,5,7$：

```text
independent[0] total=27 active=16 uncovered=0
independent[1] total=9 active=8 uncovered=0
independent[2] total=3 active=3 uncovered=0
nested total=27 active=16 uncovered=0
```

三者的 quadratic Sturm 与 linear-event scans 都在 $0<u\le1/67$ 排除了 active event；
ratio candidate 的 exact sign failures 均为 0，分支数分别为 54、37、31。候选最大值是

$$
R_p(q)=\frac{p(9q+7)}{(6p+3)q+3p^2+4p},
$$

位于 $(z,y)=(1,1/p)$。另外，direct exact-global 检查覆盖了 $p=5$ 的 43 个和 $p=7$
的 42 个 prime-$q$ 实例；$p=3$ 已检查 300 以下全部 60 个素数。这个结果把小素数族
的证据从单独的 p=99 推进到 p=3,5,7，但还不是任意 p 的定理；$p\ge23$ 可能需要更大
anchor，且 continuity lemma 仍需正式写出。

详细记录见 `work/agent_reports/small_prime_fixed_cover.md`。
## 95. p=99 topology certificate audit correction

对早期 p=99 topology 脚本做了 reciprocal replacement audit：旧脚本把含 $q_0$ 因子的
$1/(d q)$ 错写成了 floor，导致旧日志中的 375/523 与 57 个 parallel-root 数字不再是
权威结果。修正后重新运行得到：

```text
quadratic_unique 1405 source_triples 11219
sturm_roots_open_interval 0 endpoint_polys 146
parallel_roots 0 active_pair_parallel_roots 0
active_linear_triple_events 0
```

`check_p99_ratio_all_u.py` 仍给出 994 个 positive-$u$ branches、0 个 exact sign failure，
以及 $u=0$ slice 的最大值 $297/199$。因此 p=99 的结论方向没有改变，但旧计数必须视为
历史诊断值；当前证书应以 corrected scripts 和 `work/agent_reports/p99_sturm.md` 为准。
## 96. Prime-p anchor scan: topology threshold near q0>2p

修正后的 pipeline 已扫描
$p=3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97,101$。
对 $p\le31$ 使用 $q_0=67$；对更大的 p 使用测试到的、严格大于 $2p$ 的下一个素数
anchor。每个实例都通过：全部 grid/compatible chain 的 envelope dominance、quadratic
Sturm + owner/domain filtering、linear event scan，以及 ratio candidate 的 exact sign
check。候选值始终是

$$
R_p(q)=\frac{p(9q+7)}{(6p+3)q+3p^2+4p}
$$

在 $(z,y)=(1,1/p)$ 处取得。

这支持一个新的受限猜想：对 prime p，global-ratio threshold 可能在 $q_0>2p$ 附近；但
尚未成为定理，因为 continuity lemma 尚未写出。复合 $p=99$ 是明显例外：$q_0=199$ 时
topology 已稳定，但有 204 个 ratio-branch sign failures；$q_0=997$ 才通过。这把
topology threshold 与 ratio threshold 清楚地区分开来。完整表格见
`work/agent_reports/prime_p_anchor_scan.md`。
## 97. Finite-arrangement continuity lemma drafted

把固定-anchor 证明的核心桥梁写成了 `work/agent_reports/continuity_lemma.md`。其内容是：
对系数 affine in $u=1/q$ 的有限 line families，如果没有 boundary passage、active
parallelism、active triple concurrence 或 active line identity，那么每个 lower-envelope 的
active edge complex 在连通参数区间内保持组合不变；四个 envelope 的 overlay vertices 因而
是固定的 rational branches。每个 cell 内 $N/I$ 是正分母下的 linear-fractional function，
所以只需检查这些 vertex branches 的一元 sign inequalities。

这把 p=3--101 的扫描结果连接到可写证明的结构。随后又把 quadratic owner filtering
升级为 isolated algebraic roots 上的 polynomial gcd/Sturm sign checks，而不是 midpoint
近似；仍需把任意 anchor 的 candidate line family 写成一般公式，并单独处理 $u=0$
退化 slice。
## 98. 证明目标的重新分层

现有 `prove_prime_three_halves_average.py` 已经给出素数 family
$(P_1,P_2,P_3)=(2pq,pq,p)$ 的全域上界 $N/I\le3/2$，而 witness 的双重极限达到
$3/2$，所以这个受限 family 的 supremum 已经确定。当前 prime-p anchor scan 研究的是
更强的有限参数命题：是否总能把 $3/2$ sharpen 成

$$
R_p(q)=\frac{p(9q+7)}{(6p+3)q+3p^2+4p}
$$

并证明最大点为 $(1,1/p)$。这解释了为什么 q0=199 对复合 p=99 的 topology 已足够，
却不足以通过 ratio certificate：$3/2$ 上界已经成立，失败只发生在更锋利的有限-q 比较。
## 99. 文献边界复核

近期原始论文复核后，不能把“并行 GEMM 紧下界”本身当作空白：2022 已有 rectangular
classical GEMM 的 memory-independent tight constants 与匹配 1D/2D/3D algorithms；
2024/2025 又扩展到 SYRK/SYR2K/SYMM、Multi-TTM 和 asymmetric-memory joint communication。

更准确的研究 gap 是：在 nested processor-grid compatibility、跨层 residency/replication、
非对称容量和任意 $L\ge3$ 层同时存在时，能否给出统一的 per-level communication profile，
并由同一个 schedule 同时达到各层 bound。文献链接已补入总笔记第 64 节。

## 100. Direct exact-global scan completed

`check_prime_p_global.py` completed 141 exact overlay cases for
$p=23,29,37,47,59,71,83,97$ and multiple prime q values. Every case put the maximum at
$(z,y)=(1,1/p)$ with the candidate
$R_p(q)=p(9q+7)/((6p+3)q+3p^2+4p)$. This extends the direct checks beyond p=3,5,7, but remains
computational evidence pending a parameterized proof.

## 101. Radial derivative certificate

在坐标 $(1,s,st)$ 下，每个 active cell 的 ratio 对 s 的导数分子是 affine-in-t。新的
`work/check_prime_radial_cells.py` 用 exact half-plane feasibility 去掉退化边界组合，并对
$p=3,q=29$、$p=5,q=29$、$p=23,q=67$、$p=37,q=79$、$p=97,q=197$ 全部得到
`feasible_cells=8 bad=0`。八类 cell 的导数公式已写入
`work/agent_reports/radial_monotonicity_certificate.md`；在 $q>2p$ 下可直接证明这些公式
在各自 t 区间非负。剩余关键问题是把八类 active-cell 模板本身推广为任意 prime $p,q$ 的
参数化 envelope 分类。

## 102. Expanded boundary and radial evidence

边界公式的 exact regression 已扩大到 425 个 $(p,q)$ 参数对（$p\le101$ 的代表素数与多组
$q$），全部通过。独立的径向 exact rational grid scan 以步长 $1/80$ 检查了 52 个参数组合，
全部 `monotone=True`；这些数字支持八-cell 参数化路线，但不替代 active-cell 分类证明。

## 103. Symbolic radial derivative script

新增 `work/prove_prime_radial_derivatives.py`，独立用 SymPy 推导八类模板的 $D(t)$，并验证
$q=2p+r$ 下 $A(p,q)<0$ 的正项分组；脚本输出
`symbolic derivative certificate=True under p>=3, q>2p`。因此当前瓶颈已经明确落在
active-cell 分类，而不是径向导数的符号计算。

## 104. Four-chain upper-envelope reduction

新增 `work/check_prime_four_chain_bound.py`。它只保留四条合法 nested chains，构造上界
$U\ge N$，然后对 $U/I$ 做 exact arrangement 和 radial-cell 证书；在见证点检查 $U=N$。
对 19 个 $q>2p$ 实例全部得到 exact maximum $R_p(q)$、`cells=8`、`radial_bad=0`、
`witness_equality=True`。这比分类全部 nested envelope 更简洁；普适剩余问题是证明该四-chain
上界的八-cell active template。

## 105. Symbolic independent-cover proof

`work/prove_prime_independent_cover.py` 对固定的 16/8/3 candidate grids 做了参数化 dominance
检查：12 个 omitted grids 全部被某条 candidate line 在三角域上支配，且在
$p=3+a,q=2p+r$ 下符号系数非负。脚本输出
`symbolic independent-cover certificate=True omitted=12`。因此当前瓶颈已从 independent
envelope 本身收窄到四链上界的八-cell arrangement。

## 106. Full restricted three-level theorem

八-cell 分类不再是必要缺口。固定 independent candidate lines 后，$I$ 可写成
$m_0=\min(A,B,C,D,E)$、$m_1=\min(F,G)$、$H$；四条 legal chains 给出 $U\ge N$，且
$U$ 的 min 只需三个 t-regime。所有可能的 $(U,m_0)$ 组合对应七个径向导数，均已在
$q>2p,p\ge3$ 下证明非负。边界定理和 $(1,1/p)$ witness equality 随即闭合完整二维结论。

证明报告：`work/agent_reports/prime_family_full_theorem.md`；代数脚本：
`work/prove_prime_full_2d_upper_bound.py`，输出
`full two-dimensional upper-bound algebra certificate=True`。

## 107. Composite-p counterexample search

对 composite p 做 exact stress test 后，素数族公式不再成立。$(p,q)=(6,13)$ 的完整二维 exact
arrangement 给出 `max ratio=135/113`、位置 $(1,29/195)$，高于 $248/213$；$(49,101)$
给出 `11221/8039`，高于 `11221/9349`。`scan_composite_formula_gap.py` 对 p<=50、q<=500
发现 1247 个 boundary counterexamples。下一条研究线应从“任意 p 的同一公式”改为“按 divisor
profile 分类的三层 envelope”。

## 108. Interior composite counterexamples

新增 exact 2-D 结果：$(p,q)=(10,23)$ 的最大值 `4531/3666` 在
$(z,y)=(49/115,1/5)$；$(14,29)$ 的最大值 `248675/196974` 在
$(61/145,1/7)$。两者超过边界最大值，说明 composite divisor profile 会产生真正的
interior maximizer；下一步必须研究因子分解驱动的二维 envelope。

## 109. Remote exact composite checks: p=22 and p=26

使用 retreat CPU 完成两个更大的完整二维 exact arrangement。对 $(p,q)=(22,47)$，层级为
$(2068,1034,22)$，得到

$$
\max N/I=\frac{1005565}{775602}\approx1.2964961411,
\qquad (z,y)=\left(\frac{97}{235},\frac1{11}\right).
$$

对 $(p,q)=(26,53)$，层级为 $(2756,1378,26)$，得到

$$
\max N/I=\frac{1505465}{1155702}\approx1.3026411653,
\qquad (z,y)=\left(\frac{109}{265},\frac1{13}\right).
$$

相应的素数族公式分别只有 $1892/1577\approx1.1997464$ 与
$12584/10559\approx1.1917795$，所以这不是舍入误差，而是显著的 divisor-profile gap。

两者都由 54/27/9 个候选 grids、24/16/8 个 active independent lines 和 31 条 active
nested lines 组成；arrangement vertices 分别为 289015 与 291599。结果继续支持：对
复合 $p=2r$，最大点可能沿 $y=1/r$ 出现，但 $z$ 与比值由额外 divisor profile 决定，
不能套用素数族的 $R_p(q)$。

对四个 exact cases $p=2r, q=4r+3$（$r=5,7,11,13$），active-line pattern 相同，且
最大点与比值可写成候选子族公式

$$
(z,y)=\left(\frac{2q+3}{5q},\frac1r\right),\qquad
\frac NI=\frac{5qr(8q+13)}{28q^2r+15q^2+6qr^2+52qr+9r^2}.
$$

这只是由 active lines 代入得到的 conjectural subfamily，不是任意 composite $p$ 的定理；
下一步应证明这些 lines 的 dominance 条件，并检查 $q$ 穿越 divisor thresholds 时何时失效。

## 110. Targeted literature refresh (2026-10-03)

针对“并行紧下界是否出现新总突破”做了定向检索。当前可核实的主线仍是：2022 年
rectangular classical GEMM 给出三种 processor-grid regime 的 memory-independent tight
constants 及 matching 1D/2D/3D algorithm；2024 年把同一方法扩展到 SYRK/SYR2K/SYMM；
2025 年 JOMMA 处理 asymmetric memories 下的 horizontal/vertical joint communication。
检索没有发现取代这条 general GEMM theorem 的新统一结果。因此研究价值更可能在
multilevel、nested-grid compatibility、replication 和 divisor-profile 这类结构化模型，
而不是重新声称“并行 GEMM 尚无紧下界”。

## 111. Exact completion for p=18, q=37

retreat 上长时间运行的 exact arrangement 已完成。对 $(p,q)=(18,37)$，层级为
$(1332,666,18)$，得到

$$
\max N/I=\frac{13905}{10826}\approx1.2844079069,
$$

最大点为

$$
(z,y)=\left(1,\frac{77}{1665}\right).
$$

候选 grids 数为 108/54/18，active independent lines 为 38/25/11，active nested lines
为 52，arrangement vertices 为 2071814。素数族公式在此只给 $120/101\approx1.18812$，
因此 $p=18$ 进一步确认：即便 $p=2r$ 的若干实例呈现规则子族，换一个 divisor profile
（这里 $r=9$）就可能改变最大点的位置和公式。

对四个正例，最小 nested envelope 都由同一组四条 chain 产生（从内层到外层）：

```text
(r,2q,2) -> (r,2q,1) -> (r,2,1)
(2r,q,2) -> (r,q,2)   -> (r,1,2)
(2r,q,2) -> (2r,q,1)  -> (2r,1,1)
(2r,2q,1) -> (r,2q,1) -> (r,2,1)
```

对应 independent minimizers 为 $(q,r,4)$、$(q,r,2)$、$(r,2,1)$。这把下一步证明任务
具体化为：在 $r,q$ 为相应素数且 $q=4r+3$ 时，排除所有额外 divisor grids；而 $r=9$
的反例正好说明这个排除步骤需要素因子条件。

新增 `work/check_2r_prime_subfamily.py`，对 $r=5,7,11,13,17$、$q=4r+3$ 做 exact
local-envelope check；五个实例都得到同一组 independent/nested pattern 和候选闭式比值。
新样本 $r=17,q=71$ 的候选点为 $(29/71,1/17)$、候选比值为 $701267/532722$。这仍是
局部证书；其全局 arrangement 已在下一节由 retreat 完成。

## 112. Global exact confirmation for p=34, q=71

retreat 完成了 $p=34=2\cdot17$, $q=71=4\cdot17+3$ 的全局 exact arrangement：

$$
\max N/I=\frac{701267}{532722}\approx1.3163845308,
\qquad (z,y)=\left(\frac{29}{71},\frac1{17}\right).
$$

候选 grids 为 54/27/9，active independent lines 为 24/16/8，active nested lines 为 31，
arrangement vertices 为 296028。结果与候选子族公式完全一致；素数族公式只有
$21964/18301\approx1.200153$。因此该子族已获得五个 exact global cases 的支持，
但仍不是任意 composite $p$ 的定理。

## 113. Global exact confirmation for p=38, q=79

retreat 又完成 $p=38=2\cdot19$, $q=79=4\cdot19+3$：

$$
\max N/I=\frac{4840725}{3666242}\approx1.3203506479,
\qquad (z,y)=\left(\frac{161}{395},\frac1{19}\right).
$$

该实例有 54/27/9 个候选 grids、24/16/8 个 active independent lines、31 条 active nested
lines 和 296851 个 arrangement vertices。结果仍与候选子族公式一致；素数族公式只有
$27284/22733\approx1.200194$。全局 exact 样本数增至六个。

原来的四条 chain 在 composite profile 上不是足够紧的上界；新增四条合法 chain 后，
`work/check_2r_subfamily_eight_chain_bound.py` 对 10/5/2 条 sorted independent lines 与 8 条
chain 做完整 exact arrangement。对 $r=5,7,11,13,17,19$ 六个实例全部得到候选值和候选点，
输出 `eight-chain exact upper-bound certificate=True`。剩余问题已压缩为固定 divisor profile
下的 25-line 参数化 arrangement。

`work/prove_sorted_factor_rearrangement.py` 证明了 sorted-grid reduction：在
$1\ge z\ge y\ge0$ 下，按因子从大到小分别配给 $y,z,1$ 系数不增加 line value；六个排列的
差值均由非负增量展开。于是 10/5/2 条 sorted lines 确实足以表示 independent envelopes。

`work/prove_2r_subfamily_eight_chain_cells.py` 进一步枚举 independent-owner 与 chain-owner
的 full-dimensional cells：$r=5,7,11,17,19$ 分别得到 36/35/34/34/34 个 proving cells，
每个 cell 都有一条 chain 在所有 exact vertices 上证明候选比值上界。cell 数会随参数变化，
所以后续符号证明需要显式处理 threshold，而不能假设单一 topology。

新增 `work/probe_2r_subfamily_symbolic_cells.py`：在 $r=21$ 的 33-cell branch 上提升所有
vertices 为 $r$ 的有理函数，121 个 vertices 的 feasibility 与 ratio signs 在 $r=21+a$ 下
全部通过 coefficientwise positivity；$r=21,23,50,100$ 的 fixed-profile topology 都是 33
cells。输出 `symbolic r>=21 cell certificate=True for the 33-cell branch`。因此大参数分支
已基本闭合，剩余是小参数 topology branches 与“无新 cell”完备性证明。

新增 `work/prove_2r_subfamily_independent_cover.py`。在固定 divisor profile
$p=2r,q=4r+3$ 下，它对 54/27/9 个 grids 做 exact symbolic cover：24/16/8 条 active lines
覆盖全部 omitted lines，差值在 $r-5\ge0$ 下逐项为非负多项式。输出为
`symbolic independent-cover certificate=True for r>=5, q=4r+3`。因此该候选子族的
independent envelope 已从数值观察提升为参数化代数证书；剩余是 nested upper envelope。

新增 `work/prove_2r_subfamily_chain_forms.py`，证明四条 chain 在
$z_0=(8r+9)/(5(4r+3)),y_0=1/r$ 处同时取值
$N_0=(32r+37)/(4r(4r+3))=(8q+13)/(4rq)$，并输出六个 pairwise chain difference identities。
所以候选 numerator 与 witness equality 已完成符号闭合；剩余只是在整个 arrangement 上证明
$U_8/I$ 的上界。四条 chain 只是八链上包络中的第一组，复合 profile 还需要新增的四条
chain 才能得到当前 exact certificate。

## 114. Fixed-profile topology audit and larger exact samples

新增 `work/check_2r_subfamily_topology_stability.py`，把 cell 身份编码为三层 independent
owner index 与 chain index，并调用 `run_profile(..., proving_only=False)` 统计全部可行的
full-dimensional cells。$r=21,23,50,100$ 都得到相同的 33-cell signature：

```text
samples=[(21,33,True),(23,33,True),(50,33,True),(100,33,True)]
```

这一步排除了“只挑选能证明上界的 cell”造成的假稳定；但仍是有限审计，尚未证明任意实数
$r\ge21$ 不会出现新 cell。

在 retreat CPU 上又对 14 个较大的素数参数对
$(r,q)=(31,127),(37,151),(41,167),(47,191),(59,239),(67,271),(89,359),
(107,431),(109,439),(149,599),(151,607),(157,631),(179,719),(181,727)$
运行完整的 25-line $U_8/I$ arrangement。全部精确命中预测点
$((2q+3)/(5q),1/r)$ 和闭式比值；加上此前六个样本，目前共有 20 个 exact global cases。
这仍然验证的是 fixed divisor profile，不能替代“无新 cell”的参数化证明。

retreat CPU 又逐个枚举了固定 profile 的所有 cell：对每个整数 $21\le r\le40$（$q=4r+3$），
均为 33 个 cell，且 owner/chain signature 与 $r=21$ 完全相同（`BAD []`）。这扩大了稳定区间的
有限证据，但没有消除实参数 no-new-cell 缺口。

## 115. Formal three-level theorem model

新增 `outputs/three-level-nested-communication-model.md`，正式固定了 v0 模型：square classical GEMM、static three-level grid、no recomputation、counted replication、balanced work、edge-based word volume，以及 componentwise-divisible nested chains。文档把当前的归一化 affine lines 与真正的物理通信量分开：后者需要从 GEMM DAG/phase argument 推导尺度因子 \(\kappa_\ell(n,P_\ell,M_\ell)\)。

目标定理分成两层：`T3-volume` 要证明任意合法 schedule 满足
\(Q_{\mathrm{vol}}\ge N-O(n^2)\)，`T3-tight` 还要求为每条 active chain 构造 matching blocked schedule。新增 `work/check_three_level_model.py` 只做模型一致性检查，不冒充下界证明。

## 116. One-level recovery checkpoint

新增 `work/check_one_level_recovery.py`。它把归一化 line 还原为矩形 GEMM 的
\(\lambda_{m,k,n}=mk/(ab)+mn/(ac)+kn/(bc)\)，并对 cubic square cases
\(P=1,8,27,64,125\) 精确验证 \(3n^2/P^{2/3}\)。这一步只确认 affine geometry 和量纲，尚未替代 HBL/phase-partition lower-bound proof。
