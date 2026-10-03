# 2022 之后并行矩阵乘法通信下界进展（截至 2026-10-03）

## 结论先行

本轮检索没有发现一篇已经解决“任意 (L\ge 3) 层嵌套处理器/内存层级、允许复制与跨层复用、容量可非对称”的 classical GEMM 普适紧通信下界论文。2022 年的 memory-independent rectangular GEMM 紧常数结果仍然是普通稠密 GEMM 的核心基线。2023--2026 年的进展主要沿三条线展开：

1. **把同一类 HBL/几何不等式方法扩展到结构化算子**（Multi-TTM、SYRK/SYR2K/SYMM、随机矩阵 sketching），并在各自模型中给出 matching algorithm；
2. **把水平通信和单个垂直内存层级合并计价**，尤其是非对称读写成本（JOMMA）；
3. **改进算法、调度和重叠模型**（SFC-CA GEMM、overlap 条件、matrix-chain 处理），但这些工作没有给出任意多层 hierarchy 的统一 lower-bound theorem。

因此，对我们的三层 overlay 问题，最新文献提供了可复用的证明组件和模型警告，却没有直接替代当前的 exact envelope 研究。

## 论文清单与影响

### 1. Al Daas–Ballard–Grigori–Kumar–Rouse，SPAA 2022 / arXiv 2022

