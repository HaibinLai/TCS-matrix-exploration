# 还能从哪里突破：2026-10 研究判断

当前项目已经有静态三层 nested-incidence theorem、matching tree schedule、
任意 L 层/矩形/非对称成本推广，以及受限 SYRK/SYMM 和 finite-capacity
row-split tight 子定理。真正未解决的部分不是再增加 factor-chain 参数，而是把
finite-capacity trace 变成可证明的对象。

## 最值得投入的方向：overlap correction

现有 exact (2\times2\times2) 单 owner 结果显示，(M=3) 时实际
read/partial traffic 是 12，而单独的 cut 和 phase 项的最大值只有 8。直接
相加又会重复计算首次加载。因此需要寻找一个 overlap correction：

\[
Q\ge Q_{\rm cut}+Q_{\rm phase}-\Gamma(M,\text{trace}),
\]

或者直接构造一个只按一次事件计费的 typed phase/cut dual。

推荐的技术路线是：

1. 不枚举完整 resident masks，而按每个 phase 的
   \((|\pi_A(F)|,|\pi_B(F)|,|\pi_C(F)|)\) 和 shared-cache lineage 分类；
2. 对每类 phase 写出 HBL 约束、首次到达约束和 C-store/reload 约束；
3. 将剩余问题写成小型整数流或线性规划，观察其 dual 变量是否稳定；
4. 对 (2^3)、(3^3) 得到同一组 dual certificate 后，再尝试归纳到一般
   (m,k,n,M)。

这是最可能产生“新定理”的路线，因为它直接连接现有的静态 cut 定理和
有限容量 phase 定理。

## 第二方向：证明动态版本的可分解条件

当前 Steiner 定理已经允许固定 hierarchy tree 上的 arbitrary leaf demands，
但容量和 phase 仍未接入。可以先找一个充分条件：如果每个 data entry 的
copy lineage 在每条 edge 上是 laminar 的，且每个 phase 的 output partial
只向一个 ancestor 方向移动，那么 trace 可以按 edge 分解。若条件成立，可以
得到

\[
Q\ge\sum_e \mathcal E_e(M_e)
\]

并给出逐边 schedule；若条件不成立，最小反例本身就是动态 owner 破坏单一
nested chain 的证据。

这个方向比直接处理任意动态执行小很多，也能回答“什么时候静态 theorem 可以
升级成多级 theorem”。

## 第三方向：把 weighted nested partition 变成组合优化问题

非对称 edge cost 下，(2\times2\times2) 已经证明最优 partition 不一定是
矩形 grid。下一步可以研究 projection-incidence objective 的结构：它可能
对应一个带类型权重的 laminar partition / multiway-cut 问题。

可突破的结果有两种：

- 证明某个受限权重族下矩形 chain 仍然最优；
- 或证明一般 weighted nested optimization 已经包含一个已知困难问题，从而
  给出“为何不应期待统一闭式公式”的复杂度边界。

这条线偏组合优化，适合作为主定理的边界结果，不应替代 finite-capacity 主线。

## 第四方向：recomputation 的复杂度边界

允许 recomputation 后，变量是 compute-event multiset
\(\mathcal F(u)\)，而不是固定 owner partition。一个可行目标是证明：
固定 event assignment 时 Steiner forest 是 tight；优化 event assignment 在带
weighted edge 和容量约束时至少包含 Steiner forest、set cover 或 facility
location 的特例。

如果能给出一个正式的 NP-hardness/restricted polynomial-time boundary，就能把
“没有闭式 theorem”转化成一个有价值的理论结果，再集中研究 row-split、固定
reduction tree 等可解子类。

## 第五方向：结构化 kernel 的多级 phase

SYRK/SYMM 的静态 union/unordered-pair projection 已经可以写出 incidence
bound；2024 年已有单层 symmetric HBL 和 matching algorithms。因此真正可能
超出的地方是：

- symmetric projection 与多级 edge cost 的联合；
- triangle partition 的跨层 retained-copy difference；
- symmetric phase 与 C partial reduction 的 overlap correction。

这条线应在 GEMM overlap correction 出现规律后再推进，避免同时引入两个新难点。

## 当前不值得继续投入的方向

- 继续扩大 (r)、(q) 的 arrangement sweep；
- 继续收集没有新计费模型的 GPU kernel 性能数字；
- 把 row-split 或 (M\ge K+2) 的 tight 子定理包装成一般三层 theorem；
- 把 cut、phase、I/O 三个标量未经 overlap proof 直接相加。

## 决策门槛

下一阶段用一个小型 exact/LP 实验回答三个问题：

1. overlap correction 是否只依赖 phase projection 类型，而不依赖完整 cache mask；
2. shared-cache lineage 是否能用一个低维状态表示；
3. 是否存在达到该 dual bound 的 schedule。

若三个问题都得到肯定，就继续证明有限容量 restricted three-level theorem；若
第二或第三个答案是否定，就把结果明确定位为 trace-envelope/hardness theorem，
而不是继续寻找不存在的统一闭式公式。

## 新的 exact 证据

受限的 shared-B/C trace 已经给出一个可复现的有限容量结果：在
(2\times2\times2) row-split GEMM 中，每个 B-entry 只通过 shared cache 到达
一次、禁止 direct B load 时，0/1 shortest-path enumeration 对所有 24 个 arrival
permutations 给出

$$
Q_{M=3}=14,\qquad Q_{M=4}=12.
$$

其中 12 是四个 A arrivals、四个 shared-B arrivals 和四个最终 C writes 的
静态 baseline；(M=3) 的额外两次 traffic 来自 C accumulator 的 store/reload。
这个结果已写入 `docs/finite-capacity-restricted-shared-c-trace.md`。它把
“overlap correction”从抽象问题变成了一个具体的两-word penalty，但 direct-B
和 repeated-shared-B 仍可能改变 unrestricted optimum，因此下一步是证明它们
不能把 14 降到 13，或构造一个 13 的反例。
