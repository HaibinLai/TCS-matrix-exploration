# 一层 phase/HBL lemma：已恢复部分与三层缺口

这份笔记只处理 classical GEMM 的一个标准 phase argument。它恢复有限本地内存项，但不把它误写成三层 nested theorem。

## Phase model

考虑一个处理单元执行 $W$ 个 scalar products，局部快速内存容量为 $M$ words。把执行切成 phases，使每个 phase 至多有 $M$ 个 words 穿过该处理单元的通信边界。phase 开始时最多已有 $M$ 个 words，因此该 phase 期间可参与计算的不同 $A,B,C$ entries 总数至多为 $2M$，忽略常数级输入输出边界项。

令该 phase 实际使用的 entries 集合为 $S_A,S_B,S_C$。每个 scalar product 对应一个 $(i,k,j)$，投影到

\[
(i,k),\qquad(k,j),\qquad(i,j).
\]

Loomis–Whitney 给出

\[
F_t\le\sqrt{|S_A||S_B||S_C|}.
\]

在 $|S_A|+|S_B|+|S_C|\le 2M$ 下，AM–GM 得

\[
F_t\le \left(\frac{2M}{3}\right)^{3/2}=O(M^{3/2}).
\]

因此若一个处理单元完成 $W$ 个 products，至少需要

\[
\Omega\left(\frac{W}{M^{3/2}}\right)
\]

个 phases。每个完整 phase 搬运 $\Theta(M)$ words，于是得到 per-processor volume

\[
Q_{\mathrm{local}}=\Omega\left(\frac{W}{\sqrt M}\right).
\]

对 balanced $P$-processor classical GEMM，$W=\Theta(n^3/P)$，所以

\[
Q_{\mathrm{local}}
=\Omega\left(\frac{n^3}{P\sqrt M}\right)
\]

（这里是每个处理单元的 volume；总 volume 还要乘上参与计算的处理器数）。

## 这一步证明了什么

这恢复了已知 one-level communication lower bound 的 memory-dependent 项。它只使用 computation DAG、local capacity 和 phase volume；没有使用 processor-grid factorization，也没有使用 nested ownership。

## 还没有证明什么

它没有推出当前 affine line

\[
\frac{mk}{ab}+\frac{mn}{ac}+\frac{kn}{bc},
\]

因为该 line 是 memory-independent、grid/ownership-sensitive 的项。要得到它，需要另一个 argument：固定 block ownership 后，$A$、$B$、$C$ 的不同 projections 必须在 processor grid 上传播或归约，并分别产生三个数据移动项。

它也不能自动对三个层次求和。若同一个 word 同时满足多个层次的 phase budget，直接把三个 one-level bounds 相加可能重复计数；这正是 T3-volume 的 edge accounting 和 nested-chain lemma 必须显式处理的地方。

## 下一条严格命题

下一步要证明的是固定三维 grid $g=(a,b,c)$ 下的 memory-independent ownership lemma：在 static block ownership、一次计算每个 product、且 replication 通过计费传输产生的条件下，任意 schedule 至少付出

\[
\Omega\left(
\frac{mk}{ab}+\frac{mn}{ac}+\frac{kn}{bc}
\right)
\]

的相应 edge volume（常数和 $O(mk+mn+kn)$ 边界项需要明确）。只有把这个 lemma 与三层 componentwise compatibility 结合，才会得到 $N(z,y)$ 的真实下界。
