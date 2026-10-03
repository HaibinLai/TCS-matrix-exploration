# T3-volume 的证明骨架与缺口

这份文件把三层 nested communication lower bound 拆成可以分别验证的命题。它不把当前的 $N(z,y)$ 直接当成已经证明的下界。

## 已证明目标：静态 nested-partition theorem

对 classical GEMM 的产品集合 (T=[m]	imes[k]	imes[n])，令
(Pi_1preceqPi_2preceqPi_3preceqPi_4={T}) 是 owner-consistent nested partitions。定义
[
X_A(Pi)=sum_{SinPi}|pi_A(S)|,
\quad X_B(Pi)=sum_{SinPi}|pi_B(S)|,
\quad X_C(Pi)=sum_{SinPi}|pi_C(S)|.
]
在一次产品计算、单份初始输入、单份最终输出的模型中，第 (ell) 条边满足
[
V_ell^Age X_A(Pi_ell)-X_A(Pi_{ell+1}),
]
[
V_ell^Bge X_B(Pi_ell)-X_B(Pi_{ell+1}),
\quad
V_ell^Cge X_C(Pi_ell)-X_C(Pi_{ell+1}).
]
树形 broadcast/reduction 在相同拓扑模型下达到这些计数。完整陈述见 `docs/nested-partition-static-theorem.md`。

矩形 grids 是该定理的特例；`docs/t3-static-hierarchical-theorem.md` 给出对应的闭式增量公式。

## Lemma A：单层 projection bound

把执行切成第 $\ell$ 条通信边界上的 phases。一个 phase 至多读取/写出 $s$ 个 words；在该 phase 内记

- $S_A$：出现过的 $A$-entries；
- $S_B$：出现过的 $B$-entries；
- $S_C$：出现过的 partial/output entries。

每个完成的 scalar product 对应一个三元组 $(i,k,j)$，其三个 projections 分别落在 (S_A,S_B,S_C)。Loomis–Whitney/HBL 给出

\[
|F|\le\sqrt{|S_A||S_B||S_C|}.
\]

结合 phase 的 memory/transfer budget，可得到该层完成的 products 上限；对所有 phases 求和，得到该层的 word-volume lower bound

\[
V_\ell\ge \Lambda_\ell(g_\ell;z,y)-O(n^2).
\]

**仍待完成的部分：** 需要把 phase 切分、本地容量 $M_\ell$、replication 和输入输出 materialization 接到上述 owner-boundary theorem 上，并证明有限容量项的精确系数是

\[
\Lambda_\ell(g;z,y)
=\kappa_\ell(n,P_\ell,M_\ell)
\left(\frac1{ab}+\frac z{ac}+\frac y{bc}\right).
\]

## Lemma B：nested ownership chain

对每个层次固定一个 block ownership map。第 $\ell+1$ 层的 owner 必须是第 $\ell$ 层 owner 的 quotient/coarsening；因此其三维 grid 满足

\[
g_{\ell+1}\preceq g_\ell.
\]

三层执行因此诱导一个

\[
(g_1,g_2,g_3)\in\mathcal C(P^*).
\]

**这里的关键边界：** 该 lemma 对 static ownership 是定义性的；若允许执行期间动态重分块、动态 replication 或不同阶段使用不同 processor grid，就不能直接使用同一条 chain，需要把 theorem 改成对 chain sequence 或 time-expanded chain 的下界。

## Lemma C：edge-volume additivity

把慢存储↔$P_3$、$P_3\leftrightarrow P_2$、$P_2\leftrightarrow P_1$ 视为三条不同收费边。每个 word 在每条实际边上的传输都单独计数，因此

\[
Q_{\mathrm{vol}}=V_1+V_2+V_3.
\]

在这个计费定义下，Lemma A 的三个 lower bounds 可以相加；输入输出 materialization 只产生 $O(n^2)$ 边界项。

## Arbitrary-schedule lifting target

静态 nested-partition theorem 已经完成；更强的 arbitrary-schedule 目标是证明：动态 owner labels 能诱导一个 time-expanded nested partition，或者给出一个不弱于它的带权 copy-lineage 下界。当前已证明的动态 corollary 只有
\[
\sum_{\ell=1}^{3}V_\ell\ge \partial(\Pi_{m fine}),
\]
它不提供逐边 chain envelope。

因此旧的完整 affine-line sum (N(z,y)) 仍只能作为矩形几何 proxy。要得到带容量的 T3-volume，需要额外证明 phase/HBL 项与 nested-partition 增量项如何 charging，不能由 arrangement enumeration 单独推出。

## 需要的反例检查

在声明 T3-volume 前必须分别测试：

1. 一个 word 是否可以在一次跨层传输中同时满足两个层次的 projection budget；
2. replication 是否让某一层的 $V_\ell$ 低于固定-grid line；
3. 动态 grid 是否产生没有单一 chain 的执行；
4. recomputation 是否改变 HBL phase 的 product count；
5. 不平衡 work 是否绕过以 $P_1$ 为基准的 phase bound。

如果其中任一项成立，应该扩大模型中的 schedule class，而不是把反例隐藏在 $N/I$ 计算之外。

## 当前实验对应关系

- `check_one_level_recovery.py`：验证矩形 GEMM 的 affine geometry；
- `check_three_level_model.py`：验证 grid compatibility、envelope counts 和 $N\ge I$；
- `prove_2r_subfamily_empty_cell_certificates.py`：验证一个固定 divisor profile 的 arrangement cells；
- `check_nested_partition_weighted_counterexample.py`：证明非对称成本下矩形化反例；
- `check_l_level_static_theorem.py`：验证静态 (L)-level 增量定理。

因此目前最重要的下一步是补出 phase/HBL 的物理尺度推导和 time-expanded owner lemma，而不是继续增加 (r) 的样本。

## 已取得的受限定理：T3-static

`docs/static-grid-ownership-lemma.md` 和 `work/check_static_grid_ownership.py` 完成了 static-grid 版本的复制/归约计数。固定 (a\times b\times c) grid、单份初始输入、每个 product 一次计算时，SG-1 给出 exact leading edge volume，标准 broadcast/reduction schedule 可以达到它。若三条边的 ownership maps componentwise coarsen，则对兼容 chain 求和得到 T3-static。

这不是 arbitrary-schedule 的 T3-volume：动态 grid、免费初始复制、recomputation 和有限容量 phase coupling 仍未覆盖。
