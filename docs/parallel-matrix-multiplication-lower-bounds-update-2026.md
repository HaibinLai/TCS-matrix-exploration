# 并行矩阵乘法通信紧下界：2022–2026 进展核查

> 检索截止：2026-10-02。这里的“紧下界”指 parallel/distributed-memory data movement 的 lower bound，并且存在达到同阶或同常数的算法；不把单纯的 kernel 优化、性能论文或代数通信复杂度自动算作机器通信下界。

## 核心判断

截至 2026 年 10 月 2 日，在 **word-volume / distributed-memory** 模型中能确认的最新一般性 dense rectangular matrix multiplication 结果仍然是 Al Daas–Ballard–Grigori–Kumar–Rouse 的 2022 工作：它给出了 **memory-independent、带 tight constants、按矩阵长宽比分类** 的并行通信下界。2026 年出现了 low-bandwidth round-complexity 模型下的矩形 MM 新结果，但它计数的是每轮每机 (O(\log n))-bit 消息，不应与 word-volume theorem 混为一谈。2023–2025 的主要推进不是替换 2022 年的一般 GEMM 定理，而是：

1. 将 memory-independent/HBL/几何不等式框架扩展到对称矩阵核和多张量运算；
2. 对特殊结构利用对称性减少常数，并给出通信最优算法；
3. 继续解决“下界可达性”、任意处理器数、内存/复制 trade-off 和实际数据布局问题；
4. 将“理论 lower bound”映射到 GPU/tensor accelerator 的 dataflow，但这类工作通常不是新的分布式通信定理。

## 时间线

### 2022：普通 dense parallel MM 的 memory-independent tight constants

**Al Daas, Ballard, Grigori, Kumar, Rouse, “Tight Memory-Independent Parallel Matrix Multiplication Communication Lower Bounds,” SPAA 2022 / arXiv:2205.13407.**

主要结果：

- 对并行矩阵乘法给出不依赖本地内存大小的通信下界；
- 常数按三个矩阵的 aspect ratios 与处理器数的相对关系分区；
- 改进此前只有渐近阶、或常数不紧的结果；
- “memory-independent”表示即使本地内存无限大，该通信仍不可避免；有限内存时这些下界在很多区域仍是最紧的可用结果。

方法上，它把通信下界转化为约束优化问题，求出三类几何投影/通信情形的最优常数。研究时应把它与早期的 2D/2.5D 公式分开：后者往往预设数据布局或内存范围，而 2022 结果强调 aspect-ratio-aware 和 memory-independent。

