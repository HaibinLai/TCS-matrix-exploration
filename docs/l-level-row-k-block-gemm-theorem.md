# Fresh-arrival row--k-block 的 \(L\)-level 定理

这是三层 row--k-block theorem 的递归扩展。它采用明确的 fresh-arrival
计费口径：每一级 child group 获得一份所需 operand 时计一次，C partial
在父级归约后继续向上。保留父级已有副本的 incremental convention 见
T3-static-vector；两者不能混用。

## 模型

计算矩形 GEMM
\[
A_{m\times k}B_{k\times n}=C_{m\times n}.
\]

层级编号为 \(0,1,\ldots,L\)，0 是 root source/output，\(L\) 是 fine
product owners。第 \(\ell\) 层把行划分成 \(H_\ell\) 个 blocks，把 reduction
dimension 划分成 \(S_\ell\) 个 blocks，其中
\[
H_0=S_0=1,\qquad
H_0\le\cdots\le H_L,\qquad
S_0\le\cdots\le S_L.
\]

第 \(\ell\) 层的 groups 由 row block 和 reduction block 的笛卡尔积给出。
每个 product 在唯一的 level-\(L\) group 计算。对 edge
\(e_\ell=(\ell-1,\ell)\) 采用以下静态规则：

1. 每个 level-\(\ell\) child group 为其 owner assignment 接收所需 A/B
   entries 的一份 fresh arrival；
2. level-\(\ell\) 产生的 C partial 全部跨 \(e_\ell\) 送到父层，再在那里
   按 row block 归约；
3. level 0 最终接收每个 C-entry 一份 output；
4. 不允许 recomputation、压缩或免费初始 replication；
5. 双向跨边 movement 都计入同一个 word volume。

令 \(V_\ell\) 是 edge \(e_\ell\) 的 aggregate volume。

## 定理

任意满足上述静态 nested assignment 的执行，对每个
\(1\le\ell\le L\) 都满足

\[
\boxed{
V_\ell\ge
mk+H_\ell kn+S_\ell mn.
}
\tag{L-RK}
\]

三项依次对应 A fresh arrivals、B 的 row-group copies 和 C partials。
因而

\[
\boxed{
Q_{\mathrm{fresh}}
\ge
\sum_{\ell=1}^{L}
\left(mk+H_\ell kn+S_\ell mn\right).
}
\tag{L-RK-total}
\]

## 证明

固定一个 edge \(e_\ell\)。

- 每个 A-entry 属于唯一的 level-\(\ell\) row/reduction child group，
  因而至少贡献 \(mk\) 次 fresh arrival；
- 每个 B-entry 被 \(H_\ell\) 个 row groups 需要，每个 group 至少收到一份，
  因而贡献 \(H_\ell kn\)；
- 每个 C-entry 在 level \(\ell\) 有 \(S_\ell\) 个 reduction-block partial，
  且规则要求这些 partial 在父层归约，因此贡献 \(S_\ell mn\)。

三类 entry 不重叠，逐项相加得到 (L-RK)。

## Tightness

按层递归执行：

1. 从 root 向下，按每一级 row/reduction block 复制 A/B；
2. 在 level \(L\) 计算所有 products；
3. 从 level \(L\) 向上，把每个 C-entry 的 partial 逐级发送到父层；
4. 每一级父 group 完成规定的 row-wise reduction；
5. level 0 写回最终 C。

对每个 edge，A、B、C 三类 movement 分别恰好为
\[
mk,\qquad H_\ell kn,\qquad S_\ell mn.
\]
所以 (L-RK) 在这个 fresh-arrival 模型中 tight。

## 非对称边/类型成本

若 edge \(e_\ell\) 对 A、B、C movement 的单位成本分别为
\(\alpha_{\ell,A},\alpha_{\ell,B},\alpha_{\ell,C}\)，则

\[
\boxed{
Q_{\mathrm{asym,fresh}}
\ge
\sum_{\ell=1}^{L}
\left(
\alpha_{\ell,A}mk
+\alpha_{\ell,B}H_\ell kn
+\alpha_{\ell,C}S_\ell mn
\right),
}
\tag{L-RK-asym}
\]

并由同一个递归 schedule 取等。

## 边界

这个 theorem 的 fresh-arrival 规则使证明可以逐层归纳，但它没有把父层
已有副本用于抵消下一层的第一份 arrival。若允许 retained copies，正确对象
变成相邻 nested partitions 的 incidence difference；若允许动态 replication、
有限容量 reload 或 recomputation，则需使用联合 phase/cut trace。
