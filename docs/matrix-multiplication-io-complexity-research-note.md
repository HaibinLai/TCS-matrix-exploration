# 矩阵乘法 I/O 复杂度：研究探索笔记

> 版本：2026-10-02  
> 目标：建立一个可继续推进的研究地图，区分计算模型、已知下界、达到下界的算法和可验证的研究空白。

## 0. 研究问题与范围

对矩阵乘法

\[
C=AB,
\qquad A\in\mathbb{F}^{m\times k},\;B\in\mathbb{F}^{k\times n},\;C\in\mathbb{F}^{m\times n},
\]

研究在给定计算模型下，算法必须在不同存储位置或处理器之间移动多少数据。本文中的 I/O、communication、data movement 分别指：

- **两级存储 I/O**：快内存容量为 \(M\)，慢内存无限大；一次移动一个 word，或在外存模型中一次移动一个 block（大小 \(B\)）。
- **并行通信**：每个处理器有本地内存，数据通过网络或互连交换；分别计 bandwidth（words）和 latency（messages/synchronization）。
- **多级层次**：对每一对相邻层级分别计数，而不是把整个 cache/HBM/DRAM 视成一个平均容量。

核心问题不是只有渐近算术复杂度 \(O(n^3)\) 或 \(O(n^\omega)\)，而是：

> 在允许怎样的重排、重计算、复制和临时存储时，完成给定矩阵乘法至少需要多少数据移动？是否存在达到该下界的算法，并且常数、消息数和实际硬件行为是否也匹配？

## 1. 先固定的符号和边界

- \(Q\)：word-level I/O 或通信量。
- \(M\)：快内存容量（words）；并行时可写作每处理器本地容量 \(M_p\)。
- \(B\)：外存 block 大小；外存 I/O 通常以 block 次数计。
- \(P\)：处理器/节点/GPU 数量。
- \(F\)：算术操作数；经典 GEMM 为 \(\Theta(mkn)\)，Strassen 为 \(\Theta(n^{\log_2 7})\)。
- 下界要注明是否包含输入读取、输出写回、初始化 \(C\)，以及是否允许 recomputation。
- “紧”可能只表示阶（\(\Theta\)），也可能表示 leading constant；两者不能混用。

## 2. 历史主线（按问题演化）

| 年份 | 工作 | 主要贡献 | 研究时应保留的限制 |
|---|---|---|---|
| 1981 | Hong–Kung, *I/O Complexity: The Red–Blue Pebble Game* | 建立 red-blue pebble game；经典矩阵乘法的两级存储 I/O 下界 | 原始模型和计数口径需与现代 word/block 模型对应 |
| 1994 | Vitter–Shriver, *Algorithms for Parallel Memory, II: Hierarchical Multilevel Memories* | 在 P-HMM/P-BT 并行层级内存模型中，对标准 square MM 给出匹配的多级访问上界和下界 | 访问成本模型折叠了层级，网络通信被忽略；不是现代 rectangular GEMM 与 nested processor-grid 的定理 |
| 2004 | Irony–Toledo–Tiskin, *Communication Lower Bounds for Distributed-Memory Matrix Multiplication* | 将通信下界推广到分布式并行矩阵乘法 | 处理器内存、数据分布和算法类别影响公式 |
| 2011 | Ballard–Demmel–Holtz–Schwartz, *Minimizing Communication in Numerical Linear Algebra* | 用几何/扩张方法统一 dense、sparse、sequential、parallel 的通信下界，并同时讨论 bandwidth 与 latency | 是广泛线性代数框架，不等于每个 MM 变体都有 tight constant |
| 2012–2014 | Ballard 等, *Communication-Optimal Parallel Algorithm for Strassen’s Matrix Multiplication*；*Communication costs of Strassen’s matrix multiplication* | Strassen 并行算法达到相应通信下界；强调快速算法也必须分析通信 | 主要针对特定快速算法和并行模型 |
| 2015 | Scott–Holtz–Schwartz, *Matrix Multiplication I/O-Complexity by Path Routing* | 用 path routing 处理 recursive / Strassen-like 算法的 I/O 下界 | 经典递归结构、重计算和一般 bilinear 算法之间仍有差别 |
| 2016（会议版 2017） | Bilardi–De Stefani, *The I/O Complexity of Strassen’s Matrix Multiplication with Recomputation* | 在允许 recomputation 时给出 Strassen 的 tight 两级存储下界 | 这是 Bilardi–De Stefani 的工作，不是“GT 2016”论文 |
| 2017 | Smith–Lowery–Langou–van de Geijn, *A Tight I/O Lower Bound for Matrix Multiplication* | 对普通 classical GEMM 给出 leading-order \(2n^3/\sqrt M\) 下界，并构造达到该主项的理论算法 | 结论针对 ordinary MM、两级存储和特定计数方式；输入/输出低阶项仍需单列 |
| 2019 | De Stefani, *The I/O Complexity of Hybrid Algorithms for Square Matrix Multiplication* | 对 Strassen-like 递归与 classical base case 的 hybrid/non-stationary 算法给出 tight 下界，允许 recomputation | 仍是特定 hybrid 类别，不是所有快速 MM 的统一定理 |
| 2022 | Al Daas–Ballard–Grigori–Kumar–Rouse, *Tight Memory-Independent Parallel Matrix Multiplication Communication Lower Bounds* | 给出不依赖本地内存参数、带 tight constants 的并行 MM 通信下界，并按矩阵长宽比分类 | 重点是 parallel bandwidth；消息数、异构层次和实际 kernel 仍需另外分析 |
| 2026 | Gupta–Suomela–Vahidi, *Rectangular Matrix Multiplication in the Low-Bandwidth Model* | 在每机每轮只能收发 $O(\log n)$ bit 的模型中，研究两类矩形 MM，并给出 round-complexity 的 upper/unconditional/conditional bounds | 计数单位是 rounds/bit budget，不是 word-volume 或 HCP critical-path words |
| 2025 | Gupta–Korhonen–Studený–Suomela–Vahidi, *Low-Bandwidth Matrix Multiplication* | 将 low-bandwidth sparse MM 推广到多种稀疏结构并改进算法轮数 | 是 sparse 算法进展，不是 dense GEMM 的 universal tight lower bound |
| 2025 | Al Daas 等, *Minimizing Communication for Parallel Symmetric Tensor Times Same Vector Computation* | 对三阶对称张量给出 parallel tight communication bound 与 matching algorithm | 是 symmetric tensor extension，不是矩形 GEMM 主定理 |
| 2025–2026 | GPU/异构系统中的 communication-avoiding GEMM、低精度和 fused kernels 持续发展 | 把理论下界映射到 HBM、L2、shared memory、register、片上互连和 tensor core | 新系统论文常报告性能或工程模型，不能自动视为新的复杂度下界 |

推荐从原论文或作者版本开始阅读：

