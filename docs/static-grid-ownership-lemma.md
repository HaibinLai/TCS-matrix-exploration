# Static-grid ownership lemma

这份 lemma 给出当前 affine line 的第一个实际来源。它只针对固定 block ownership 的 classical GEMM，不声称覆盖动态 grid、免费初始 replication 或 recomputation。

## 假设

对 $A_{m\times k}B_{k\times n}$，使用一个固定的 $a\times b\times c$ processor grid，且 $abc=P$。把矩阵切成

- $a$ 个 row blocks；
- $b$ 个 reduction-$k$ blocks；
- $c$ 个 column blocks。

假设：

1. 每个 $A$-entry 和 $B$-entry 初始只有一个付费 ownership；
2. 每个 scalar product 只计算一次；
3. 每个 $C$-entry 的 $b$ 个 partial products 最终只保留一份输出；
4. replication、broadcast、reduction 的每一条 word transfer 都计入 edge volume。

## 复制与归约计数

一个 $A$-block 的尺寸为 $mk/(ab)$。为了让 $c$ 个 column coordinates 都能参与计算，每个 $A$-entry 至少产生 $c-1$ 个额外副本。因此所有 $A$ 的总传输至少为

\[
V_A\ge(c-1)mk.
\]

同理，$B$-blocks 沿 $a$ 个 row coordinates 复制，得到

\[
V_B\ge(a-1)kn.
\]

每个 $C$-entry 的 $b$ 个 reduction-$k$ partials 必须合并成一个输出，至少需要 $b-1$ 次 word movement。因此

\[
V_C\ge(b-1)mn.
\]

于是固定 grid 的总 edge volume 满足

\[
V_{\mathrm{grid}}
\ge
(c-1)mk+(a-1)kn+(b-1)mn.
\tag{SG-1}
\]

除以 $P=abc$，得到 per-processor average

\[
\bar V_{\mathrm{grid}}
\ge
\frac{mk}{ab}+\frac{kn}{bc}+\frac{mn}{ac}
-\frac{mk+kn+mn}{P}.
\tag{SG-2}
\]

因此当前脚本使用的 affine line

\[
\lambda_{m,k,n}(a,b,c)=
\frac{mk}{ab}+\frac{mn}{ac}+\frac{kn}{bc}
\]

是 SG-2 的 leading term；少掉的 $P^{-1}$ 项是初始 ownership/output materialization 的边界修正，不能在小 $a,b,c$ 时假装为零。

## Matching schedule

在完全连接或允许 tree broadcast/reduction 的通信模型中，标准 blocked 3D schedule 可以：

1. 沿 $c$ 个 column coordinates 广播 $A$-blocks；
2. 沿 $a$ 个 row coordinates 广播 $B$-blocks；
3. 沿 $b$ 个 reduction coordinates 做 $C$-partial reduction。

它分别使用 $c-1$、$a-1$、$b-1$ 份 entry movement，因此达到 SG-1 的 leading volume。这个 matching statement 依赖静态 block ownership 和允许的通信拓扑；环形或受限网络需要单独计数 message hops。

## 三层推论（受限版本）

若三条收费边分别使用固定 grids $g_1,g_2,g_3$，且 ownership maps 按 componentwise divisibility coarsen，使

\[
g_3\preceq g_2\preceq g_1,
\]

则对每条边应用 SG-1，并将三条边的 volume 相加，得到

\[
Q_{\mathrm{static}}(\mathcal A)
\ge
\sum_{\ell=1}^{3}
V_{\mathrm{grid}}(g_\ell)-O(mk+mn+kn).
\]

对所有合法 chains 取最小值，得到 static-grid nested envelope 的下界；标准 nested broadcast/reduction schedule 在同一模型下给出 matching upper bound。

这已经是一个可证明的 **static-grid three-level theorem**。它还不是 arbitrary-schedule T3-volume，因为后者必须处理动态 ownership、免费初始复制、recomputation 和非块状的数据流。