来源：[arXiv 2205.13407](https://arxiv.org/abs/2205.13407)，[作者发表列表中的摘要与 BibTeX](https://users.wfu.edu/ballard/publications.html)。

### 2023：SYRK 的并行 memory-independent 紧下界

**Al Daas, Ballard, Grigori, Kumar, Rouse, “Parallel Memory-Independent Communication Bounds for SYRK,” SPAA 2023.**

SYRK 计算 \(C\leftarrow AA^T+C\)，输出具有对称性，因此只需计算三角区域。论文的推进是：

- 为对称计算扩展关键几何不等式；
- 得到比一般 GEMM 更小的、带 tight constants 的 parallel communication lower bound；
- 使用 triangular block partition，构造达到下界的 1D/2D/3D 风格算法。

这不是新的任意 GEMM 下界，而是说明“矩阵结构可以把一般 GEMM 常数真正降下来”，并且这种降幅可以在并行实现中达到。

来源：[SPAA 2023 记录](https://doi.org/10.1145/3558481.3591072)，[STFC 摘要](https://epubs.stfc.ac.uk/work/56530728)。

### 2023：Multi-TTM 的 parallel communication lower bounds

**Al Daas, Ballard, Grigori, Kumar, Rouse, “Communication Lower Bounds and Optimal Algorithms for Multiple Tensor-Times-Matrix Computation,” 2023 online / SIAM J. Matrix Anal. Appl. 2024.**

Multi-TTM 是 Tucker 分解中的多张量乘矩阵运算。论文：

- 对 parallel Multi-TTM 给出 communication lower bounds；
- 用 HBL inequalities 和受约束非线性优化求 bound；
- 构造逻辑处理器网格，证明算法达到下界；
- 表明把 Multi-TTM 机械拆成多个 TTM 可能产生额外通信。

它的重要意义是方法论：HBL/几何优化不只适用于单个 GEMM，而能处理多个耦合张量算子。但它属于 tensor algebra 的推广，不是 dense GEMM 主定理的更新。

来源：[SIAM 2024 文章页](https://epubs.siam.org/doi/10.1137/22M1510443)。

### 2024 预印本、2025 期刊：SYRK、SYR2K、SYMM 的统一对称矩阵结果

**Al Daas, Ballard, Grigori, Kumar, Rouse, Vérité, “Communication Lower Bounds and Optimal Algorithms for Symmetric Matrix Computations,” arXiv 2024；ACM TOPC 2025, 12(2).**

论文统一研究：

- SYRK：\(AA^T\)；
- SYR2K：\(AB^T+BA^T\)；
- SYMM：一个输入矩阵具有对称性时的矩阵乘法。

对 sequential 和 distributed-memory parallel 两类模型都给出 lower bounds，并给出通信最优算法。证明继续依赖对称版本的几何不等式和约束优化；算法采用 triangular blocking/partitioning。

该工作是截至 2025 年最接近“并行矩阵乘法紧下界体系继续扩展”的主线成果，但对象是 BLAS-3 对称核，不是无结构的 GEMM。

来源：[arXiv 2409.11304](https://arxiv.org/abs/2409.11304)，[ACM TOPC 2025 元数据](https://doi.org/10.1145/3727344)，[STFC 记录](https://epubs.stfc.ac.uk/work/62135956)。

### 2023–2025：相关但不能混称为 GEMM 总下界的工作

- **Zhu, Hua, Jin, “Joint-Communication Optimal Matrix Multiplication with Asymmetric Memories,” JCST 2025**：把处理器间 horizontal bandwidth 与主存/cache 间 vertical bandwidth 放进同一个目标。在对称读写内存中，两类最优性可以组合；在 NVM 等 asymmetric-memory 模型中存在 trade-off，并给出 joint lower bound 与匹配的 JOMMA 算法。它是多级/异构内存方向的重要近作，但模型是特定的联合成本，不等价于任意 \(L\)-level HCP 的逐层 tight theorem。来源：[期刊页面](https://doi.org/10.1007/s11390-023-3489-y)。
- **Schwartz–Vaknin, “Pebbling Game and Alternative Basis for High Performance Matrix Multiplication,” SIAM J. Sci. Comput.**：在已有 classical/fast MM 通信下界框架下，研究替代基和实现成本；文中明确使用 classical 与 fast MM 的 parallel lower-bound 公式，并讨论 Strassen 实现的可达性。它更像算法/表示改进，而非新的任意 parallel GEMM lower-bound 定理。来源：[SIAM 文章](https://epubs.siam.org/doi/full/10.1137/22M1502719)。
- **“Matrix Multiplication and Number on the Forehead Communication,” CCC 2023**：研究矩阵乘法张量与多方通信复杂度的联系，属于代数/通信复杂度理论；不能直接当作机器内存或处理器间 data-movement lower bound。来源：[Dagstuhl 论文](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.CCC.2023.16)。
- **2025 DAC 的 tensor accelerator dataflow 工作**：提出为算子融合和 tiling 计算 memory-communication lower bound 的设计原则，并在加速器上报告节省；它是架构/映射层面的 bound 和优化，不是对任意并行 MM 算法的 universal distributed-memory theorem。来源：[IEEE Xplore](https://ieeexplore.ieee.org/document/11132765/)。
- **2025–2026 GPU communication-avoiding GEMM 工作**：有价值地验证了 HBM、片上 buffer、fusion 和 dataflow 的工程影响，但需要逐篇检查其“lower bound”是否是模型内最优、某个 kernel 的可达下界，还是经验上的 traffic baseline。
- **Ju, Zhang, Solomonik, “Communication Lower Bounds for Nested Bilinear Algorithms via Rank Expansion of Kronecker Products,” FoCM 2025**：针对 nested Toom–Cook、Strassen 和部分对称 tensor contraction，利用 rank expansion 与 Kronecker-product 结构给出 memory-hierarchy/processor communication lower bounds。它主要推进 fast/nested bilinear algorithms 的 no-recomputation 分支，不替代 2022 年 classical rectangular GEMM 的 memory-independent theorem。来源：[DOI 10.1007/s10208-023-09633-8](https://doi.org/10.1007/s10208-023-09633-8)，[Illinois Experts 记录](https://experts.illinois.edu/en/publications/communication-lower-bounds-for-nested-bilinear-algorithms-via-ran)。
- **Vitter–Shriver, “Algorithms for Parallel Memory, II: Hierarchical Multilevel Memories,” Algorithmica 1994**：在 P-HMM/P-BT 并行层级内存模型中，对标准 square matrix multiplication 给出 matching multilevel access bounds。它说明“多级内存从未被分析”是不准确的；但该模型把层级访问折叠进 access-cost function，并忽略 hierarchy 间 network communication，因此不等于现代 rectangular GEMM 的 nested processor-grid theorem。来源：[论文 PDF](https://ittc.ku.edu/~jsv/Papers/ViS94.sorting_hierarchical.pdf)。
- **Gupta, Suomela, Vahidi, “Rectangular Matrix Multiplication in the Low-Bandwidth Model,” arXiv:2606.04652 (2026)**：在 $n$ 台机器、每轮每机只能收发一个 $O(\log n)$-bit 消息的模型中，研究 $\langle n,d,n\rangle$ 与 $\langle d,n,d\rangle$ 两类矩形 MM；给出 upper bounds、unconditional lower bounds 和 conditional lower bounds，并在 $\langle n,d,n\rangle$ 中出现 $d\approx\sqrt n$ 的 phase transition。它是 2026 年很直接的矩形并行下界进展，但目标是 rounds/bit bandwidth，而不是 2022 定理的 critical-path words。来源：[arXiv HTML](https://arxiv.org/abs/2606.04652)。
- **Gupta, Korhonen, Studený, Suomela, Vahidi, “Low-Bandwidth Matrix Multiplication: Faster Algorithms and More General Forms of Sparsity,” SIROCCO 2025**：在同一每轮 $O(\log n)$ bit 的 distributed model 中，把已知 sparse square-MM 算法推广到 row/column/average-sparse 等结构，并将 uniformly sparse 的算法轮数降到 $O(d^{1.832})$。这是 low-bandwidth 算法与稀疏性扩展，不是无稀疏 dense GEMM 的 universal tight lower bound。来源：[arXiv 2404.15559](https://arxiv.org/abs/2404.15559)，[作者版](https://jukkasuomela.fi/matrix-mul-more/)。
- **Al Daas, Ballard, Grigori, Kumar, Rouse, Vérité, “Minimizing Communication for Parallel Symmetric Tensor Times Same Vector Computation,” 2025**：对三阶对称张量沿两个 mode 乘同一向量给出 parallel communication lower bound 和 matching algorithm，把矩阵三角分块推广到三阶对称张量。它延续 symmetric-kernel 主线，但对象已不是矩形 GEMM。来源：[arXiv 2506.15488](https://arxiv.org/abs/2506.15488)。
- **Distributed Batch Matrix Multiplication: Tradeoffs in Download Rate, Randomness, and Privacy, IEEE TIT 2026**：研究 coded/private batch MM 的 download-rate trade-off，并给出 converse/achievability。它是信息论与隐私模型，通信单位不是处理器间 words、messages 或 memory-hierarchy traffic，因此只作为相邻模型记录。来源：[IEEE Xplore](https://doi.org/10.1109/TIT.2026.3710646)。

## 目前的理论版图

| 问题对象 | 最新可确认的紧下界状态 |
|---|---|
| 无结构 classical dense GEMM，parallel，矩形 | 2022 memory-independent tight constants；后续未发现替代性更一般主定理 |
| classical GEMM，给定本地内存的 bandwidth/latency trade-off | 早期 Irony–Toledo–Tiskin、Ballard 等和 2D/2.5D/3D 结果；需按内存区间与复制模型引用 |
| 矩形 MM，low-bandwidth rounds | 2026 arXiv 结果给出特定 $\langle n,d,n\rangle$、$\langle d,n,d\rangle$ 的 upper/unconditional/conditional bounds；不等同于 word-volume 下界 |
| 稀疏 MM，low-bandwidth rounds | 2025 SIROCCO 工作改进 sparse 算法并扩展稀疏定义；没有替代 dense GEMM 的 universal tight theorem |
| 对称三阶张量 times same vector | 2025 arXiv 给出 parallel tight lower bound 与 matching algorithm；属于 symmetric tensor extension |
| coded/private batch MM | 2026 IEEE TIT 研究 download-rate/privacy converse；不属于机器 data-movement 下界 |
| Strassen/fast MM 的 parallel communication | 2012 communication-optimal Strassen 及扩张方法；2022 后主要是实现、表示和特殊算法类扩展 |
| SYRK | 2023 parallel memory-independent tight bounds |
| SYR2K、SYMM | 2024 预印本，2025 ACM TOPC 期刊版，sequential + distributed-memory tight bounds |
| Multi-TTM | 2024 SIAM 期刊版，HBL-based parallel lower bounds and optimal algorithms |
| 多级 GPU/HBM/L2/shared/register 同时 tight | 1994 P-HMM/P-BT 已有抽象 multilevel square-MM 结果；现代 rectangular GEMM、网络通信与 nested-grid 约束下仍未找到统一 theorem |
| 任意网络拓扑、异构链路、带 latency/energy 的联合 tight bound | 仍是开放方向；2025 asymmetric-memory 工作只覆盖特定 joint objective |

## 对“这些年进展”的准确概括

1. **一般 GEMM 的突破点在 2022，而不是 2024/2025。** 2022 结果把矩形、memory-independent 和 tight constants 做得更完整。
2. **2023–2025 的主要增量是结构化算子。** 对称性、张量模式和三角分块被纳入同一几何/HBL 思路；这带来真正更小的常数和 matching algorithms。
3. **下界证明和算法构造越来越绑定。** 新论文不只给 bound，还设计 triangular/grid/block distribution 来达到它；“证明 tight”需要上下界同时出现。
4. **多级硬件仍有明显缺口。** 现有 parallel lower bounds 通常抽象为 processor-local memory + network；GPU 上的 HBM/L2/shared/register、tensor-core fragment、fusion 和异步传输尚未被统一到同一个一般 lower-bound 模型。
5. **需要谨慎区分三种 communication。** machine data movement、代数多方通信复杂度、以及 accelerator dataflow traffic 都会用“communication”一词，但数学对象和可比结论不同。

## 最值得继续追的研究问题

### 1. 从 2022 一般 GEMM 到多级内存

给定 \(P\)、每处理器内存 \(M\) 以及 GPU 的多级容量 \((M_1,M_2,M_3)\)，能否证明一个对所有 schedule 都成立、并且在每一级都可由同一算法近似达到的 bound？

### 2. 任意处理器数与实际数据布局

许多 matching algorithms 在处理器网格、维度整除或特定 replication factor 下最干净。对任意 \(P\)、任意矩形尺寸和不整除分块，能否保持 tight constant，而不是只得到渐近阶？

### 3. 带 latency、同步和能耗的联合下界

现有结果通常先优化 words，再单独分析 messages。对现代互连，是否存在同时 tight 的

\[
(\text{words},\ \text{messages},\ \text{synchronizations},\ \text{energy})
\]

Pareto lower bound？

### 4. 融合和近似计算

当 GEMM 与 bias、activation、reduction 或量化融合时，哪些移动真的可以从理论下界中删除？对允许误差、随机化或低精度的 MM，通信下界如何依赖误差参数？

### 5. 从理论 bound 到真实 kernel

对 COSMA、SUMMA、2.5D/3D、CUTLASS/cuBLAS 等实现，分别测量：

- 处理器间 words/messages；
- HBM↔L2、L2↔shared、shared↔register traffic；
- packing、边界 tile 和临时缓冲；
- 实际 traffic 与对应理论 bound 的常数比。

这样才能判断一个“理论 gap”究竟来自证明、算法，还是硬件计数口径。

## 建议的阅读顺序

1. 2022：普通矩形 GEMM 的 memory-independent tight constants；
2. 2023：SYRK 的对称几何不等式与 triangular blocking；
3. 2024：Multi-TTM 的 HBL/约束优化；
4. 2024/2025：SYR2K/SYMM 的统一结果；
5. Schwartz–Vaknin：pebbling、替代基与 fast-MM 实现；
6. GPU/accelerator 工作：只在先固定 machine model 后比较 traffic。

## 结论

目前最可靠的研究判断是：**并行普通矩阵乘法的“主下界”在 2022 年已达到一个重要的 memory-independent tight-constant 里程碑；2023–2025 的新进展主要沿结构化矩阵和张量算子扩展，而“一般 GEMM 在多级异构内存、任意网络、联合 bandwidth/latency/energy 模型下的 tight lower bound”仍然是很有空间的方向。**