1. [Hong–Kung 的 I/O Complexity 页面](https://www.eecs.harvard.edu/htk/publications/)  
2. [Ballard et al. 2011（SIAM PDF）](https://perso.ens-lyon.fr/loris.marchal/docs-data-aware/Ballard_Demmel_Holtz_Schwartz_2011_Minimizing_Communication_Linear_Algebra.pdf)  
3. [Bilardi–De Stefani 2016/2017](https://arxiv.org/abs/1605.02224)  
4. [Smith et al. 2017](https://arxiv.org/abs/1702.02017)  
5. [De Stefani 2019](https://doi.org/10.4230/LIPIcs.ISAAC.2019.33)  
6. [Al Daas et al. 2022](https://arxiv.org/abs/2205.13407)  
7. [Communication-optimal parallel Strassen](https://arxiv.org/abs/1202.3173)

## 3. 已知结果：经典矩阵乘法

### 3.1 Sequential，两级 word-I/O 模型

对 \(n\times n\) classical GEMM，在 \(M\) 足够小且输入不能一次放入快内存时，经典阶下界为

\[
Q(n,M)=\Omega\!\left(\frac{n^3}{\sqrt M}+n^2\right).
\]

其中：

- \(n^3/\sqrt M\) 来自每个 fast-memory segment 最多支持 \(O(M^{3/2})\) 次有用乘法；证明通常结合 Loomis–Whitney 投影不等式、S-partition 或 pebble game。
- \(n^2\) 是读取输入和写回输出的基本项，不能被前一项替代。
- Smith et al. 2017 对 ordinary MM 的 leading-order 项做紧，主项写作 \(2n^3/\sqrt M\)；常数依赖 I/O 计数口径和是否把某些初始/最终移动计入。

对矩形 \(m\times k\) 乘 \(k\times n\)，应从三维迭代空间 \((i,k,j)\) 重新推导，而不是机械地把 \(n\) 替换成最大维度。一个安全的阶级模板是

\[
Q=\Omega\!\left(\frac{mkn}{\sqrt M}+mk+kn+mn\right),
\]

但在极端长宽比和受限布局下，更精确的分段下界可能由多个 min/max 项共同决定，需引用对应的 rectangular-MM 定理。

### 3.2 Block I/O（外存模型）

若一次传输一个 block（\(B\) words），常见 dense square 结论写成

\[
\Omega\!\left(\frac{n^3}{B\sqrt M}\right)
\]

次 block I/O，再加输入输出扫描项。必须说明矩阵布局、是否允许 tall-cache 条件、以及 block 对齐；word 移动量和 block 次数不是同一个指标。

### 3.3 达到下界的算法

经典 blocked/tiled GEMM 选取 tile 边长 \(b\approx\sqrt{M}\)，使一个阶段内的 \(A\)、\(B\)、\(C\) 子块总量为 \(O(M)\)，每阶段完成 \(O(b^3)=O(M^{3/2})\) 次乘法，因而达到 \(O(n^3/\sqrt M+n^2)\) 的阶。要声称“tight”，还要说明：

- tile 是否能同时容纳三个子块；
- 是否重复读取 \(A/B\) 或写回部分和；
- packing、panel、临时缓冲和并行同步是否计入；
- 真实 BLAS/Goto-style 实现是否达到理论 leading constant。

## 4. Strassen-like、快速和 hybrid 算法

### 4.1 Strassen 的两级存储下界

令 \(\omega_S=\log_2 7\)。Bilardi–De Stefani 在允许 recomputation 时给出

\[
Q_S(n,M)=\Omega\!\left(M\left(\frac{n}{\sqrt M}\right)^{\omega_S}\right)
=\Omega\!\left(\frac{n^{\omega_S}}{M^{\omega_S/2-1}}\right),
\]

并证明该量级可达。这里的关键贡献是把 recomputation 纳入 lower-bound 证明，而早期一些 path-routing/expansion 论证只适用于 no-recomputation。

### 4.2 Hybrid 算法

De Stefani 2019 研究在递归高层使用 Strassen-like 算法、到阈值 \(n_0\) 后使用 classical multiplication 的 hybrid。uniform、non-stationary 类别的代表性下界为

\[
\Omega\!\left[
\left(\frac{n}{\max\{\sqrt M,n_0\}}\right)^{\omega_S}
\left(\max\left\{1,\frac{n_0}{M}\right\}\right)^3 M
\right],
\]

具体表达式随 non-uniform recursive calls 变得更复杂。研究时应把 \(n_0\)、递归形状、临时空间和 recomputation 明确写进模型。

### 4.3 一般快速矩阵乘法仍未被一个简单公式覆盖

“\(n^\omega\) 算术复杂度”不能单独决定 I/O 复杂度。需要知道 bilinear algorithm 的：

- rank/tensor decomposition 和每层的线性组合数量；
- CDAG 的 vertex/edge expansion、path routing 或 flow 性质；
- 是否允许重计算、编码变换和不规则递归；
- 中间结果的数值表示和临时存储是否收费。

因此不能把 Strassen 下界直接宣称为所有 fast MM 的下界。

## 5. Parallel 与 distributed-memory 设置

### 5.1 经典 2D 分布式算法

在 \(P\) 个处理器上、每处理器本地存储约 \(n^2/P\) 的典型 2D 模型中，Cannon/SUMMA 类算法的 bandwidth 通信阶通常为

\[
\Omega\!\left(\frac{n^2}{\sqrt P}\right)
\quad\text{words per processor},
\]

并伴随与 \(\sqrt P\) 同阶的消息/同步项（具体形式依赖 blocking、collective 和网络模型）。这是 2D 数据布局下的结果，不能直接当作任意算法的 memory-independent universal bound。

### 5.2 复制、2.5D/3D 与 memory-dependent trade-off

复制因子增加后，可用额外内存换带宽；2.5D/3D 算法正是这种 trade-off。分析时至少要同时记录：

- 每处理器本地内存 \(M_p\)；
- replication factor；
- bandwidth words、messages、同步轮数；
- 初始分布和最终收集是否收费。

不同论文对“通信下界”使用的 memory assumption 不同。Ballard et al. 的扩张方法、Irony–Toledo–Tiskin 的并行推广和 Al Daas et al. 2022 的 memory-independent tight constants 应分开引用。

### 5.3 并行 Strassen

Ballard–Demmel–Holtz–Lipshitz–Schwartz 给出 communication-optimal parallel Strassen；其下界来自 Strassen CDAG 的扩张性质。它说明：降低算术操作数不等于自动降低通信，递归线性组合和中间结果分发本身也可能成为瓶颈。

### 5.4 需要警惕的“并行下界”混淆

- bandwidth 下界不等于 latency 下界；
- 每处理器下界不等于全系统总通信量；
- 强扩展（固定 \(n\)，增大 \(P\)）和弱扩展（每处理器问题规模近似固定）对应不同可行区间；
- 允许 replication 的算法不能用只针对 2D、不复制模型的公式评价；
- “memory-independent”不代表与网络拓扑、消息大小、同步开销都无关。

## 6. 多级内存层次

对 HBM、L2、shared memory、register 或 DRAM/NVRAM 等多级层次，一个理想化目标是对每个相邻层级 \(\ell\) 写出

\[
Q_\ell\ge \mathrm{LB}(M_\ell,M_{\ell+1},P_\ell),
\]

然后寻找一个 schedule 同时接近所有层级的下界。这比把所有容量压缩成一个 \(M\) 更严格，因为：

- 某一级的最优 tile 可能破坏另一级的重用；
- register/shared-memory 受线程束、bank conflict、tensor-core fragment 约束；
- 数据复制和 layout transform 可能在不同层级重复发生；
- GPU kernel 中的异步 copy、prefetch 和 fusion 使“单一 segment”定义不再直接适用。

Vitter–Shriver 1994 已经在 P-HMM/P-BT 这类统一 access-cost 模型中给出标准 square MM 的 parallel multilevel 最优结果；因此不能把“多级内存从未被研究”作为 gap。当前更窄、也更贴近现代并行 GEMM 的问题是：在 rectangular aspect ratios、processor-grid divisibility、网络通信和每层独立/nested layout 约束同时存在时，能否构造一个仍然 tight 的统一 schedule。已有 cache-oblivious、communication-avoiding 和硬件特化工作通常只覆盖其中一部分模型。

来源：[Vitter–Shriver, *Algorithms for Parallel Memory, II: Hierarchical Multilevel Memories*](https://ittc.ku.edu/~jsv/Papers/ViS94.sorting_hierarchical.pdf)。

## 7. 截至 2026 年的研究空白候选

下面不是已经证明的 open theorem，而是适合逐项核验的候选问题。

### A. 模型层面的统一性

- [ ] 能否给出一个同时覆盖 classical、Strassen-like、hybrid 和一般 bilinear MM 的 CDAG/partition theorem，并明确 recomputation 的代价？
- [ ] 能否把 word-I/O、block-I/O、bandwidth、messages 和 synchronization 放进同一个带参数的 lower-bound 体系？
- [ ] 对矩形、batched、不同精度和稀疏/结构化矩阵，哪些下界是 tight，哪些只差多项式或对数因子？

### B. 多级和异构内存

- [ ] 是否存在对任意递归 MM 算法都成立、且每一级同时近似 tight 的 multilevel lower bound？
- [ ] 在 HBM–L2–shared–register 层次中，tensor-core fragment、bank conflict、warp-level exchange 应如何进入 I/O 模型？
- [ ] fusion（例如把缩放、累加、归约融合进 GEMM）何时真的降低通信下界，何时只是把移动隐藏起来？
- [ ] 对 CPU–GPU 或多 GPU 系统，能否把 PCIe/NVLink、HBM 和片上共享存储作为不同边，并得到可验证的端到端 bound？

### C. 并行与网络

- [ ] 在 arbitrary topology、非均匀链路和故障/重配置条件下，memory-independent bound 能否转成 topology-aware bound？
- [ ] 复制、压缩、编码计算和 recomputation 的联合 trade-off 是否已有 tight characterization？
- [ ] latency、同步和能耗的联合下界能否与 bandwidth 下界同时达到？

### D. 算法家族与实际实现

- [ ] 对非均匀、非平稳 hybrid 算法，是否可以把理论下界转成自动化验证器：输入递归规则和内存容量，输出每级 I/O 下界？
- [ ] Goto/BLIS/cuBLAS/CUTLASS 等实现距离 Smith et al. 的 leading constant 还差多少，差距来自 packing、边界 tile、线程同步还是硬件指令约束？
- [ ] 对低精度、混合精度和累加精度变化，word 的定义应按字节、元素还是有效信息量计数？
- [ ] 对 irregular shapes、small-batch 和动态 batch，理论 bound 如何与实际 kernel 的 autotuning 共同验证？

### E. 证明技术

- [ ] Loomis–Whitney、S-partition、expansion、path routing、Grigoriev flow 是否能组合成一个可机械检查的 proof pipeline？
- [ ] 如何证明允许任意 recomputation、临时编码和数值重排时仍然成立的下界？
- [ ] 对近似乘法、随机化算法和允许误差的数值计算，通信 lower bound 如何随误差参数变化？

## 8. 建议的最小研究路线

1. **复现经典证明**：从 red-blue pebble game 写出 square 和 rectangular classical GEMM 的 S-partition/Loomis–Whitney 证明，明确每个 segment 的边界和输入输出项。
2. **复现 tight constant**：逐行核对 Smith et al. 2017 的 FMA transformation、只计 input reads 的论证和 leading constant；用一个可运行的 blocked GEMM 估计实际 words moved。
3. **建立统一记号**：为 sequential、parallel、Strassen、hybrid 各写一页“模型卡”，列出 \(M,B,P\)、是否复制、是否重计算、计数口径。
4. **做一个小型文献矩阵**：每篇论文记录算法类、模型、下界、是否 tight、是否允许 recomputation、是否包含 latency、是否有 matching algorithm。
5. **挑一个窄而可证的问题**：优先考虑“特定递归/混合算法在两级或三级内存中的 tight bound”，避免一开始声称解决所有 fast MM。
6. **加上可验证实验**：用硬件计数器、CUDA/Nsight 或内存访问 trace 测量理论 words moved；将 cache miss、HBM transaction、shared-memory transaction 分开记录。
7. **形成 gap claim**：只有在检索 2019–2026 的引用链、technical report、thesis 和 arXiv 更新后，才能把某项写成“未解决”；否则使用“尚未找到统一结果”的措辞。

## 9. 建议的文献阅读顺序

1. Hong–Kung：理解 pebble game 和为什么 \(M^{3/2}\) 是经典三因子乘法的核心容量规模。
2. Irony–Toledo–Tiskin + Ballard et al. 2011：理解从 sequential 到 parallel、从 bandwidth 到 latency 的转换。
3. Smith et al. 2017：掌握 classical GEMM 的 tight leading term 和计数边界。
4. Scott–Holtz–Schwartz 2015：理解 path routing 对递归算法的作用。
5. Bilardi–De Stefani 2016/2017：重点读 recomputation 仍然成立的 Strassen 下界。
6. Ballard et al. 2012/2014：阅读 communication-optimal parallel Strassen 的 matching algorithm。
7. De Stefani 2019：研究 hybrid/non-stationary 递归。
8. Al Daas et al. 2022：核对 memory-independent parallel tight constants。
9. 最后再读 2023–2026 的 GPU、异构、低精度和系统论文，把它们映射回明确的理论模型。

## 10. 研究记录模板

每阅读一篇论文，填写：

```text
Citation:
Year / venue:
Problem shape: square / rectangular / batched / sparse
Algorithm class: classical / Strassen-like / hybrid / arbitrary bilinear
Model: sequential two-level / block I/O / parallel / multilevel / heterogeneous
Parameters: n,m,k,M,B,P,replication
Counts: words / blocks / messages / synchronizations / energy
Recomputation: allowed? yes/no; encoded intermediates?
Lower bound:
Upper bound / matching algorithm:
Tightness: order / leading constant / only special regime
Main proof tool:
Hidden assumptions:
What remains open:
Reproducible artifact or experiment:
```

## 11. 结论性工作假设

当前最稳妥的研究起点是：

> **先研究带明确递归结构和 recomputation 规则的 classical–Strassen hybrid，在两级或三级内存中证明 tight I/O bound；再把同一个证明映射到并行复制和 GPU 层次。**

这样既直接承接 2017 classical tight bound、2016/2017 Strassen-with-recomputation 和 2019 hybrid 结果，也能把“多级异构层次中同时 tight”作为一个清晰、可证伪、可实验验证的后续问题。

## 12. 2026-10-02 探索更新：并行 hierarchy overhead 的新 witness

研究日志中的一个具体构造已经从数值猜想推进为一维 witness 定理。取三个处理器层级

$$
(P_1^*,P_2^*,P_3^*)=(2pq,pq,p),
$$

其中 $p,q$ 为不同素数且 $q>p$，并在 aspect-ratio 点 $(z,y)=(1,1/p)$ 比较所有 processor grids。对每个层级的独立最优 grid 和所有 nested chains 做平方自由因子枚举后，精确得到

$$
I_p(q)=\frac{3}{p}+\frac{3}{2p^2}+\frac{3/2+2/p}{q},qquad
N_p(q)=\frac{9}{2p}+\frac{7}{2pq}.
$$

符号证书证明这些目标在所有 $p\ge3,q>p$ 中确实分别是 independent 与 nested 的最优值。因此任意对所有 hierarchy 和 aspect ratios 成立的 multiplicative overhead 常数 $C$ 都满足

$$
C\ge R_p(q)=\frac{p(9q+7)}{(6p+3)q+3p^2+4p},qquad
C\ge\frac32
$$

其中第二个不等式由先取素数 $q\to\infty$、再取素数 $p\to\infty$ 得到。这个结果是固定 aspect-ratio witness 的必要下界，不是 $3/2$ 可达的上界；是否存在更大的 family，以及能否证明统一 $C=3/2$ 上界，仍然开放。

证明脚本为 [`work/prove_prime_p_family.py`](../work/prove_prime_p_family.py)，详细推导和二维 sanity checks 见 [`parallel-io-exploration-log.md`](parallel-io-exploration-log.md)。

## 13. 边界上的解析最大值

对同一素数族，在边界 $z=x$ 上令 $t=y/x$。逐一比较因子分配后，三个 independent 层的 lower envelopes 为

$$
f_1(t)=\begin{cases}
\frac1{pq}+t,&0\le t\le\frac1{pq},\\
\frac3{2pq}+\frac t2,&\frac1{pq}\le t\le\frac1q,\\
\frac{p+2}{2pq}+\frac{t}{2p},&\frac1q\le t\le1,
\end{cases}
$$

$$
f_2(t)=\begin{cases}
\frac2{pq}+t,&0\le t\le\frac1q,\\
\frac{p+1}{pq}+\frac tp,&\frac1q\le t\le1,
\end{cases}
\qquad f_3(t)=\frac2p+t.
$$

三个明确的 nested chains 分别给出三个区间上的 numerator upper bound。区间 ([1/q,1/p]) 上相应 ratio 的导数为正，区间 ([1/p,1]) 上相应 ratio 的导数为负；结合 endpoint certificate 在 (t=1/p) 的 equality，可得严格边界结论

$$
\max_{0\le t\le1}\frac{N(1,1,t)}{I(1,1,t)}
=\frac{p(9q+7)}{(6p+3)q+3p^2+4p}.
$$

这把原来的边界最大点猜想升级为解析定理；脚本还对 161 个扩展素数对做了 exact boundary regression。完整二维域仍需证明内部 $z<x$ 不会产生更大值。检查脚本为 [`work/check_prime_p_boundary_theorem.py`](../work/check_prime_p_boundary_theorem.py)。

## 14. 二维推广的径向单调性猜想

令

$$
(x,z,y)=(1,s,st),\qquad 0\le s,t\le1.
$$

边界定理对应 $s=1$。当前待证的充分命题是：对固定 $t$，

$$
F_{p,q}(s,t)=\frac{N(1,s,st)}{I(1,s,st)}
$$

关于 $s$ 单调不减。若成立，则边界结果立即给出完整二维上界。`work/check_prime_radial_monotonicity.py` 已在 54 个参数组合的 exact rational 网格上检查，没有发现反例；这仍是诊断证据，不是定理。下一步应按 active grid cell 对

$$
H_g(1,s,st)=c/P+s(b+ta)/P
$$

的 ratio 导数做符号证明。

在这个方向上已经可以严格覆盖一个内部区域：当 $t\le1/q$ 时，$2pq$、$pq$、$p$ 三层的 independent minimizers 分别可由边界 active grid 延伸到所有 $s\in[0,1]$；对应的两个 nested chains 逐层达到这些 minima。因此

$$
F_{p,q}(s,t)=1\qquad(0\le s\le1,\ 0\le t\le1/q).
$$

完整二维证明只需继续处理 $t\ge1/q$ 的区域。

## 15. 修正后的二维 $3/2$ cell 证书

这一节记录一次验证修正：初版脚本把三角域约束方向写反，实际检查了
$0\le s\le u\le1$；同时要求同一条 nested chain 覆盖整个 independent cell，这个要求
过强，因为 nested minimum 可以在一个 independent cell 内切换。初版的 9-cell 与固定
两类 chain 结论已删除，不再作为证据使用。

现版 `work/check_prime_three_halves_cells.py` 在正确域

$$
(x,z,y)=(1,s,u),\qquad 0\le u\le s\le1
$$

上，把 independent lower envelope 与所有合法 nested chains 的 lower envelope 叠加。每个
grid $g=(a,b,c)$、$abc=P$ 的代价为

$$
H_g(1,s,u)=\frac cP+s\frac bP+u\frac aP.
$$

交换论证将 independent 候选限制到 $a\ge b\ge c$，三层候选数为 $(5,2,1)$。对每个
independent candidate 组合和每条 nested chain，加入该 chain 不高于所有其他 chain 的
线性约束；在每个非空 subregion 上，$H_{\mathcal C}-\tfrac32I$ 是仿射函数，因此顶点
检查给出连续域上的精确有理数证书。

修正后的每个参数有 10 个 independent cells 和 84 个 nested subregions。默认 30 组参数
全部通过；扩展到 161 组 $p<q$ 素数参数也全部通过，包括此前暴露问题的 $(p,q)=(5,53)$。
这仍是逐参数证书，不是对所有 $p<q$ 的统一定理。下一步应按 $q\ge2p$ 与 $p<q<2p$
符号化 10 个 cell 与 nested subregion 的合并模式，再证明每类仿射差值在
$p\ge3,q>p$ 下非正。

复现：

```text
python -m py_compile work/check_prime_three_halves_cells.py
python work/check_prime_three_halves_cells.py
# checked=30 exact 3/2 cell certificates
```

### 16. Active nested line 的进一步压缩

三层 $(2pq,pq,p)$ 有 27 条合法 nested chains，但正确 lower-envelope 过滤后，每个已测
参数只留下 16 条 active affine lines。以 $(p,q)=(5,53)$ 为例，这些 line 的系数由

$$
A=\frac1p+\frac{3}{2pq},\quad
B=\frac1p+\frac1{2q},\quad
C=\frac12,\quad
D=1+\frac{3}{2q},\quad
E=\frac52,\quad
F=3
$$

的排列组合构成。$(3,29),(5,53),(11,13),(11,101)$ 均得到 16 条 active lines，且每个
参数有 84 个 nested subregions。后续符号证明可以先按 $q\ge2p$ 与 $p<q<2p$ 固定
active line 模板，再对每个交集多边形的顶点证明
$L_{\mathrm{nested}}-\tfrac32L_{\mathrm{independent}}\le0$。

### 17. 16-chain active template

按实际 grid 三元组提取后，30 组回归参数的 active nested chain 集合都恰好等于以下
16 个模板：

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

`work/check_prime_active_chain_templates.py` 做 exact lower-envelope 交集检查；默认参数
覆盖 $q<2p$ 与 $q>2p$ 两种情形，全部得到 `active=16 template_match=True`。这为后续
符号证明提供了有限候选模板；进一步加入接近 $q=p$ 的参数后共检查 42 组，仍全部通过，
但尚未证明该模板对所有素数参数稳定。

### 18. 非模板 chain 的全域支配检查

16 条模板之外的 11 条合法 nested chain，可以通过仿射支配进一步消去。两条 chain 的
代价差在 $(s,u)$ 上是仿射函数，所以在 $0\le u\le s\le1$ 上只需检查
$(0,0),(1,0),(1,1)$ 三个顶点。`work/check_prime_chain_dominance.py` 对默认 30 组以及
包含 $q$ 接近 $p$ 的 42 组参数都验证了：每条非模板 chain 都被某条模板 chain 在整个
三角域上支配。

进一步把 $p,q$ 都取自 $\{3,5,\ldots,97\}$，对所有 $p<q$ 的 276 组参数运行同一检查，
得到 `checked=276 affine chain-dominance cases`；这扩大了回归范围，但仍不替代逐行的
参数化证明。

因此，一个更紧凑的证明路线是：先用 11 个全域支配不等式证明 nested lower envelope
只需保留 16 条模板，再证明这 16 条模板与 independent envelope 的交集上满足
$N\le\tfrac32I$。目前支配关系仍只有逐参数 exact 证据，尚未完成对所有 $p\ge3,q>p$
的符号化证明。

令 $r=1/p,t=1/q,v=rt$。逐行写出 11 个支配关系后，三个三角域顶点上的差值只包含

$$
-3+r+\frac32v,\quad -\frac52+\frac52r,\quad
-\frac32+\frac32r+\frac32t-kv,
$$

$$
-\frac r2,\quad -\frac r2+\frac v2,\quad
-\frac t2,\quad -\frac t2+\frac v2,
$$

以及 $-1-\alpha t+\frac52r+\beta v/2$（$\alpha\in\{3/2,2\}$、$\beta\in\{0,1\}$）。
在 $0<t<r\le1/3$ 下这些表达式均非正；这为一个可能适用于所有实数 $p\ge3,q>p$
的 16-chain reduction 提供了证明框架，仍需逐行完成正式核对。

这一步已由 `work/prove_prime_chain_dominance_symbolic.py` 完成逐行核对，输出
`checked=11 symbolic dominance rows`。因此在当前素因子枚举模型下，nested lower envelope
确实可以先约化到 16 条模板；尚未解决的是这 16 条模板与 independent envelope 交集上的
统一 $3/2$ 上界。

新增 `work/check_prime_three_halves_reduced.py`，直接使用 16 条模板而不是全部 27 条
合法 chain；默认 30 组参数仍全部通过，得到 10 个 independent cells、84 个 nested
subregions。这确认了 chain reduction 与二维 $3/2$ 证书可以独立组合。

### 19. 平均三条 nested chain 的直接 $3/2$ 上界

取三条合法 chains

$$
\mathcal A=((p,2,q),(p,1,q),(p,1,1)),\quad
\mathcal B=((p,q,2),(p,q,1),(p,1,1)),\quad
\mathcal C=((pq,1,2),(pq,1,1),(p,1,1)).
$$

令 $r=1/p,t=1/q,v=rt$。它们的平均 affine cost 为

$$
\bar L=\left(\frac32r+\frac43v,\ \frac76(r+v),\ \frac32+t\right).
$$

对第一层 $2pq$ 的 5 个 sorted factor candidates、第二层 $pq$ 的 2 个 candidates，
并分别处理 $q\ge2p$ 与 $p<q<2p$，共有 20 个 candidate combinations。脚本
`work/prove_prime_three_halves_average.py` 对每个组合检查

$$
\bar L-\frac32(L_{2pq}+L_{pq}+L_p)
$$

在 $(0,0),(1,0),(1,1)$ 的精确符号，输出 `checked=20 symbolic average certificates`。
由于 nested minimum 不超过三条 chain 的平均值，而 independent minimizer 可以限制到
sorted candidates，这证明了该素数 hierarchy family 的全域上界

$$
N_{p,q}(s,u)\le\frac32 I_{p,q}(s,u).
$$

结合 witness $R_p(q)\to3/2$，得到此特定 $(2pq,pq,p)$ family（$3\le p<q$ 为素数）的
overhead supremum 正好为 $3/2$。这里的 supremum 只对这些 odd-prime 参数取；这仍不等于任意三层 processor hierarchy
的 universal theorem。

## 20. 复合层次的动态规划扫描（截至 2026-10-02）

新增 `work/scan_boundary_dp.py`，在 $z/x=1$ 边界上用兼容状态的 lower-envelope 动态
规划代替 nested-chain 全枚举。对整除族

$$
(P_1,P_2,P_3)=(p_3r_2r_1,p_3r_2,p_3),qquad P_1\le240,
$$

共检查 1382 个层次；最大边界比值是

$$
\frac{N}{I}=\frac{535}{427}\approx1.2529274
$$

（$(P_1,P_2,P_3)=(230,115,5)$，$y/x=1/5$）。随后对前六个候选用
`work/exact_2d_pruned.py` 做二维精确 arrangement，最大值仍为该边界点；目前没有发现
超过 $3/2$ 的复合层次反例。

该结果只是有限搜索证据，不能替代任意三层 hierarchy 的定理。它支持两个后续方向：
证明最坏点可限制到 $z/x=1$ 的边界，以及把兼容 lower envelope 的动态规划写成关于层数
的归纳证明。

## 21. 2025 年前后并行紧下界的进展

近期最接近多层通信问题的工作是 Zhu、Hua、Jin 的 *Joint-Communication Optimal Matrix
Multiplication with Asymmetric Memories*（JCST 40(3), 2025，
[DOI](https://doi.org/10.1007/s11390-023-3489-y)）。该文同时计量处理器间 horizontal
bandwidth 与主存—缓存 vertical bandwidth：对称内存时可组合两个方向的最优算法；非对称
内存时证明两者有 trade-off，并构造达到 joint lower bound 的 JOMMA。它覆盖一个垂直内存
层加一个分布式处理器层，尚不是任意多层 hierarchy 的定理。

另一条进展是 Al Daas 等人的 *Communication Lower Bounds and Optimal Algorithms for
Symmetric Matrix Computations*（arXiv:2409.11304，后发表于 ACM TOPC 12(2), 2025）。该文
对 SYRK、SYR2K、SYMM 在 sequential 和 distributed-memory parallel 模型中都给出 tight
下界与匹配算法，说明几何不等式加约束优化可以扩展到结构化 BLAS-3 kernel；但它不解决
一般 GEMM 的跨层兼容性。

截至本笔记的范围，文献缺口可写成：已有单层 memory-dependent / memory-independent
下界、结构化 kernel 下界和二层 joint-communication 下界；仍缺少任意 $L\ge3$ 层、允许
复制与跨层复用的统一 tight lower bound 及同时匹配每层的 schedule。

## 22. 四层 hierarchy 的首轮边界实验

`work/scan_multilevel_boundary_dp.py` 将兼容 lower-envelope 动态规划推广到任意层数。
在四层整除族

$$
(P_1,P_2,P_3,P_4)=(p_0r_1r_2r_3,p_0r_1r_2,p_0r_1,p_0)
$$

上，对 $P_1\le80$ 的 109 个层次做精确 $z/x=1$ 扫描，最大比值为

$$
\frac{803}{721}\approx1.11373
$$

（$(56,28,14,2)$，$y/x=36/77$）。当前样本没有显示层数增加会自动把 overhead 推高到
$3/2$ 以上；不过这仍是边界实验，尚未覆盖二维 aspect-ratio，也不是多层定理。

## 23. 四层二维 arrangement 验证器

新增 `work/exact_multilevel_2d.py`，将 partial-chain lower-envelope pruning 和二维
arrangement vertex 枚举推广到任意层数。它先与已有三层 verifier 在 $(30,15,3)$ 上复现
$13/12$，再对四层候选得到：

$$
(56,28,14,2):\quad \max N/I=803/721\approx1.11373,
$$

$$
(80,40,20,4):\quad \max N/I=226/205\approx1.10244.
$$

另外，$(60,20,10,2)$ 的全二维最大值为 $83/76\approx1.09211$，同样在 $z=1$、$y=1/2$
取得。

这些候选的二维最大点都在 $z=1$ 边界；前两个分别为 $y=36/77$ 与 $y=1/4$。这仍是有限层次的
精确证据，但已经把“四层只在边界扫描”的结论提升为两个实例上的全二维核验。

## 24. 五层 hierarchy 的首个全二维实例

五层边界扫描检查了 11 个 $P_1\le64$ 的整除层次，最高值为

$$
(48,24,12,6,2):\quad N/I=53/51\approx1.03922,qquad y/x=1/2.
$$

`work/exact_multilevel_2d.py` 对该层次完成全二维精确核验：最终 nested envelope 有 70
条 active lines，arrangement 有 995008 个顶点，最大值仍为 $53/51$，位于
$(z,y)=(1,1/2)$。这进一步支持边界最大点现象，但也显示直接扩大 arrangement 的代价
会迅速增长。
最高五层样本的 partial-state 统计为
`(45,45,1) -> (30,72,3) -> (18,102,9) -> (9,120,22) -> (3,98,43)`，最终 nested envelope
只有 70 条 active lines。这提示可以围绕 active-line 数建立状态压缩或归纳界，而不必枚举
完整 nested chains。

## 25. 六层边界趋势

六层扫描（$P_1\le128$，13 个整除层次）的最大值为

$$
(96,48,24,12,6,2):\quad N/I=329/317\approx1.03785,qquad y/x=1/2.
$$

当前三至六层数据中，最大 overhead 始终由三层样本产生；层数增加后比值反而下降。这
提示“最坏层数为三层”可能是一个可检验的研究猜想，但目前只有有限整除族的边界证据。

## 26. 随机层级抽样：层数不具有简单单调性

`work/sample_multilevel_boundary.py` 固定 seed=20261003、每层 10 个样本、$P_1\le300$，
得到一组可复现实验：三层最高 $1.09255$，四层 $1.09227$，五层 $1.09501$，六层
$1.04054$。五层略高于该次抽到的三层和四层样本，说明不能把“层数越多 overhead 越小”
当作定理。已知三层构造的 $535/427$ 仍明显更高；更合理的猜想是，在固定总规模和因子
约束下，三层可能是最坏层数，但需要更大范围搜索或解析证明。

## 27. 凸包加速与复合 $p$ 族

`work/scan_multilevel_boundary_hull.py` 用 exact monotone hull 将一维 envelope 剪枝从两两
交点枚举降为按斜率排序的栈算法，并在已知实例上复现原始 verifier 的比值。三层整除扫描
扩大到 $P_1\le1000$ 的 11217 个层次后，最高值为

$$
(954,477,9):\quad N/I=726/535\approx1.35701,qquad y/x=1/9.
$$

进一步允许 $p$ 复合，`work/scan_composite_p_family.py` 检查 $p\le100,q\le1000$ 的
15000 个参数对；最高为 $p=99,q=997$ 的 $14817/10034\approx1.47668$。同一 $p=99$、
$q=10007$ 时约为 $1.49087$。因此素数平方自由假设只适合构造易证明的 witness，不代表
最坏有限参数；复合因子的 divisor structure 需要纳入后续符号分析。

## 28. $p=99$ 复合族的解析 witness

新增 `work/prove_composite_p_q_witness.py`，对

$$
(P_1,P_2,P_3)=(198q,99q,99),\qquad (z,y)=(1,1/99)
$$

在 $q_0=997$ 与 $q=\infty$ 两个 endpoint 对全部 competitor 做 exact affine comparison。
目标 independent grids 为 $(q,11,18)$、$(q,9,11)$、$(99,1,1)$，目标 nested chain 为
$( (99,2,q),(99,1,q),(99,1,1) )$；脚本输出两个方向均无 bad comparison。

因此对所有更大的素数 $q\ge997$，

$$
I(q)=\frac{199q+2277}{6534q},\qquad
N(q)=\frac{9q+7}{198q},\qquad
\frac{N(q)}{I(q)}=\frac{297q+231}{199q+2277}.
$$

极限为 $297/199\approx1.49246$。这说明平方自由素数构造并非唯一的高 overhead 来源；
复合 $p$ 的因子分配会改变有限参数公式，但仍把该族推向 $3/2$。

## 29. 复合 $p$ 规律的自动 endpoint 检验

`work/discover_composite_certificates.py` 在 $q_0=997$ 自动寻找 $t=1/p$ 的最优 grids 和
chain，并检查两个 endpoint。对 $3\le p\le100$ 的全部 49 个奇数 $p$，证书均通过，且

$$
\lim_{q\to\infty}N/I=\frac{3p}{2p+1}.
$$

偶数 $p$ 有 48/49 个通过某个因子结构相关的公式；只有 $p=100$ 在该 $q_0$ 尚未满足目标
independent line 的稳定性。由此可见，平方自由条件主要是早期符号枚举的便利假设，而不
是高 overhead 的本质来源。

## 30. 奇数复合 $p$ 的渐近结构

固定奇数 $p$，令 $q\to\infty$ 且 $q\nmid2p$，在 $y/x=1/p$ 处，independent 的极限
候选 grids 为 $(q,1,2p)$、$(q,1,p)$、$(p,1,1)$，所以

$$
I_\infty(p)=\frac{3}{p}+\frac{3}{2p^2}.
$$

nested chain $((p,2,q),(p,1,q),(p,1,1))$ 给出 $N_\infty(p)=9/(2p)$。已有自动证书对
$3\le p\le100$ 的所有奇数 $p$ 都支持其它 q-placement 不会更低，从而得到统一形式

$$
R_\infty(p)=\frac{3p}{2p+1}.
$$

第 31 节已经把 q-placement 分情况写成关于任意奇数 $p$ 的整数不等式，形成了不依赖有限
枚举的正式渐近引理。

## 31. 奇数 $p$ 渐近 witness 的正式引理

对任意奇数整数 $p\ge3$，取素数 $q\to\infty$ 且 $q\nmid2p$。在 $y/x=1/p$ 处有

$$
H_{(a,b,c)}=\frac{b+c+a/p}{abc}.
$$

由 q 所在坐标分类可得：independent 三层的极限分别是

$$
\frac1{2p^2},\qquad \frac1{p^2},\qquad \frac3p,
$$

所以 $I_\infty=3/p+3/(2p^2)$。nested chain 中 q 若在第二/第三坐标，前两层至少贡献
$1/(2p)+1/p$；若在第一坐标，令第二层 q-free 因子为 $r$、第三层对应因子为 $d\mid r$，
利用 $p/d=1$、$3$ 或至少 $5$ 三种情况可得总成本仍至少 $9/(2p)$。链

$$
((p,2,q),(p,1,q),(p,1,1))
$$

达到该值，因此

$$
N_\infty=\frac9{2p},\qquad
\lim_{q\to\infty}\frac NI=\frac{3p}{2p+1}.
$$

这把 $3/2$ 必要下界推广到了任意奇数复合 $p$ 序列，而不依赖平方自由或素数假设。
有限 sanity check 脚本 `work/check_odd_p_asymptotic.py` 已验证 $p\le100$ 的 49 个奇数实例。

## 32. Witness 点的有限-$q$ $3/2$ 上界

对任意奇数 $p\ge3$ 和素数 $q>p$，在 $(z,y)=(1,1/p)$ 处，按 $q$ 所在坐标分类可得

$$
I(p,q)\ge L(p,q):=\frac3p+\frac3{2p^2}+\frac3{pq}.
$$

固定合法 chain $((p,2,q),(p,1,q),(p,1,1))$ 的成本为

$$
U(p,q)=\frac9{2p}+\frac7{2pq}.
$$

并且

$$
\frac32L(p,q)-U(p,q)=\frac9{4p^2}+\frac1{pq}>0.
$$

因此在这个 witness aspect-ratio 点上，有限 $q$ 也满足 $N\le3I/2$。脚本
`work/prove_boundary_point_three_halves.py` 对 787 个奇数 $p$、素数 $q$ 参数对完成了 exact
检查；完整二维上界仍未由此推出。

## 33. 大复合参数的二维快速定位证据

为测试复合族中较大的有限参数，运行了 `work/exact_multilevel_2d.py --float-locator`。
对于

$$
(P_1,P_2,P_3)=(197406,98703,99)=(2\cdot99\cdot997,99\cdot997,99),
$$

浮点 arrangement 定位器扫描约 620 万个候选点，最优点为

$$
(z,y)=(1,1/99).
$$

随后用有理数精确回代得到

$$
I=\frac{100340}{3257199},\qquad
N=\frac{4490}{98703},\qquad
\frac NI=\frac{14817}{10034}\approx1.4766792904.
$$

该结果与边界扫描及 \(p=99\) endpoint 证书相符，进一步支持高 overhead witness 位于
\(y/x=1/p\) 的边界猜想。由于候选点定位阶段使用浮点数，这一节是快速定位和精确回代
证据，不是对全部 arrangement 顶点的完全精确穷举证明；要形成定理，仍需对 winning
cell 的可行性和所有其他候选的支配关系进行精确验证。

## 34. 近年并行紧下界的进展与缺口（文献核查至 2026-10-03）

近年的进展更像是“补齐模型边界”，而不是出现一条覆盖所有层次的全新 GEMM 定理：

- **2022，memory-independent 并行 GEMM。** Al Daas、Ballard、Grigori、Kumar、Rouse 对并行
  经典矩阵乘法给出了按 aspect ratio 分情况的紧常数，并构造达到下界的算法。这一结果精确
  化了 distributed-memory 的强 scaling 极限，但只处理并行通信模型中的 memory-independent
  项。论文：<https://arxiv.org/abs/2205.13407>。
- **2023，Multi-TTM。** Al Daas 等将几何/HBL 不等式和约束非线性优化用于多个 tensor-times-
  matrix 的并行通信，并用逻辑处理器网格达到下界。论文：
  <https://doi.org/10.1137/22M1510443>。它证明紧下界技术可以推广到更一般的张量收缩，
  但不等于普通 GEMM 的多层定理。
- **2024，SYRK/SYR2K/SYMM。** Al Daas 等对三个对称 BLAS-3 核同时给出 sequential 和
  distributed-memory 紧下界，并用三角块划分达到下界。论文：
  <https://arxiv.org/abs/2409.11304>。结构化输入改变了几何投影和可达算法，因此不能简单
  用普通 GEMM 公式替代。
- **2024，非对称内存。** Zhu、Hua、Jin 的 JOMMA 工作把不同处理器内存容量纳入 joint-
  communication 下界，并给出匹配算法。论文：<https://doi.org/10.1007/s11390-023-3489-y>。
  这一步连接了复制、负载不均衡和通信总量，但仍是单层并行抽象。

因此目前最值得追的空白是：对任意嵌套层数 (L\ge3)，同时允许跨层复用、复制、非对称容量
和不同通信代价时，给出逐层 tight profile，并证明一个实际 schedule 达到 profile。现有结果
分别覆盖了二层 I/O、并行 memory-independent 项、非对称单层内存或特定结构化核；它们尚未
合成为一个统一 theorem。这个缺口与本项目的 exact envelope/chain 实验直接衔接：先从三层
可分解 processor family 提取可证明的边界，再尝试推广到一般 (P_1\ge P_2\ge\cdots\ge P_L)。

## 35. 精确 lower-envelope overlay 证书

新增 `work/exact_overlay_2d.py`，避免直接枚举所有 equality-line 两两交点。算法先精确提取
每个 lower envelope 上实际活动的 equality 边段，再枚举这些边段的端点和 overlay 交点。
在每个 overlay cell 内，$N/I$ 是分母为正的 affine-fractional 函数，因此最大值出现在
cell vertex；这使候选集可以显著缩小而不牺牲 exactness。

它与原始 exact arrangement 在以下实例上给出完全相同的结果：

- $(30,15,3)$：$13/12$；
- $(56,28,14,2)$：$803/721$；
- $(80,40,20,4)$：$226/205$；
- $(60,20,10,2)$：$83/76$；
- $(48,24,12,6,2)$：$53/51$。

对于此前最大的复合实例

$$
(P_1,P_2,P_3)=(197406,98703,99),
$$

得到完整有理数证书：

$$
\max_{0\le y\le z\le1}\frac{N(z,y)}{I(z,y)}
=\frac{14817}{10034}\approx1.4766792904,
$$

最大点为 $(z,y)=(1,1/99)$，对应

$$
I=\frac{100340}{3257199},\qquad N=\frac{4490}{98703}.
$$

该验证只需 74 个 overlay 候选点和 167 个活动边段；因此它已经不是浮点启发式，而是
针对该具体 hierarchy 的 exact global-max check。仍待解决的是把活动边段的结构写成关于
一般复合 $p,q$ 的参数化证明。

## 36. $p=99$ 活动集合的参数稳定性证据

对更大的 $q$ 运行 exact overlay：

- $q=10007$：$R=297231/199367\approx1.4908736150$；
- $q=100003$：$R=14850561/9951437\approx1.4923031719$。

两次都在 $(z,y)=(1,1/99)$ 达到最大值，并且都得到 74 个 overlay 候选点、167 条活动
边段，与 $q=997$ 完全相同。比值符合 endpoint 公式

$$
R(q)=\frac{297q+231}{199q+2277}.
$$

因此已有三个不同规模的 exact global checks 支持同一活动集合和同一边界公式；下一步是
将这些逐实例检查转化为关于 $q$ 的符号支配不等式，从而证明所有足够大的素数 $q$。

## 37. Overlay 算法的额外交叉验证

对 8 个较小层次结构

$$
(12,6,3),(18,6,3),(24,12,6),(36,18,6),
(40,20,10),(42,21,7),(54,27,9),(20,10,2)
$$

将 overlay 结果与旧版全 arrangement 精确算法比较，最大比值全部一致。后两个实例的最大
比值为 1 且最大点不唯一，因此代表点可以不同；这不影响 global maximum value 的验证。

## 38. $p=99$ envelope-cover 的参数化稳定性证书

新增 `work/prove_p99_envelope_stability.py`。令 $u=1/q$，其中 $q$ 是大于 99 的素数。每个
grid line 的系数都是 $u$ 的仿射函数；在 $q_0=997$ 处提取的 active lines 可以逐点支配
整个 $u\in[0,1/997]$ 区间内的所有竞争线。

证明检查只需三个域顶点 $(0,0),(1,0),(1,1)$ 和两个参数端点 $u=0,1/997$：固定 $u$ 后差值
对 $(z,y)$ 是 affine，固定域顶点后差值对 $u$ 是 affine。脚本输出：

```text
independent[0] total=162 active=56 uncovered=0
independent[1] total=54  active=24 uncovered=0
independent[2] total=18  active=10 uncovered=0
nested          total=162 active=51 uncovered=0
certificate=True for every prime q>=q0 at the envelope-cover level
```

因此 $p=99$ 族已经有了对所有素数 $q\ge997$ 的固定 finite envelope cover。这个证书还不
等于 global-ratio 定理，因为 overlay 的最大顶点可能随 $q$ 改变；剩余问题是对这组参数化
active lines 做 ratio-level 的符号支配证明。

## 39. $p=99$ ratio-level 的部分参数化证书

`work/check_p99_ratio_candidate_family.py` 将 $q_0=997$ 的活动边段提升为 $u=1/q$ 的符号
表达式，并检查目标边界函数

$$
R_*(u)=\frac{297+231u}{199+2277u}.
$$

在 2110 个去重候选表达式中，1292 个在 $q_0$ 位于 aspect-ratio 域内；其中 994 个在
$q=997$ 与 $q=100003$ 间选择到相同的 envelope branch。对所有 994 个候选，精确 root
isolation 验证

$$
R_*(u)-R_{candidate}(u)\ge0,
\qquad 0\le u\le1/997.
$$

输出为 `stable 994 bad endpoint 0` 和 `exact sign bad 0`。这一步还不是完整参数化定理，
因为尚未排除区间内部新出现、但在 $q_0$ 不可见的 equality edge；它把剩余问题进一步缩小为
“证明活动边段组合不会发生拓扑变化，或补齐所有潜在候选”的几何步骤。

## 40. 固定 cover 上的 edge-template 扫描

`work/scan_p99_edge_templates.py` 比较活动线 pair identity，而不是比较含有 $q$ 数值的
系数。对 $q=997,1009,10007,100003$ 以及有理采样 $q=10^6$，得到相同的 edge-pair 模板：

$$
(60,29,12,51)
$$

分别对应 P1、P2、P3 和 nested envelope。所有采样的 $u>0$ 都报告
`changed levels=[]`；只有 $u=0$ 的无穷 $q$ 极限出现退化、边对数量减少。该结果支持有限
素数区间内 overlay topology 稳定，但仍需用符号事件分析替代采样，才能成为完整证明。

## 41. Edge 端点的退化结构

对 $q_0=997$ 的活动边段端点做了 exact 支持关系统计。P1、P2、P3 和 nested 的非角点端点
数分别为 112、41、13、76；这些端点通常不是一般位置，而是多条 equality line 同时相交。
P1 中单个端点最多有 56 条 active-line 支持关系。

因此 edge-persistence 不能沿每个端点选一条唯一第三约束直接延拓；需要先按 equality-line
几何类型合并多重共点，再证明整组边段覆盖在参数区间内保持。这个退化结构是当前符号
拓扑证明的主要技术细节，也解释了简单三线事件枚举会出现大量伪事件。

## 42. 奇数复合 $p$ 的 exact global-overlay 扫描

新增 `work/scan_odd_p_exact_overlay.py`，对 $q=997$ 和 13 个奇数 $p$ 做 exact global
lower-envelope overlay。所有实例都在

$$
(z,y)=(1,1/p)
$$

达到最大值，包括 $p=9,15,21,25,27,33,35,45,49,63,77,99$ 等复合数。最大比值从
$p=3$ 的约 $1.2843$ 增长到 $p=99$ 的约 $1.47668$，继续逼近 $3/2$。

这组结果把边界最大结构从素数族扩展到多个复合因子族；当前仍需证明任意奇数复合 $p$
和足够大素数 $q$ 的活动集合及 ratio 支配关系。

## 43. 全部奇数 $p\le99$ 的 exact global 检查

固定 $q=997$，对全部 49 个奇数 $3\le p\le99$ 运行 exact overlay。每个实例的 global
maximizer 都是

$$
(z,y)=(1,1/p),
$$

没有出现内部最大点、其它边界最大点或超过 $3/2$ 的案例；最大比值为 $p=99$ 的
$14817/10034\approx1.47667929$。这为奇数复合 $p$ 的二维边界最大猜想提供了目前最完整的
有限参数验证。

## 44. 第二个大 $q$ 的全部奇数复核

对全部 49 个奇数 $3\le p\le99$ 在 $q=10007$ 上再次运行 exact overlay。所有 global
maximizer 仍为 $(z,y)=(1,1/p)$；最大实例为 $p=99$，其比值为

$$
\frac{297231}{199367}\approx1.490873615.
$$

结合 $q=997$ 的完整横截面，这进一步支持奇数复合族的边界最大结构和 $q$ 参数稳定性。

## 45. 奇数族的有限-$q$ 公式模式

endpoint 证书显示，全部奇数 $p$ 的 witness nested cost 统一为

$$
N_p(q)=\frac9{2p}+\frac7{2pq},
$$

而 independent cost 的常数项统一为

$$
I_{p,0}=\frac3p+\frac3{2p^2}.
$$

只有 $1/q$ 修正项依赖 $p$ 的 divisor structure。这给出一个更精确的研究目标：证明任意
奇数 $p$、素数 $q>p$ 的二维 global ratio 在 $(z,y)=(1,1/p)$ 达到，并按 $p$ 的因子结构
解析分类 $I_p(q)$ 的有限修正项。两组完整 exact 横截面支持这一统一猜想。

## 46. divisor-structure 有限-$q$ 公式

定义

$$
\sigma(n)=\min_{d\mid n}\left(\frac1d+\frac1{n/d}\right).
$$

对全部 49 个奇数 $p\le99$ 的 exact endpoint certificate，发现并验证了统一形式

$$
I_p(q)=\frac3p+\frac3{2p^2}+\frac{\sigma(2p)+\sigma(p)}q,
\qquad
N_p(q)=\frac9{2p}+\frac7{2pq}.
$$

$σ$ 项只依赖 $p$ 的 divisor structure，解释了复合 $p$ 的有限修正；常数项和 $q\to\infty$
极限则完全统一。脚本 `work/check_odd_p_boundary_formula.py` 输出
`checked=49 odd-p divisor-formula cases`。一般化证明需要控制 q 位于第二/第三坐标的
竞争分配，并给出一个只依赖 $p$ 的充分 $q$ 阈值。

## 47. Endpoint 公式的有限-$q$ 阈值

在 $(z,y)=(1,1/p)$ 处，每条 grid line 与兼容 chain 都可写成

$$
H(q)=A+B/q.
$$

`work/derive_odd_p_threshold.py` 对全部 49 个奇数 $3\le p\le99$ 精确枚举 independent
与 nested 的 endpoint 竞争项，并求出目标项对所有竞争项同时占优的整数阈值 $Q^*(p)$。
输出为 `checked=49 odd-p threshold cases`，且

$$
\max Q^*(p)=891 \quad (p=99).
$$

因此当前使用的 $q=997$ 已经超过所有这些有限 endpoint 证书的阈值；例如 $Q^*(81)=729$、
$Q^*(99)=891$。这为

$$
I_p(q)=\frac3p+\frac3{2p^2}+\frac{\sigma(2p)+\sigma(p)}q,
\qquad
N_p(q)=\frac9{2p}+\frac7{2pq}
$$

提供了可复核的“足够大 $q$”范围证据，但尚未给出二维 overlay 的全局最大值证明：仍需
排除随 $q$ 改变而出现的新 edge，并证明 ratio 在整个 $0\le y\le z\le1$ 上由该 endpoint
达到。

## 48. 文献 checkpoint（2026-10-03）

新增报告 `work/agent_reports/literature_gap.md` 对 2022 之后工作做了模型级核查。近年的
紧结果主要覆盖结构化 kernel（Multi-TTM、SYRK/SYR2K/SYMM）和两级 horizontal/vertical
joint cost（JOMMA）；2026 的 SFC-CA GEMM 是在若干一层/两层 regime 匹配已有下界的算法，
而 overlap 工作改变的是时间模型。当前未发现任意 $L\ge3$ nested GEMM 的普适 tight
per-level communication vector theorem。因此本项目的三层问题仍是一个真实 gap，但目前
只有 exact evidence 和待证 conjecture，不能宣称已有新定理。

这里的“未发现”不等于历史上没有任何多级通信结果：HCP 等特定层次化平台曾给出 LU/QR
等 kernel 的层级下界与算法。当前 gap 更窄，指 classical GEMM 在任意 $L\ge3$、允许
replication/recomputation/跨层驻留时的普适逐层 tight communication vector。

JOMMA 的更具体启示是：在 square GEMM 的两级 joint objective 中，读写权重改变时会出现
不同的 aspect-ratio regime；其算法能匹配对应标量 joint bound。这支持我们先做两层 sanity
check，再把三层目标写成 communication vector 或 support function，而不是简单相加各级
下界。

## 49. 四层 exact boundary 的扩大扫描

`work/scan_multilevel_boundary_hull.py` 在本地和 `retreat` CPU 机上运行 Fraction-exact
扫描。四层 hierarchy 的结果为：

```text
limit=48:  35 hierarchies, max 226/207  ≈ 1.09178744
limit=72:  93 hierarchies, max 803/721  ≈ 1.11373093
limit=120: 284 hierarchies, max 1331/1165 ≈ 1.14248927
limit=240: 1148 hierarchies, max 1137/916  ≈ 1.24126638
```

最大 limit=240 实例为 $(228,114,57,3)$，其 boundary 参数为 $t=1/3$。这些是反例搜索
证据，不是 tight theorem；它们没有超过 $3/2$，但仍需输出每个实例的 witness chain 和
逐层通信向量，才能判断是否存在某一级不能与其它级同时最优。

## 50. 反例搜索扩大与受限可组合命题

`work/agent_reports/counterexample_search.md` 记录了更大范围的 exact boundary 扫描：三层
limit=500 共 4107 个 hierarchy，最大 $1075/823\approx1.30620$；在 `retreat` 上三层
limit=1000 共 11217 个 hierarchy，最大

$$
\frac{726}{535}\approx1.35701
$$

，出现在 $(954,477,9)$、$t=1/9$。composite family $p\le30,q\le300$ 共检查 1556 个
参数，最大 $16525/11426\approx1.44626$，仍低于 $3/2$。这些扫描没有找到反例，但只
覆盖当前 $H$ proxy 和 $z/x=1$ 边界。

从 DP 结构可以提炼一个受限命题：若某个 aspect 点上，每一级 independent lower-envelope
都存在坐标逐层整除的最优 grid tuple，则这些 tuple 组成兼容 chain，nested envelope 等于
independent sum，overhead 为 1。非零 overhead 只能来自独立最优 grid 族无法同时选成兼容
链，通常发生在 envelope transition/breakpoint 附近。该命题解释了当前 ratio 的来源，但
仍不是完整通信模型中的 theorem。
## 51. p=99 topology-event 诊断

新增 `work/scan_p99_topology_events.py`，对 p=99 的 fixed active-line cover 枚举
$u=1/q$ 的 pair/domain 与 triple-concurrence 事件。复核输出为：258 个 pair-domain
多项式（257 个一次），6356 个 triple determinant 多项式（5980 个一次、375 个二次），
在 $(0,1/997)$ 内的候选根分别为 11 和 205；逐个检查后 `actual events=0`。

这说明当前最短证明路线确实是：先对 375 个二次根补上 exact algebraic/Sturm 可行性判号，
从而证明 topology 不发生变化；再对固定有限候选点做一元 ratio sign certificate。当前一次
根筛选为 exact，二次根仍有数值过滤，因此该结果是强诊断证据，不应直接写成完成的 p=99
global theorem。

## 54. 一般奇数 endpoint 公式的阈值定理与最小失败

报告 `work/agent_reports/odd_p_endpoint.md` 将 endpoint 处的所有 grid/chain cost 写成
$A+B/q$，并证明 divisor-structure 公式在有限 crossing threshold 之后成立。对全部 49 个
奇数 $p\le99$，`derive_odd_p_threshold.py` 的最大阈值为 $Q^*=891$。

“对所有素数 $q>p$ 立即成立”是错误的。最小测试失败为 $(p,q)=(9,11)$：实际

$$
I=\frac{400}{891},\qquad N=\frac{53}{99},\qquad R=\frac{477}{400},
$$

因为 $(2pq)$ 层的 grid $(22,3,3)$ 击败了 divisor target grid $(11,3,6)$。因此后续一般
奇数命题必须显式包含 $q\ge Q^*(p)$，并把 endpoint 公式与二维 global-max 证明分开。

## 53. p=99 quadratic event 的 Sturm 证书

修正 `work/check_p99_quadratic_sturm.py` 对 SymPy 区间端点计数的处理后，375 个 unique
quadratic triple determinants 的 exact 结果为：

```text
source_triples=523
sturm_roots_open_interval=0
endpoint_polys=4
```

四个例外多项式都只在 $u=0$ 消失，且交线方向为 `parallel_or_coincident`；在开区间
$(0,1/997)$ 内没有 quadratic topology event。这使 p=99 的 fixed-cover topology lemma
基本完成。剩余工作是单独处理 $u=0$ 的退化 overlay，并完成现有 994 个 candidate branches
的 ratio-level exact sign certificate；因此 p=99 global theorem 仍处于“接近完成但未闭合”的状态。

## 52. 反例搜索周期的结论

本轮 exact boundary 搜索扩大到三层 limit=1000（11217 个 hierarchy）、四层 limit=480
（4077 个 hierarchy）以及 composite endpoint family $p\le30,q\le300$（1556 个参数），
仍未发现超过 $3/2$ 的反例。最大三层值为 $726/535\approx1.35701$，最大 composite
endpoint 值为 $16525/11426\approx1.44626$；四层 limit=480 的最大值为
$2275/1776\approx1.28097$。

这些结果只支持当前 $H$ proxy、坐标整除型 nested chain 和 $z/x=1$ 边界上的受限命题，
不能直接升级为实际 message-volume 或完整二维定理。下一轮应优先完成 p=99 的 Sturm
event exclusion，而不是继续无目标扩大数值范围。
## 55. p=99 ratio-level wrapper

`work/check_p99_ratio_all_u.py` 将正 $u$ 的 994 个 symbolic candidate sign checks 与
$u=0$ 的退化 overlay 合并。exact 输出为：

```text
positive_u_candidates 994
positive_u_exact_sign_failures 0
u0_edge_counts (4, 4, 12, 28)
u0_overlay_points 12 segments 48
u0_best_ratio 297/199 at (1,1/99)
certificate=True
```

结合 quadratic Sturm root exclusion、linear event exact owner-gap scan 和 fixed active-cover，
p=99 的参数化 global-ratio 证明已经接近闭合。形式上的最后一步是写出 combinatorial
continuity lemma：在没有 active event 的正 $u$ 区间内，$q_0$ 的 994 个 candidate branches
覆盖全部 overlay vertices；并将 $u=0$ 的退化 overlay 作为独立边界情况纳入定理。
## 56. Combinatorial continuity for p=99

For $u=1/q\in(0,1/997]$, the exact scripts
`work/check_p99_linear_events.py` and `work/check_p99_quadratic_sturm.py` exclude every active
topology event: the linear scan reports zero active vertex, active parallel, identity, and triple
events; the 375 quadratic determinants have zero roots in the open interval. These are exactly the
possible changes for a finite arrangement of affine-in-$u$ lines over a polygon: an equality can
change its cell complex only through a boundary parallelism/vertex passage, a triple concurrence,
or a line identity. Thus the active envelope and overlay cell complex is constant on the connected
positive-$u$ interval. Since $N/I$ is affine-fractional with positive denominator on each cell, its
maximum is attained at an overlay vertex. The 994 symbolic q0-visible branches therefore cover all
positive-$u$ candidate vertices; their exact sign check has zero failures. The $u=0$ duplicate-line
degeneration is handled by a separate exact overlay, whose maximum is $297/199$ at $(1,1/99)$.

This is the formal bridge needed to state the fixed-$p$ result: for every prime $q\ge997$, the
p=99 ratio is maximized at $(z,y)=(1,1/99)$ with

$$
R(q)=\frac{297q+231}{199q+2277}.
$$

The remaining presentation task is to package the event-exclusion implication as a standalone
lemma; the computational certificates themselves now cover the positive interval and the limiting
slice.
## 57. 一般素数 p 的 endpoint 公式已可符号证明

运行 `work/prove_prime_p_family.py` 得到 132 个 Bernstein polynomial comparisons 全部通过，
覆盖 $t=1/p\in[0,1/3]$ 和 $q>p$ 的 endpoint 竞争。脚本给出：

$$
I_p(q)=\frac3p+\frac3{2p^2}+\frac{3/2+2/p}{q},
\qquad
N_p(q)=\frac9{2p}+\frac7{2pq},
$$

以及

$$
R_p(q)=\frac{p(9q+7)}{(6p+3)q+3p^2+4p}.
$$

`prove_prime_chain_dominance_symbolic.py` 另外对 11 个非模板 compatible chain 做了符号
支配检查。这把“素数 p 的 endpoint witness”从有限扫描提升为一般 $p$ 的 exact endpoint
定理；但它仍只固定在 $(z,y)=(1,1/p)$，尚未证明二维 global maximizer。复合 $p$ 还需要
保留 $sigma(p),sigma(2p)$ 的因子结构并处理更多竞争模板。
## 58. p=3 小素数探针：prime-q endpoint 与 q>=67 fixed-cover candidate

对三层模型 $(P_1,P_2,P_3)=(6q,3q,3)$ 做 exact overlay 后，小于 300 的全部 60 个
prime $q$ 都在
$(z,y)=(1,1/3)$ 达到最大值，并符合

$$
R_3(q)=\frac{27q+21}{21q+39}.
$$

不过 composite $q$ 的因子结构会改变最优 grid。$q=44$ 的 exact 最大值是
$311/299$，而上述 endpoint expression 给出 $403/321$，所以不能把 prime-q 公式
扩展到所有整数 $q>3$。

固定 anchor 需要精确选择。早期辅助脚本的 floor bug 曾产生 $u=2/87$ 和 $u=2/141$，
这些数值已撤销。修正 symbolic replacement 后，$q_0=29,47,61$ 都有 active triple
event $u=1/66$、位置 $(z,y)=(0,0)$；取 $q_0=67$ 后，31 个 unique quadratic
determinants 的 exact Sturm scan 与 linear event scan 都没有 active event，54 个
q0-visible ratio branches 也全部通过 exact sign check；另有 envelope-cover script 对
27/9/3 independent grids 与 27 条 nested chains 报告 uncovered=0。由此，p=3 已有覆盖
prime $q\ge67$ 的 fixed-cover 证书候选，但还需要把 continuity lemma 写成正式证明。

详见 `work/agent_reports/p3_probe.md`。
## 59. Corrected small-prime fixed-cover certificates

审计并修正了 topology 辅助脚本中含 anchor prime 的 reciprocal replacement：含有 $q_0$
因子的项 $1/(dq)$ 必须写成 $u/d$，不能使用整数 floor。修正后，以 $q_0=67$ 对
$p=3,5,7$ 都得到：

```text
independent[0] total=27 active=16 uncovered=0
independent[1] total=9 active=8 uncovered=0
independent[2] total=3 active=3 uncovered=0
nested total=27 active=16 uncovered=0
```

三个 $p$ 的 quadratic Sturm、linear-event 与 ratio checks 都通过；ratio candidate 分支
数为 54、37、31，候选最大值为

$$
R_p(q)=\frac{p(9q+7)}{(6p+3)q+3p^2+4p}
$$

且位置为 $(z,y)=(1,1/p)$。direct exact-global 另外验证了 $p=5$ 的 43 个、$p=7$ 的
42 个 prime-$q$ 实例，$p=3$ 验证了 300 以下全部 60 个素数。

这仍是计算证书候选，不是任意 $p$ 的正式定理；$p\ge23$ 可能需要更大 anchor，且有限
arrangement 的 continuity lemma 仍需写出。
## 60. p=99 topology 证书的审计修正

早期 topology 辅助脚本将含 anchor prime 的 $1/(d q)$ 错写成整数 floor。修正 symbolic
replacement 后，p=99 的权威输出为：

```text
quadratic_unique 1405 source_triples 11219
sturm_roots_open_interval 0 endpoint_polys 146
parallel_roots 0 active_pair_parallel_roots 0
active_linear_triple_events 0
```

ratio wrapper 仍然是 994 个 positive-$u$ branches、0 个 exact sign failures，且退化
$u=0$ slice 的最大值仍为 $297/199$。因此 p=99 的证书方向保持不变，但旧的 375/523 与
57-root 计数只应保留为历史诊断值。
## 61. Prime-p anchor scan

修正后的 exact pipeline 已对一组 prime p 扫描到 $p=101$。当 $p\le31$ 时取 $q_0=67$；
更大的 p 取严格大于 $2p$ 的下一个测试素数。所有扫描实例都通过 envelope-cover
dominance、active-event exclusion 与 ratio sign checks，候选值为

$$
R_p(q)=\frac{p(9q+7)}{(6p+3)q+3p^2+4p}.
$$

这提示 prime-p 的阈值可能满足 $q_0\gtrsim2p$，但仍缺少正式 continuity lemma。复合
$p=99$ 显示 topology threshold 与 ratio threshold 不同：$q_0=199$ topology 稳定却有
204 个 ratio failures，$q_0=997$ 才通过。详细数据见 `work/agent_reports/prime_p_anchor_scan.md`。
## 62. Finite-arrangement continuity lemma

已将 fixed-anchor 证明桥梁单独写入 `work/agent_reports/continuity_lemma.md`：只要有限
affine-in-$u$ line arrangement 没有 active boundary passage、parallelism、triple
concurrence 或 line identity，active lower-envelope complex 和四-envelope overlay 的
combinatorial type 在参数区间内保持不变。overlay vertex 坐标是 rational functions，且
$N/I$ 在每个 cell 内是正分母下的 linear-fractional function，因此全局 ratio 只需检查
有限 vertex branches；$u=0$ duplicate-line degeneration 单独 exact overlay。

这完成了证明结构的文字化；quadratic event checker 也已升级为 isolated algebraic roots
上的 polynomial gcd/Sturm sign checks。剩余工作是一般 candidate-line family、把有限证书
接到所有 prime-q grid templates 的正式论证，以及任意多层命题。
## 63. 证明目标的分层

对 prime family $(2pq,pq,p)$，三条 nested chain 的平均已经证明全域 $N/I\le3/2$，而
witness 的双重极限达到 $3/2$。因此当前真正未闭合的是更强的 finite-q sharpened
global-max formula $R_p(q)$，而不是该 family 的 $3/2$ supremum。anchor scan 与 continuity
lemma 都服务于这个更锋利的命题；它也解释了复合 p=99 的 topology/ratio threshold 分离。
## 64. 文献复核：并行紧下界的近期边界

最近文献复核后，当前领域边界可以更准确地表述为：

- Al Daas et al. 的 2022 结果已经给出 rectangular classical GEMM 的 memory-independent
  parallel lower bound 紧常数，并分析了匹配的 1D/2D/3D processor-grid algorithm；这条主线
  不是当前的空白。
- 2024/2025 的工作把同类 HBL/优化方法扩展到 SYRK、SYR2K、SYMM 等 symmetric kernels，
  并给出 sequential 与 distributed-memory 的 matching algorithms。
- Multi-TTM 已有 parallel communication lower bound 与 matching algorithm；2025 的 JOMMA
  则处理 horizontal/vertical communication 的 joint objective，且明确讨论 asymmetric
  memories 下的 tradeoff。
- 因此本项目的可辩护 gap 不是“并行 GEMM 没有 tight lower bound”，而是：在 nested
  processor-grid compatibility、跨层 residency/replication、非对称容量和任意 $L\ge3$
  层同时存在时，能否给出一个统一的 per-level communication profile，并由同一个 schedule
  同时达到各层 bound。

可核对的原始来源：[2022 tight memory-independent GEMM](https://arxiv.org/abs/2205.13407)、
[symmetric kernels](https://arxiv.org/abs/2409.11304)、
[Multi-TTM](https://epubs.siam.org/doi/10.1137/22M1510443)、
[JOMMA asymmetric-memory joint communication](https://jcst.ict.ac.cn/article/doi/10.1007/s11390-023-3489-y?viewType=citedby-info)。

## 65. Direct exact-global scan beyond the anchor certificates

为检验 fixed-anchor 证书是否反映真实的有限参数最大值，`check_prime_p_global.py` 对
$p=23,29,37,47,59,71,83,97$ 的多个 prime $q$ 做了完整的 exact overlay 枚举。总计
141 个 $(p,q)$ 实例全部通过：每个实例的全局最大值都在
$(z,y)=(1,1/p)$，没有发现内部 cell 或其他 overlay vertex 超过候选值

$$
R_p(q)=\frac{p(9q+7)}{(6p+3)q+3p^2+4p}.
$$

这不是对任意 prime $p,q$ 的证明，但它把直接全局检查从 $p=3,5,7$ 扩展到更大的 p，且
与 $q_0\gtrsim2p$ 的 fixed-cover 模式一致。当前最稳妥的表述仍是“计算证书支持的猜想”；
正式结论需要把一般 line-family、continuity lemma 和所有 prime-q 模板写成参数化证明。

## 66. Radial derivative certificate: a route to the full two-dimensional theorem

本轮把完整二维缺口进一步结构化。令 $(x,z,y)=(1,s,st)$。在一个 active overlay cell 上，
$N/I$ 对 $s$ 的导数符号由一条关于 $t$ 的一次式决定。对 $q>2p$，精确半平面可行性检查在
$p=3,5,23,37,97$ 的代表参数中都找到恰好 8 个 full-dimensional active combinations；对这
8 类，导数公式可以参数化并在各自的 $t$ 投影区间上证明非负。关键两式共享

$$
A(p,q)=6p^2q+9p^2-6pq^2-24pq-16p+6q^2+9q,
$$

且写成 $q=2p+r$ 后

$$
A=-12p^3-18p^2r-15p^2-6(p-1)r^2+2p+9r<0.
$$

因此，若能把“恰好八类 active cells”推广为任意 prime $q>2p$ 的参数化 envelope 分类，
就能证明径向单调性，再与边界定理合并得到完整二维 sharp formula。详细公式和有限检查见
`work/agent_reports/radial_monotonicity_certificate.md` 与 `work/check_prime_radial_cells.py`。

这一步尚未被宣称为任意 $p,q$ 的定理：目前缺少的是 active-cell 分类的普适不等式证明，而
不是导数符号本身。

## 67. Expanded boundary and radial checks

`check_prime_p_boundary_theorem.py` 已对 $p\le101$ 的代表素数集合与 $q$ 集合完成 425 个
exact boundary cases，包括 $q$ 接近 $p$ 和显著大于 $p$ 的情形，全部得到边界最大点
$t=1/p$ 与 $R_p(q)$。另一个独立的 exact rational radial grid scan 以步长 $1/80$
检查了 52 个参数组合，没有发现负的相邻径向增量。后者仍是诊断证据；八-cell half-plane
证书则是更强的有限实例检查。

导数代数的独立 SymPy 证书已加入 `work/prove_prime_radial_derivatives.py`；它会打印八类
$D(t)$ 的因式分解，并验证 $q=2p+r$ 时共享多项式 $A(p,q)$ 的正性分组，输出
`symbolic derivative certificate=True under p>=3, q>2p`。这验证的是导数步骤，仍不替代
active-cell 模板的普适分类。

## 68. Four-chain reduction of the interior proof

又发现一个更简洁的上界路线：只取四条合法 nested chains，令它们的 lower envelope 为 $U$。
因为 $N\le U$，只要证明 $U/I\le R_p(q)$，并在 $(1,1/p)$ 处验证 $U=N$，就能得到原问题
的 sharp upper bound，而不必先分类全部 16 条 nested active lines。

新增 `work/check_prime_four_chain_bound.py` 做 exact arrangement、full-dimensional radial
cell 检查和 witness equality 检查；对 19 个 $q>2p$ 参数实例全部得到 `cells=8`、
`radial_bad=0`、`witness_equality=True`，且 $U/I$ 的 exact global maximum 正好是
$R_p(q)$。因此普适证明的剩余部分进一步收窄为：证明这四条 chain 与 16/8/3 条 independent
active lines 组成的八-cell template 对任意 $q>2p$ 都成立。

## 69. Independent envelope cover is parameterized

新增 `work/prove_prime_independent_cover.py`。它固定 $2pq$ 层的 16 条、$pq$ 层的 8 条、$p$
层的 3 条 candidate lines，并对所有被省略的 12 个 divisor grids 证明：在三角域三个顶点上，
某条 candidate line 始终不高于它；差值在 $p=3+a,q=2p+r$ 下逐项非负。因此对所有
$p\ge3,q>2p$，independent lower envelope 已经由固定模板覆盖，不再依赖数值 active-line
猜测。剩余普适步骤只剩四条 chain 与这组固定 line 的八-cell arrangement 分类。

## 70. Restricted three-level theorem closed

前面把“八-cell active template 的普适分类”列为剩余缺口；本轮发现不需要这一步。先用
`prove_prime_independent_cover.py` 和 `prove_prime_reduced_envelopes.py` 将 independent envelope
精确化为 $(A,B,C,D,E)$、$(F,G)$、$H$ 三组 min，再用四条合法 chain 构造 $U\ge N$。链比较
直接给出 $U$ 的三个 t-regime；逐个可能的 min 组合只产生七种径向导数，
`prove_prime_full_2d_upper_bound.py` 验证了它们的符号恒非负。

因此对素数 $p\ge3,q>2p$，在本项目的三层 divisibility model 中已经得到完整结论：

$$
\max_{0\le y\le z\le1}\frac{N(z,y)}{I(z,y)}
=\frac{p(9q+7)}{(6p+3)q+3p^2+4p},
$$

最大点为 $(z,y)=(1,1/p)$。详细证明见
`work/agent_reports/prime_family_full_theorem.md`。这不是任意多层 GEMM 的通信下界定理，而是
一个已经闭合的三层参数化子问题；更一般的 multilevel/replication/asymmetric-cost gap 仍然存在。

## 71. Composite-p counterexamples: the prime hypothesis is structural

把 $p$ 放宽到 composite 后，素数族的 sharp formula 会失败。完整 exact arrangement 对
$(p,q)=(6,13)$（层级 $(156,78,6)$）得到

$$
\max N/I=135/113
$$

最大点为 $(z,y)=(1,29/195)$，而素数公式只给 $248/213$。在这个点，$I=113/180$、
$N=3/4$；一个 independent minimizer 使用 $(26,2,3)$、$(13,2,3)$、$(6,1,1)$，一个
nested minimizer 为 $(39,2,2)\to(39,1,2)\to(3,1,2)$。

更大的 exact 反例 $(p,q)=(49,101)$ 在 $(1,1/49)$ 处达到 $11221/8039$，显著高于素数公式
$11221/9349$。对 composite $p\le50$、prime $q\le500$、$q>2p$ 的 exact boundary scan
发现 1247 个反例；详情见 `work/agent_reports/composite_formula_gap.md`。

这说明素数条件来自 divisor-profile geometry，而不是技术性假设。下一步需要研究按 $p$
的因子分解分类的 envelope，或寻找不依赖素性的新上界。

## 72. Composite factors can move the maximizer into the interior

完整二维 exact arrangement 还发现：$p=10,q=23$ 的最大值为

$$
4531/3666
$$

且最大点是 $(z,y)=(49/115,1/5)$；$p=14,q=29$ 的最大值为
$248675/196974$，最大点是 $(61/145,1/7)$。两者都严格高于各自的 boundary maximum。
因此 composite divisor profile 不仅改变数值，也会破坏 prime family 的径向单调结构；后续
需要按因子分解研究 interior envelope，而不能只扫描 $z=1$ 边界。

## 73. More exact composite cases from retreat

为避免只依赖小参数，使用 retreat CPU 完成了两个更大的完整二维 exact arrangement：

* $(p,q)=(22,47)$：
  \[
  \max N/I=1005565/775602\approx1.2964961411,
  \quad (z,y)=(97/235,1/11).
  \]
* $(p,q)=(26,53)$：
  \[
  \max N/I=1505465/1155702\approx1.3026411653,
  \quad (z,y)=(109/265,1/13).
  \]

相应的素数族公式分别只有 $1892/1577\approx1.1997464$ 与
$12584/10559\approx1.1917795$，差距远大于精度误差。

两个实例都使用 54/27/9 个候选 grids、24/16/8 个 active independent lines 和 31 条
active nested lines；arrangement vertices 分别为 289015 与 291599。最大点继续落在
$y=1/r$（这里 $p=2r$）但 $z$ 和比值呈现 divisor-profile 依赖。它们是“复合参数需要
分类”而非“素数证明略有技术缺口”的进一步证据；尚未形成任意 composite $p$ 的闭式定理。

四个 exact cases $p=2r, q=4r+3$（$r=5,7,11,13$）还显示一个候选子族：

$$
(z,y)=\left(\frac{2q+3}{5q},\frac1r\right),\qquad
\frac NI=\frac{5qr(8q+13)}{28q^2r+15q^2+6qr^2+52qr+9r^2}.
$$

这来自相同 active-line pattern 的代入，暂时只能称为 conjectural subfamily。需要先证明
factor conditions 下这些 lines 的 envelope dominance，再证明对应 cell 是全局最大；不能把它
外推为所有复合 $p$ 的公式。

## 74. Literature refresh as of 2026-10-03

定向检索仍支持下面的判断：2022 年的 rectangular classical GEMM 工作已经给出三种
processor-grid regime 的 memory-independent tight constants 和 matching 1D/2D/3D schedules；
2024 年的后续工作把紧下界扩展到 SYRK、SYR2K、SYMM，2025 年的 JOMMA 则研究 asymmetric
memory 中 horizontal/vertical joint communication。当前没有检索到取代 general GEMM theorem
的统一新结果。因此更可信的 gap 是任意多层 nested hierarchy、跨层 replication 与
processor-grid compatibility 的同时 tightness，以及 composite divisor-profile 的 envelope
分类，而不是“并行 GEMM 还没有紧下界”。

## 75. Exact completion for $(p,q)=(18,37)$

retreat 上的完整二维 exact arrangement 已完成：

\[
\max N/I=13905/10826\approx1.2844079069,
\qquad (z,y)=\left(1,77/1665\right).
\]

该实例有 108/54/18 个候选 grids、38/25/11 个 active independent lines、52 条 active
nested lines，以及 2071814 个 arrangement vertices。素数族表达式仅为 $120/101$。这说明
$p=2r$ 的候选公式只适用于特定 factor profile；当 $r=9$ 时，最大点回到 $z=1$，且
$y\ne1/r$。

四个正例的 nested envelope 都由相同的四条 chain 产生（内层到外层）：

```text
(r,2q,2) -> (r,2q,1) -> (r,2,1)
(2r,q,2) -> (r,q,2)   -> (r,1,2)
(2r,q,2) -> (2r,q,1)  -> (2r,1,1)
(2r,2q,1) -> (r,2q,1) -> (r,2,1)
```

对应 independent minimizers 为 $(q,r,4)$、$(q,r,2)$、$(r,2,1)$。因此下一步可以尝试在
$r,q$ 为相应素数且 $q=4r+3$ 的条件下，符号化排除其余 divisor grids；$r=9$ 的结果表明
没有素因子条件时该模板会失效。

`work/check_2r_prime_subfamily.py` 已对 $r=5,7,11,13,17$、$q=4r+3$ 做 exact
local-envelope check；五个实例都符合候选模板。新样本 $r=17,q=71$ 的候选点为
$(29/71,1/17)$，候选比值为 $701267/532722$；随后已由 retreat 的全局 arrangement
验证。

retreat 随后完成了该实例的全局 exact arrangement：

\[
(p,q)=(34,71):\qquad
\max N/I=701267/532722\approx1.3163845308,
\quad (z,y)=(29/71,1/17).
\]

结果与候选子族公式完全一致；候选 grids 为 54/27/9，active independent lines 为 24/16/8，
active nested lines 为 31，arrangement vertices 为 296028。素数族公式只有
$21964/18301$。这把该候选子族的 global exact 样本扩展到五个，但仍不足以构成普适定理。

又完成了第六个全局样本：

\[
(p,q)=(38,79):\qquad
\max N/I=4840725/3666242\approx1.3203506479,
\quad (z,y)=(161/395,1/19).
\]

候选 grids 为 54/27/9，active independent lines 为 24/16/8，active nested lines 为 31，
arrangement vertices 为 296851。它继续精确符合 $p=2r,q=4r+3$ 候选公式；素数族公式仅为
$27284/22733$。

`work/prove_2r_subfamily_independent_cover.py` 已闭合候选子族的 independent envelope：在
$r,q$ 为互异素数且 $q=4r+3$ 的固定 divisor profile 下，54/27/9 个 grids 中的 24/16/8 条
active lines 足以覆盖其余 lines，
且每个 dominance 差值在 $r\ge5$ 下都有 exact polynomial positivity certificate。下一步是
把八条 nested chains 的 upper envelope 做参数化证明；其六个样本的 exact arrangement 已
全部通过。

`work/prove_2r_subfamily_chain_forms.py` 已符号验证四条 chain 在候选点同时取值
$N_0=(32r+37)/(4r(4r+3))$，因此 numerator 的候选公式与 witness equality 已闭合。剩余
工作是证明八链有限 arrangement 上的全局 $U_8/I$ 上界。

前四条 chain 的 affine forms 已整理在复合参数报告中；复合 profile 需要再加入四条 chain，
令 $U_8=\min(C_1,\ldots,C_8)$，则 $N\le U_8$，并且在候选最大点处取等。剩余问题
是证明有限 25-line arrangement 上的线性分式不等式：$U_8/I$ 不超过候选闭式比值。

四条 chain 对 composite profile 在全域上过松；加入四条额外兼容 chain 后，得到八链上包络
$U_8$，满足 $N\le U_8$。`work/check_2r_subfamily_eight_chain_bound.py` 对 10/5/2 条
sorted independent lines 与 8 条 chain 做 exact arrangement，六个样本全部达到候选值。
因此全局证明的剩余部分已缩减为固定 divisor profile 的 25-line 参数化 arrangement。

sorted-grid reduction 也已单独验证：`work/prove_sorted_factor_rearrangement.py` 对
$1\ge z\ge y\ge0$ 的六个因子排列给出 exact nonnegative-difference certificate，因此
10/5/2 条 sorted lines 的 reduction 有 rearrangement-inequality 依据。

八链 cell 枚举显示，$r=5,7,11,17,19$ 的 proving-cell 数分别为 36、35、34、34、34。
每个 cell 都存在一条 chain 使线性分式上界在该 cell 的 exact vertices 成立，但 topology
会在参数阈值处变化；正式证明需要把这些 threshold 分支显式列出。

对稳定的大参数分支，`work/probe_2r_subfamily_symbolic_cells.py` 已完成 33-cell symbolic
lift：在 $r=21$ 枚举的 121 个 vertices 全部通过 $r=21+a$ 的 polynomial sign check，并在
$r=21,23,50,100$ 验证 cell 数均为 33。还需补齐小参数分支，以及证明没有未枚举的 cell 在
$r\ge21$ 出现。

### 当前拓扑审计与更大样本

新增 `work/check_2r_subfamily_topology_stability.py`，用三层 independent owner 与 chain owner
编码 cell 身份，并用 `proving_only=False` 统计所有可行的 full-dimensional cells，而不只统计
已经能证明候选上界的 cells。在 $r=21,23,50,100$，均得到 33 个 cell 且 owner/chain
signature 完全一致：

```text
samples=[(21,33,True),(23,33,True),(50,33,True),(100,33,True)]
```

这把“大参数分支稳定”从 proving-cell 检查推进到全部可行 cell 的有限审计，但还不是任意
实数 $r\ge21$ 的 no-new-cell 符号证明。

在 retreat CPU 上又对 14 个更大的素数参数对
$(r,q)=(31,127),(37,151),(41,167),(47,191),(59,239),(67,271),(89,359),
(107,431),(109,439),(149,599),(151,607),(157,631),(179,719),(181,727)$
运行完整 25-line $U_8/I$ arrangement。全部精确命中
$z=(2q+3)/(5q),y=1/r$ 及闭式比值；连同此前六个样本，共 20 个 exact global cases。
这些结果仍针对固定 divisor profile，不能替代参数化的 no-new-cell 证明。

## Formal three-level model (v0)

The next phase is now specified in [three-level-nested-communication-model.md](three-level-nested-communication-model.md). The base object is square classical GEMM (C=AB) with a static three-level processor hierarchy, no recomputation, counted replication, balanced work, and edge-based word volume. For (P_1\ge P_2\ge P_3), a grid chain satisfies componentwise divisibility (g_3\preceq g_2\preceq g_1).

The normalized experiment uses

$$
\ell(g;z,y)=\frac1{ab}+\frac{z}{ac}+\frac{y}{bc},
\qquad 0\le y\le z\le1,
$$

then defines the independent envelope (I) and compatible-chain envelope (N). The research theorem is no longer stated as an unconditional claim about (N/I): the missing lifting step is to derive the physical scale factors (\kappa_\ell(n,P_\ell,M_\ell)) from a GEMM DAG/phase argument and prove

$$
Q_{\mathrm{vol}}(\mathcal A;z,y)\ge N(z,y)-O(n^2).
$$

A matching blocked schedule for every active chain is required for tightness. `work/check_three_level_model.py` verifies the normalized line, compatibility relation, envelope counts, and (N\ge I) sanity condition for (P^*=(460,230,10)); it does not claim the physical lower-bound theorem is proved.

### One-level recovery checkpoint

`work/check_one_level_recovery.py` restores the unnormalized rectangular GEMM line

$$
\lambda_{m,k,n}(a,b,c)=\frac{mk}{ab}+\frac{mn}{ac}+\frac{kn}{bc}.
$$

For a square problem and cubic grid this is (3n^2/P^{2/3}), so the current affine geometry recovers the standard one-level memory-independent scaling. This is a units/geometry check only; the HBL lower-bound proof and finite-memory term are still separate obligations.

### Static-grid theorem checkpoint

`outputs/static-grid-ownership-lemma.md` isolates a restricted theorem that is actually provable by direct ownership counting. For a fixed (a\times b\times c) block grid with one-copy inputs and one-time products,

$$
V_{\mathrm{grid}}\ge(c-1)mk+(a-1)kn+(b-1)mn.
$$

A matching broadcast/reduction schedule reaches this count in the corresponding communication topology. Componentwise-coarsened grids across the three charged edges therefore give a **T3-static** nested theorem. This is a real lower-bound result under explicit static ownership assumptions; arbitrary dynamic schedules remain outside the theorem.