**论文：** [Tight Memory-Independent Parallel Matrix Multiplication Communication Lower Bounds](https://arxiv.org/abs/2205.13407)，SPAA DOI [10.1145/3490148.3538552](https://doi.org/10.1145/3490148.3538552)。

**模型与结果。** 经典矩形乘法 (n_1\times n_2) 乘 (n_2\times n_3)，(P) 个分布式内存处理器；初始输入各一份、最终输出一份，并假定计算或数据 load-balanced。论文给出即使每个处理器本地内存无限也成立的 memory-independent bandwidth lower bound，按 (P) 相对三个矩阵长宽比的位置分成三个 regime，并把 leading constants 做到紧。其构造的 3D processor-grid 算法在三个 regime 达到相同常数。

**紧性范围。** 对单层 distributed-memory classical GEMM 紧；不是嵌套层级定理，也不处理每一级独立代价向量、复制策略的 Pareto frontier 或任意加权跨层成本。

**对我们的直接影响。** 这篇结果应作为三层模型最外层/无限本地内存极限的基准 (N) 或 (I)。证明中的“访问数据投影 + 受约束优化”与我们使用的 lower-envelope 形式兼容，但不能直接推出“逐层下界同时可达”。

### 2. Al Daas–Ballard–Grigori–Kumar–Rouse，SIAM JMAA 2024

**论文：** [Communication Lower Bounds and Optimal Algorithms for Multiple Tensor-Times-Matrix Computation](https://epubs.siam.org/doi/10.1137/22M1510443)，DOI [10.1137/22M1510443](https://doi.org/10.1137/22M1510443)。

**模型与结果。** Multi-TTM 是 Tucker 分解中的多个 tensor-times-matrix 操作。作者在并行模型下用 HBL 不等式把一次局部计算可覆盖的算术项、输入投影和输出投影联系起来，解析求解约束非线性优化问题；随后用具有两倍输入 tensor 模态数的逻辑处理器网格给出达到下界的算法。

**紧性范围。** 对 Multi-TTM 的并行数据移动量（在论文的 mild assumptions 下）上下界匹配；不是普通 (AB) 的新定理，也没有嵌套 memory hierarchy 的逐级通信向量结果。

**对我们的直接影响。** 证明模板说明“多投影 HBL + 解析优化”可以处理比三维 GEMM 更高维的计算 DAG。若要推广三层 overlay，应尝试将每一级的可访问投影写成同一组 HBL 约束，然后研究不同层 envelope 的兼容性；但论文的逻辑网格只证明一个并行层面的最优算法，不能自动给出层间复用。

### 3. Al Daas–Ballard–Grigori–Kumar–Rouse–Vérité，arXiv 2024；TOPC 2025

**论文：** [Communication Lower Bounds and Optimal Algorithms for Symmetric Matrix Computations](https://arxiv.org/abs/2409.11304)；期刊版本 DOI [10.1145/3727344](https://doi.org/10.1145/3727344)。

**模型与结果。** 研究 SYRK（(AA^T)）、SYR2K（(AB^T+BA^T)）与 SYMM（一个输入为对称矩阵的乘法），分别建立 sequential 和 distributed-memory parallel communication lower bounds。核心工具是针对对称计算的几何不等式及受约束非线性优化；算法通过 triangular block partitioning 避免重复访问对称项。

**紧性范围。** 论文声称在 sequential 与 distributed-memory 模型中均有 communication-optimal 算法；紧性针对这些对称 kernel 和其三角存储/访问结构，不等于普通 GEMM 的任意多层定理。

**对我们的直接影响。** 这说明“对称性会改变投影集合和常数”，不能把 GEMM 的 (abc) 体积约束机械套到 SYRK/SYMM。若未来把三层研究扩展到结构化 BLAS-3，必须先为每个 kernel 重新定义每一级的投影和兼容链；当前 GEMM 结果不自动转移。

### 4. Zhu–Hua–Jin，JCST 2025（JOMMA）

**论文：** [Joint-Communication Optimal Matrix Multiplication with Asymmetric Memories](https://www.sciopen.com/article/10.1007/s11390-023-3489-y)，DOI [10.1007/s11390-023-3489-y](https://doi.org/10.1007/s11390-023-3489-y)。

**模型与结果。** 分布式内存并行模型额外加入主存与 cache 之间的垂直通信；目标是 square GEMM 的 horizontal（处理器间）和 vertical（内存层级间）bandwidth 之和。读写对称内存（例如 DRAM）中，水平最优和垂直最优可以直接组合；在读写非对称内存（例如 NVM）中，两者一般不能同时各自最优，作者先给 joint lower bound，再给达到该 joint bound 的 JOMMA 算法，通过选择每个处理器的局部矩阵尺寸和 processor grid/schedule 实现匹配。

**紧性范围。** 这是目前与我们问题最接近的工作：它确实把一个并行层和一个 cache 层放进同一目标函数，并在其定义的 joint cost 下达到下界。但是模型是两级垂直通信、square GEMM、带特定读写权重的标量总成本；并未给出三层或任意 (L) 层的通信向量下界，也没有刻画所有层级成本的 Pareto frontier。

**可复用的公式。** 论文的 enough-memory 定理按 (2\omega/\beta) 分三段（(eta) 为水平 bandwidth 权重，(omega) 为写成本，(r/S^{1/2}) 为垂直读项的参数化系数）：

\[
Q=\Omega\!\left(\frac{n^2\beta}{P^{2/3}}+\frac{n^3r}{P S^{1/2}}\right),
\quad 2\omega/\beta\le1;
\]
\[
Q=\Omega\!\left(\frac{n^2\beta^{2/3}\omega^{1/3}}{P^{2/3}}+\frac{n^3r}{P S^{1/2}}\right),
\quad 1<2\omega/\beta<P^{1/2};
\]
\[
Q=\Omega\!\left(\frac{n^2\omega}{P}+\frac{n^3r}{P S^{1/2}}\right),
\quad 2\omega/\beta\ge P^{1/2}.
\]
有限内存版本还给出 (omega/\beta\le1)、(1<omega/\beta<n^2/M)、(omega/\beta\ge n^2/M) 三段，并由 JOMMA 达到相应 (Theta) 量级。这些公式可作为我们的三层模型退化到两层时的 sanity check。

**对我们的直接影响。** JOMMA 说明“把各级 bound 相加”在非对称内存中需要谨慎；更合理的目标可能是多维成本向量或带权 support function。我们的 (N/I) overlay 可被看作其 joint-cost 分析的三层离散化推广，但必须证明不同层级的 witness schedule 可兼容。

### 5. Nissim–Schwartz–Shabo，JSSPP 2024 / Springer 2025

**论文：** [Challenges in Parallel Matrix Chain Multiplication](https://doi.org/10.1007/978-3-031-74430-3_7)。

**模型与结果。** 对矩阵链的括号化和处理器分配联合优化，成本写成 (C=\alpha L+\beta BW+\gamma F)，并区分 memory-dependent 与 memory-independent communication。论文给出通信感知的动态规划与 resource-aware processor allocation，并证明在其矩阵链模型下的括号化最优性。

**紧性范围。** 这是算法/调度最优性结果，不是单个 GEMM 的新 lower-bound theorem；其通信函数依赖已有 classical/fast MM bounds，并且部分分析假设通信受限、内存不构成瓶颈。

**对我们的直接影响。** 它支持一个重要警告：当多个乘法阶段共享处理器和内存时，逐个调用单步最优 GEMM 未必全局最优。若我们研究多层或矩阵链，需要把“层级 envelope 兼容性”和“任务树/括号化”分开建模。

### 6. Isaev–Eswar–Vuduc，SPAA 2025

**论文：** [Brief Announcement: Optimality Conditions for Parallel Communication-Avoiding Matrix Multiplication with Overlapped Communication](https://doi.org/10.1145/3694906.3743357)。

**模型与结果。** 研究允许 computation/communication overlap 时，何种并行 communication-avoiding GEMM 能达到最优运行时间的条件；重点是把带宽、延迟与重叠纳入性能模型，而不是只数通信字节。

**紧性范围。** Brief announcement；主要是 overlap 下的 optimality conditions，不是替换 2022 memory-independent bandwidth lower bound 的新普适定理。若只以 word volume 为目标，其结论不能直接改变已有下界。

**对我们的直接影响。** 我们当前的三层 (N/I) 比率只比较 word traffic。若目标转向真实时间，需要为每一级增加 ((\alpha_\ell,\beta_\ell)) 和可重叠约束；最坏 ratio 可能由关键路径而非总字节决定。

### 7. Georganas–Heinecke–Dubey，arXiv 2026（v3: 2026-09-30）

**论文：** [Space Filling Curves is All You Need: Communication-Avoiding Matrix Multiplication Made Simple](https://arxiv.org/abs/2601.16294)。

**模型与结果。** 使用 generalized space-filling curves 划分 GEMM 计算空间，并通过复制实现 SFC-CA GEMM。论文在 private LRU cache + slow memory 的共享内存模型及 distributed-memory 实验中，声称对方阵和若干矩形 regime 达到已知 memory-dependent / memory-independent communication lower bounds 的渐近量级；理论部分明确列出不同形状和内存区间的条件。

**紧性范围。** 这是算法论文：其“provable asymptotic communication optimality”是相对于已知下界在若干 regime 的匹配，并未提出任意层级的新 lower-bound framework；模型主要是一层 fast cache 加 slow memory，分布式部分也不是任意 (L\)-level hierarchy。

**对我们的直接影响。** 它提供了可用的上界构造思路（空间填充曲线、复制、shape-oblivious schedule），可用来测试我们 lower-envelope 的可达性；但不能作为三层 nested (N) 的证明。特别要区分“某算法在每个 regime 达到已知 bound”和“所有层级同时达到各自 bound”。

### 8. Al Daas–Ballard–Grigori–Hussain–Kumar–Rahman–Rouse，arXiv 2026

**论文：** [Communication Lower Bounds and Algorithms for Sketching with Random Dense Matrices](https://arxiv.org/abs/2603.20966)。

**模型与结果。** 对 (B=A\Omega)（(Omega) 为 dense random matrix）以及 Nyström 中的 (\Omega^T A\Omega) 建立并行通信下界。作者提出新的几何投影不等式，把约束化为可解析求解的优化问题；对单次 (A\Omega) 在所有范围给出 communication-optimal algorithm，对两次乘法组成的 Nyström 过程给出接近下界的算法。

**紧性范围。** (A\Omega) 的随机矩阵结构允许处理器本地生成 (Omega) 的部分元素，因此其下界可能严格小于普通 dense (AB)；这不是 ordinary GEMM 的新紧下界，也没有解决嵌套层级。

**对我们的直接影响。** 该工作证明“operand 可生成/可复制”会改变投影约束，是我们研究复制策略时应考虑的反例来源。未来可把三层模型扩展为“哪些输入必须搬运、哪些可重生成”的 typed projection 问题。

### 9. Gupta–Korhonen–Studený–Suomela–Vahidi，arXiv 2024

**论文：** [Low-Bandwidth Matrix Multiplication: Faster Algorithms and More General Forms of Sparsity](https://arxiv.org/abs/2404.15559)。

**模型与结果。** 低带宽同步分布式模型：每轮每台计算机只能收发一个 (O(\log n))-bit 消息；研究稀疏矩阵乘法，改进均匀稀疏情形的轮数并覆盖 row/column/degeneracy/average/general sparsity。

**紧性范围。** 这是稀疏、低带宽 round-complexity 模型，不是 dense GEMM 的 word-I/O 或内存层级 lower bound；不能直接比较 2022 的 (P,M) bounds。

**对我们的直接影响。** 它提醒我们需明确“通信量（words）”“消息轮数（latency）”和“关键路径”三个目标；三层 overlay 当前只覆盖前者。

## 目前可以确认的研究空白

### 先区分一个较早的 multilevel 先例

Grigori–Jacquelin–Khabou 的 [HCP multilevel LU/QR 工作](https://doi.org/10.1007/978-3-319-07518-1_5)（ISC 2014；相关 HCP 预印本始于 2013）已经在一个特定的 Hierarchical Cluster Platform 模型中，为 LU/QR 的各层通信给出扩展下界并设计多层算法。更早的数值线性代数综述也指出，两层 bandwidth/latency bound 可以逐邻接层应用到 nested hierarchy。这里的关键区别是：这些结果针对特定 LU/QR 或把已有两层 bound 逐层套用，**没有给出我们正在寻找的 classical GEMM 任意 (L\ge3) 层、允许复制/重算/跨层复用的统一 per-level tight vector theorem**。因此“没有普适多层定理”不能理解为“历史上从未有过任何 multilevel bound”，而是指在当前更强模型下仍缺少统一紧性结论。

HCP 论文对其正则通信模式实际上给出了显式的层级形式：若第 (i) 层的处理器数为 (P_i^*)，总处理器数为 (P)，则 matrix-product-like 任务的第 (i) 层 bandwidth 满足

\[
W_i=\Omega\!\left(\frac{\#\mathrm{flops}}{\sqrt{M_i}}\right)
 =\Omega\!\left(n^2\sqrt{\frac{P_i^*}{P}}\right),
\qquad
S_i=\Omega(W_i/\phi_i),
\]

其中 (M_i) 是聚合内存、(phi_i) 是消息聚合容量。ML-CAQR 在该 HCP 模型中可在各层达到这些 bound（允许 polylog 因子）。这组公式可作为我们三层实验的历史 sanity check；但 HCP 假设通信沿固定层级聚合、每层所有下属处理元参与，未覆盖我们当前允许的 arbitrary replication/recomputation 和 nested-envelope compatibility。

### 已经解决或接近解决的范围

- 单层 distributed-memory classical rectangular GEMM 的 memory-independent lower bound，且 leading constants 紧（2022）。
- 单层/两层模型中若干结构化 kernel 的 HBL lower bound + matching algorithm（Multi-TTM、SYRK/SYR2K/SYMM）。
- 只有一个 cache 层、或把水平和垂直 bandwidth 聚合成一个标量成本时的若干最优算法（JOMMA、SFC-CA 的若干 regime）。

### 尚未看到普适解决的范围

1. 任意 (L\ge3) 级处理器/内存层级的 **向量化**通信下界：同时给出每一层必须搬多少 words/messages。
2. 允许复制、重算、跨层缓存驻留时，证明各层 lower bound 能否同时达到；或者给出不可同时达到的精确 Pareto frontier。
3. 非对称读/写成本和水平/垂直成本的多权重版本，而不只是 JOMMA 的两级标量和。
4. 将 HBL/投影不等式、processor-grid 选择和 nested schedule 统一成一个可解析优化问题。
5. 把 bandwidth、latency、overlap 和同步约束放进同一个多层模型。

## 对当前三层项目的建议

1. **保留 2022 定理作为外层基准。** 我们的 (I(z,y)) 与 (N(z,y)) 应明确标注：前者是把各层看成可独立使用的 lower-envelope 基线，后者是兼容 nested chain 的真实候选值；不能把 2022 的 tightness 直接宣称为三层 tightness。
2. **把 JOMMA 的 joint cost 当作两层 sanity check。** 先让三层模型退化为“一个并行层 + 一个 cache 层”，验证是否能重现其“对称成本可组合、非对称成本出现 trade-off”的定性结论。
3. **从向量而不是单一 ratio 开始。** 先计算可达集合 ((Q_1,Q_2,Q_3)) 或其下凸包，再对不同权重取 support function；这样可以区分“某个权重下最优”与“逐层同时最优”。
4. **为复制/重算显式加类型。** 参考随机 sketching 的可本地生成 operand：输入若可重生成，不能把它当成普通必须搬运的 projection；这可能产生真正的三层反例。
5. **把 overlap 单独作为后续模型。** 先完成 word-volume theorem，再加入每级 (alpha_\ell,\beta_\ell) 和 overlap；否则当前 envelope 的比率容易混淆 bandwidth 与时间最优。

## 文献判断的可信边界

上述“截至 2026-10-03 未检索到任意 (L\ge3) 普适紧定理”是基于 arXiv、ACM/SIAM/Springer 论文页和作者公开版本的定向检索结论，不是形式化的穷尽证明。最接近的两项是 JOMMA（两级 horizontal+vertical joint cost）和 2026 SFC-CA GEMM（在若干区间匹配已有 lower bounds）；二者都不能替代我们要证明的三层 nested theorem。

## 来源核验状态

- **正式发表且摘要/元数据可在出版社页面核验：** Multi-TTM（SIAM JMAA 2024）、Symmetric kernels（TOPC 2025，arXiv 版本也公开）、JOMMA（JCST 2025）、matrix-chain chapter（Springer 2024 online / 2025 copyright）。
- **正式会议论文但公开内容有限：** SPAA 2025 overlap brief announcement；目前核验了 DOI、DBLP 条目和会议目录，未把摘要之外的细节当作定理使用。
- **公开预印本，尚未当作期刊定稿：** SFC-CA GEMM（arXiv:2601.16294，v3 于 2026-09-30 修订）、random dense sketching（arXiv:2603.20966，2026-03-21 v1）、low-bandwidth sparse MM（arXiv:2404.15559）。报告中对这些工作的“optimal”措辞仅按其预印本摘要/正文声明转述。
- **未纳入核心结论的邻近方向：** secure/distributed coded MM、稀疏图乘法、硬件 dataflow lower bound 等。它们改变了安全、稀疏性或硬件模型，不能直接回答 dense classical GEMM 的 nested-I/O 问题。

## 可直接写入主日志的短结论

> **Literature checkpoint (2026-10-03).** Post-2022 work tightens communication bounds for structured kernels (Multi-TTM; SYRK/SYR2K/SYMM) and for a two-level joint horizontal/vertical cost with asymmetric memories (JOMMA). 2026 SFC-CA GEMM gives a shape-oblivious algorithm matching known one-level bounds in several regimes, while 2026 random-sketching work extends HBL lower bounds to generated operands. No cited work gives a universal tight per-level communication vector for arbitrary (L\ge3) nested GEMM with replication/recomputation. Our three-level exact overlay therefore remains a genuine open gap rather than a rediscovery of an existing theorem.
