# 一般嵌套分区定理与矩形化反例

静态三层定理不必从矩形 processor grid 开始。可以直接对产品集合的任意嵌套 owner partitions 证明逐边下界；矩形 grid 只是这个定理的一个特例。

## 嵌套分区

令
\[
T=[m]\times[k]\times[n]
\]
是 scalar-product 集合。令
\[
\Pi_1\preceq\Pi_2\preceq\Pi_3\preceq\Pi_4,
\qquad \Pi_4=\{T\},
\]
其中 $\Pi_1$ 是最细计算层，$\Pi_3$ 是最粗处理器层；$\Pi_\ell\preceq\Pi_{\ell+1}$ 表示每个细 part 完全包含在一个粗 part 中。

对分区定义投影和：
\[
X_A(\Pi)=\sum_{S\in\Pi}|\pi_A(S)|,
\quad
X_B(\Pi)=\sum_{S\in\Pi}|\pi_B(S)|,
\quad
X_C(\Pi)=\sum_{S\in\Pi}|\pi_C(S)|.
\]
若粗 part 中每个投影 incidence 已有一个 copy，则第 $\ell$ 条边的新增 incidence 为
\[
\Delta_\ell^A=X_A(\Pi_\ell)-X_A(\Pi_{\ell+1}),
\]
\[
\Delta_\ell^B=X_B(\Pi_\ell)-X_B(\Pi_{\ell+1}),
\qquad
\Delta_\ell^C=X_C(\Pi_\ell)-X_C(\Pi_{\ell+1}).
\]
这些量非负，因为细分区只会增加投影 incidence。

## 一般 nested-partition theorem

在一次产品计算、单份初始输入、单份最终输出和 owner-consistent nested partitions 的模型中，边 $E_\ell$ 满足
\[
V_\ell^A\ge\Delta_\ell^A,
\qquad
V_\ell^B\ge\Delta_\ell^B,
\qquad
V_\ell^C\ge\Delta_\ell^C.
\tag{NP-vector}
\]

证明是逐个 incidence 计数。若某个 A-entry 在粗分区出现 $d_c$ 个 owner parts，在细分区出现 $d_f$ 个 owner parts，那么已有 copies 只能覆盖 $d_c$ 个 incidence，至少需要 $d_f-d_c$ 个新 copy。对所有 A-entries 求和就是 $\Delta_\ell^A$。B 相同。C 的 $d_f$ 个 partial aggregates 需要归并到 $d_c$ 个粗 owner parts，至少需要 $d_f-d_c$ 次 movement。

因此对任意非负边和数据类型成本，
\[
Q_w\ge
\sum_{\ell=1}^{3}
\left(
\alpha_{\ell,A}\Delta_\ell^A+
\alpha_{\ell,B}\Delta_\ell^B+
\beta_{\ell,C}\Delta_\ell^C
\right).
\tag{NP-weighted}
\]
在允许每个粗 owner group 与其细 child groups 进行树形 broadcast/reduction 的拓扑中，可以逐类达到这些 incidence counts。因此这是 arbitrary nested partition 的静态 tight theorem。

## 矩形 grid 是特例

若每个 $\Pi_\ell$ 来自 componentwise-coarsened $a_\ell\times b_\ell\times c_\ell$ block grid，则
\[
\Delta_\ell^A=(c_\ell-c_{\ell+1})mk,
\]
\[
\Delta_\ell^B=(a_\ell-a_{\ell+1})kn,
\]
\[
\Delta_\ell^C=(b_\ell-b_{\ell+1})mn,
\]
恰好恢复 `t3-static-hierarchical-theorem.md` 的三层定理。

## 重要反例：非对称层成本下不能矩形化

在 $2\times2\times2$ 产品集合上取三层 owner 数
\[
(P_1,P_2,P_3)=(8,4,2)
\]
以及边权
\[
(w_1,w_2,w_3)=(1,2,1).
\]

取 $\Pi_1$ 为 8 个 singleton，$\Pi_2$ 为固定 $(i,k)$ 后包含两个 $j$ 的 4 个 parts，$\Pi_3$ 为两个 diagonal parts：
\[
\{(0,0,j),(1,1,j):j=0,1\},
\]
\[
\{(0,1,j),(1,0,j):j=0,1\}.
\]
对应的三条增量分别是
\[
(\Delta_1,\Delta_2,\Delta_3)=(4,0,8),
\]
所以加权成本为
\[
1\cdot4+2\cdot0+1\cdot8=12.
\]

穷举全部 315 条嵌套分区链后，任意分区最优值确实为 12；但所有矩形 grid chain 的最优增量是
\[
(4,4,4),
\]
加权成本为
\[
1\cdot4+2\cdot4+1\cdot4=16.
\]
因此：

> 矩形化在非对称层成本下是假的，即使在最小的 $2\times2\times2$ 实例上也失败。

这不是算法失败，而是模型层面的反例。后续 asymmetric-cost 理论必须使用一般 nested-partition envelope；不能只枚举矩形 factor chains。

## 研究含义

- 无权 aggregate volume 会沿层次 telescopes，最终只依赖最细 partition 的 projection boundary；
- 带权或按层归一化的通信成本保留中间 partition 的作用；
- 25-line factor arrangement 只能作为矩形 grid 的特殊几何平台；
- 真正可推广的对象是 nested-partition envelope，矩形 grid 是可实现的受限子类。

`experiments/check_nested_partition_weighted_counterexample.py` 给出上述穷举和反例检查。
