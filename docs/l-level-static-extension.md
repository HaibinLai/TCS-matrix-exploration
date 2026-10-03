# 从三层到 L 层：静态增量通信定理

三层逐边定理的结构可以直接推广到任意固定层数 (L)。这里仍然是 classical GEMM、一次产品计算、静态 owner-consistent grids 和计费 replication/reduction；动态 owner、免费初始复制和 recomputation 另行处理。

## L 层模型

令第 (1) 层是最细的计算层，第 (L) 层是最粗的处理器层，并定义源层
\[
g_{L+1}=(1,1,1).
\]
每层使用
\[
g_\ell=(a_\ell,b_\ell,c_\ell),
\qquad a_\ell b_\ell c_\ell=P_\ell,
\]
且
\[
g_{\ell+1}\preceq g_\ell
\quad(1\le \ell\le L).
\]

令 (V_\ell^A,V_\ell^B,V_\ell^C) 分别是第 \(\ell\) 条边上 A 复制、B 复制和 C 归约的 aggregate word volume。与三层证明完全相同，得到逐边向量下界
\[
V_\ell^A\ge(c_\ell-c_{\ell+1})mk,
\]
\[
V_\ell^B\ge(a_\ell-a_{\ell+1})kn,
\]
\[
V_\ell^C\ge(b_\ell-b_{\ell+1})mn.
\]

因此
\[
V_\ell\ge
(c_\ell-c_{\ell+1})mk+
(a_\ell-a_{\ell+1})kn+
(b_\ell-b_{\ell+1})mn.
\tag{L-vector}
\]

证明仍然是逐个矩阵元素计数：每个粗层 A-copy 扩展到 (c_\ell/c_{\ell+1}) 个子组，每个 B-copy 扩展到 (a_\ell/a_{\ell+1}) 个子组，而 C 的 partial 数从 (b_\ell) 归并到 (b_{\ell+1})。

## 非对称 read/write 成本

令每条边对三类 movement 使用非负成本
\[
\alpha_{\ell,A},\quad
\alpha_{\ell,B},\quad
\beta_{\ell,C}.
\]
它们可以分别表示 A/B 输入复制和 C 输出归约的 read/write 或链路成本；不把不同成本强行压成一个 bandwidth 参数。

定义
\[
Q_{\rm asym}=
\sum_{\ell=1}^{L}
\left(
\alpha_{\ell,A}V_\ell^A+
\alpha_{\ell,B}V_\ell^B+
\beta_{\ell,C}V_\ell^C
\right).
\]
则
\[
Q_{\rm asym}\ge
\min_{g_L\preceq\cdots\preceq g_1}
\sum_{\ell=1}^{L}
\left[
\alpha_{\ell,A}(c_\ell-c_{\ell+1})mk
+\alpha_{\ell,B}(a_\ell-a_{\ell+1})kn
+\beta_{\ell,C}(b_\ell-b_{\ell+1})mn
\right].
\tag{L-asym}
\]

允许树形 broadcast/reduction 时，逐类 schedule 使用恰好对应数量的 word movement，因此 (L-asym) 在这个静态模型中 tight。非均匀成本的作用是改变最优 chain；它不会改变单边计数证明。

## 一层和无权特例

当 (L=1) 时，源层是 ((1,1,1))，恢复
\[
V\ge(c-1)mk+(a-1)kn+(b-1)mn.
\]
当所有 edge weights 相同，aggregate volume 沿层次 telescopes：
\[
\sum_{\ell=1}^{L}V_\ell
\ge(c_1-1)mk+(a_1-1)kn+(b_1-1)mn.
\]
但加权或按层归一化的成本一般不 telescopes，因此嵌套 chain 仍然是一个真正的优化变量。

## 已知范围和下一步

这个 L-level 结论证明的是静态嵌套 ownership 的向量/加权下界，矩形 (m\times k) 乘 (k\times n) 已包含在内。它尚未处理：

- arbitrary dynamic owner partitions；
- free initial replication；
- recomputation；
- 有限 local memory 的 phase/HBL 项与 ownership 项的联合 tightness；
- SYRK、SYMM 等共享输入/对称输出结构。

因此它是三层定理的自然扩展，也是后续动态定理的基准模型，而不是对所有多级 GEMM 实现的最终声明。

`experiments/check_l_level_static_theorem.py` 检查一层 SG-1、四层 chain、无权 telescoping 和非对称边成本下的 L-level envelope。
