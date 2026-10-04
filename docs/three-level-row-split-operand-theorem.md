# 三层 row-split operand 通信定理

这是 shared-operand streaming lemma 的一个真正三层版本。它只研究
classical GEMM 的 A/B operand traffic，C partial 和最终归约仍由完整
T3-static theorem 处理。

## 模型

层次是一棵三层 rooted tree：

\[
\text{root source}
\longrightarrow
\text{\(H\) middle groups}
\longrightarrow
\text{\(R\) fine owners}.
\]

计算是 \(m=R\) 的 GEMM：
\[
C=AB,\qquad A\in\mathbb R^{R\times K},\quad
B\in\mathbb R^{K\times N}.
\]

fine owner \(r\) 负责第 \(r\) 行的全部 products。\(R\) 个 owners 被划分成
\(H\) 个 middle groups，记第 \(h\) 个 group 的 owner 集合为
\(\mathcal R_h\)，且 \(\sum_h|\mathcal R_h|=R\)。

\[
\{a_{r,k}b_{k,j}:1\le k\le K,\ 1\le j\le N\}.
\]

每个 A/B entry 在 root 只有一个 source copy。middle group 有至少一个
word 的 transient/shared cache；每个 fine owner 的 local cache 容量为 2。
每条层次边按 word arrival 计费，middle-to-owner promotion 和 local eviction
不单独收费；不允许 recomputation。C 的计算、写回和归约从这个 operand-only
定理中省略。

令 \(V_{\mathrm{top}}\) 是所有 root-to-middle edges 的 aggregate volume，令
\(V_{\mathrm{fine}}\) 是所有 middle-to-leaves edges 的 aggregate volume。

## 定理

任意满足上述模型的执行都满足

\[
\boxed{
V_{\mathrm{top}}\ge RK+HKN,
\qquad
V_{\mathrm{fine}}\ge RK+RKN.
}
\tag{3L-OP-LB}
\]

因此总 operand volume 满足

\[
Q_{\mathrm{op}}\ge 2RK+(H+R)KN.
\tag{3L-OP-TOTAL}
\]

## 证明

每个 \(a_{r,k}\) 只被 fine owner \(r\) 使用。root 只有一个 source，
所以该 entry 至少要穿过 root-to-middle 一次，再穿过 middle-to-owner
一次。共有 \(RK\) 个 A-entry，因此两条边各至少承担 \(RK\)。

每个 \(b_{k,j}\) 被每个 middle group 中的 owners 使用。root-to-middle
边上，每个 group 至少需要一个 arrival，因此 B 对 top edge 的贡献至少是
\(HKN\)。在 middle-to-leaves 边上，单个 B-entry 的需求叶集合包含全部
\(R\) 个 owners；每个 leaf-side copy lineage 至少产生一个 word event，
所以其贡献至少是 \(RKN\)。

两类 entry 的需求不同，逐 entry 相加得到 (3L-OP-LB)。

## Tightness schedule

对每个 reduction index \(k\)：

1. root 将所有 \(a_{r,k}\) 各发送一次到其所属 middle group，再各发送一次到
   owner \(r\)；
2. root 将 \(B\) 的 \(N\) 个 entries \(b_{k,j}\) 各发送一次到每个 middle
   group；
3. 每个 middle group 将当前 \(b_{k,j}\) 广播给自己的 owners；
4. owner \(r\) 保留 \(a_{r,k}\) 和当前 \(b_{k,j}\)，完成
   \(a_{r,k}b_{k,j}\)。

每个 middle group 的一个 shared slot 足够流式处理 \(B_{k,:}\)，owner 的
两个 local slots 足够保留一个 A-entry 和当前 B-entry。该 schedule 使用

\[
V_{\mathrm{top}}=RK+HKN,\qquad
V_{\mathrm{fine}}=RK+RKN,
\]

逐条达到下界。

## 与完整三层 GEMM theorem 的接口

这个定理已经包含三层 tree 上的 nested copy-lineage 和 matching schedule，
并展示 shared demand 如何改变不同边的 volume。要升级为完整 classical GEMM
定理，还需要把：

- C 的 \(b_\ell\)-way partial reduction；
- finite-capacity reload；
- 多个 middle groups 和 componentwise grid chain；
- asymmetric edge/type costs；
- recomputation；

加入同一个 trace。A/B 的证明可以直接作为 T3-Steiner incidence 项，C 则使用
已有的 nested-partition reduction 项。
