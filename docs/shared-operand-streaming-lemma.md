# Shared-operand streaming lemma

这是一个把 shared-cache exact trace 推广成公式的受限子定理。它只计
A/B operand traffic，用来隔离 shared-cache lineage；C partial、最终输出和
多级嵌套留给完整 E-TRACE。

## 模型

把 \(m=R\) 的 GEMM 按 row 分给 \(R\) 个 owners。owner \(r\) 负责
\[
\{a_{r,k}b_{k,j}:1\le k\le K,\ 1\le j\le N\}.
\]

每个 owner 的 local cache 容量为 2，只能同时保留一个 \(a_{r,k}\) 和一个
B-entry。child group 的 shared cache 只存 B，容量为 \(G\)。parent 对每个
A/B entry 只有一个 source copy；parent-to-owner 或 parent-to-group 的每个
arrival 计一个 word，shared-to-local promotion 免费；不允许 recomputation。

## 定理

在这个模型中，完成全部 \(RKN\) 个 products 的最小 operand arrival volume 为

\[
Q_{\mathrm{op}}^\star(R,K,N,G)=
RK+
\begin{cases}
RKN,&G=0,\\
KN,&G\ge1.
\end{cases}
\tag{SO-1}
\]

## 证明

每个 \(a_{r,k}\) 只被 owner \(r\) 使用，至少需要一次 arrival；共有 \(RK\)
个 A-entry，因此 A 至少贡献 \(RK\)。

当 \(G=0\) 时，每个 \(b_{k,j}\) 都必须分别送到 \(R\) 个 owners，B 至少贡献
\(RKN\)。当 \(G\ge1\) 时，每个 \(b_{k,j}\) 至少跨 parent-group 边一次，
所以 B 至少贡献 \(KN\)。

下界可以达到。\(G=0\) 时，每个 owner 固定一个 \(k\)，加载一次
\(a_{r,k}\)，依次读取 \(B_{k,:}\) 并计算该行的 \(N\) 个 products；对
\(k=1,\ldots,K\) 重复即可，每个 A-entry 一次、每个 B-entry 每个 owner
一次。

\(G\ge1\) 时，对每个 \(k\)，先让所有 owners 各加载自己的 \(a_{r,k}\)，
再把 \(B_{k,:}\) 逐 entry 流过 shared cache。每个 B-entry 只跨边一次，
promotion 到所有 owners 后完成该 \(k\) 的全部 products；local capacity 2
只需保留 \(a_{r,k}\) 和当前 B-entry。于是 schedule 使用 \(RK+KN\) 次
arrival，达到 (SO-1)。

## 与 exact trace 的关系

\(R=2,K=2,N=2\) 时，(SO-1) 给出

\[
Q_{\mathrm{op}}^\star(G=0)=12,\qquad
Q_{\mathrm{op}}^\star(G\ge1)=8,
\]

正好恢复 exact shared-cache trace 的结果。

这个 lemma 说明 shared cache 影响的是投影需求的 lineage：B 的需求集合从
“每个 owner 一份”变成“同一个 child group 的一份”。它还没有处理 C 的
partial reduction，因此不能替代三层 classical GEMM theorem。
