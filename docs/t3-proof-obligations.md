# T3-volume 的证明骨架与缺口

这份文件把三层 nested communication lower bound 拆成可以分别验证的命题。它不把当前的 $N(z,y)$ 直接当成已经证明的下界。

## 目标

在 static-grid、no-recomputation、counted-replication 的 classical GEMM 模型中，证明

\[
Q_{\mathrm{vol}}(\mathcal A;z,y)
\ge
\min_{\mathbf g\in\mathcal C(P^*)}
\sum_{\ell=1}^{3}\Lambda_\ell(g_\ell;z,y)-O(n^2).
\]

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

**尚未完成的部分：** 需要明确 $s$、本地容量 $M_\ell$、replication、输入输出 materialization 如何进入不等式，并证明最后的系数确实是

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

## Conditional theorem

若 Lemma A 对所有允许的 static ownership grid 成立，且 Lemma B 的 chain 约束覆盖所有合法 schedule，则对任意 schedule 有

\[
Q_{\mathrm{vol}}(\mathcal A)
\ge
\sum_{\ell=1}^{3}\Lambda_\ell(g_\ell;z,y)-O(n^2)
\]

对于某条实际 chain。对所有可能的 chain 取最小值，得到

\[
Q_{\mathrm{vol}}(\mathcal A)
\ge N(z,y)-O(n^2).
\]

这说明 $N$ 是 conditional theorem 的右侧；它不是单靠 arrangement enumeration 得出的无条件 lower bound。

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
- 尚无脚本证明 Lemma A 或 Lemma B 对任意 GEMM schedule 成立。

因此目前最重要的下一步是补出 Lemma A 的物理尺度推导，而不是继续增加 $r$ 的样本。

## 已取得的受限定理：T3-static

`docs/static-grid-ownership-lemma.md` 和 `work/check_static_grid_ownership.py` 完成了 static-grid 版本的复制/归约计数。固定 (a\times b\times c) grid、单份初始输入、每个 product 一次计算时，SG-1 给出 exact leading edge volume，标准 broadcast/reduction schedule 可以达到它。若三条边的 ownership maps componentwise coarsen，则对兼容 chain 求和得到 T3-static。

这不是 arbitrary-schedule 的 T3-volume：动态 grid、免费初始复制、recomputation 和不规则 ownership 仍未覆盖。
