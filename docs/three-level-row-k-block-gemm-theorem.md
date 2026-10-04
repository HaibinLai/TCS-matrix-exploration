# 三层 row--k-block classical GEMM 定理

这是当前最小的、包含 C partial 的三层 nested GEMM 定理。它使用固定的
row-by-k owner assignment，把三层层次、A/B 复制、C 归约和最终写回放在
同一个 word-volume 计费模型里。

## 模型

取矩形 GEMM
\[
A\in\mathbb R^{m\times k},\qquad
B\in\mathbb R^{k\times n},\qquad
C=AB.
\]

把 \([m]\) 划分为 \(H\) 个 row blocks，把 \([k]\) 划分为 \(S\) 个非空
reduction blocks。层次为

\[
\text{root source/output}
\longrightarrow
\text{\(H\) row-middle groups}
\longrightarrow
\text{\(HS\) fine owners \((h,s)\)}.
\]

owner \((h,s)\) 计算
\[
\{a_{i,k}b_{k,j}: i\in I_h,\ k\in K_s,\ 1\le j\le n\}.
\]

模型假设：

1. 每个 product 只计算一次；
2. A、B 在 root 各只有一个 source copy；
3. 每个 fine owner 产生一个 \(C_{i,j}\) 的 \(s\)-partial；
4. partial 必须在对应 row-middle group 合并，最终 \(C_{i,j}\) 写回 root；
5. 每条 root-to-middle 或 middle-to-fine word movement 都计一次；
6. 不允许 recomputation、压缩或免费初始复制；
7. 暂不把容量 reload、message startup 和拓扑拥塞混入 volume。

令 \(V_{\mathrm{top}}\) 是所有 root-to-middle edges 的 aggregate volume，令
\(V_{\mathrm{fine}}\) 是所有 middle-to-fine edges 的 aggregate volume。

## 定理

任意满足上述静态 nested assignment 的执行满足

\[
\boxed{
V_{\mathrm{top}}\ge mk+Hkn+mn,
}
\tag{RK-top}
\]

\[
\boxed{
V_{\mathrm{fine}}\ge mk+Hkn+Smn.
}
\tag{RK-fine}
\]

这里三项分别对应 A、B 和 C 的 movement。因此总 word volume 满足

\[
\boxed{
Q_{\mathrm{RK}}
\ge
2mk+2Hkn+mn+Smn.
}
\tag{RK-total}
\]

## 证明

### A

每个 \(a_{i,k}\) 只被 owner \((h(i),s(k))\) 使用。root 到该 owner 的唯一路径
经过一个 row-middle group，因此该 entry 至少跨 top edge 一次、fine edge 一次。
共有 \(mk\) 个 A-entry，得到两条边各 \(mk\)。

### B

每个 \(b_{k,j}\) 被每个 row block \(I_h\) 的 owner \((h,s(k))\) 使用。它
至少要从 root 复制到全部 \(H\) 个 row-middle groups，再分别到这 \(H\) 个
fine owners。因此 B 在 top 和 fine 两条边各贡献 \(Hkn\)。

### C partial 与最终写回

固定 \(C_{i,j}\)。每个 reduction block \(K_s\) 产生一个由 owner
\((h(i),s)\) 负责的 partial，共 \(S\) 个 partial。每个 partial 必须穿过
该 row group 的 middle-to-fine 边才能进入 row-middle 的归约状态，所以 fine
edge 至少承担 \(Smn\) 个 C-partial movements。

归约后的一个 \(C_{i,j}\) 必须写回 root，所有 \(mn\) 个输出各贡献一次
top-edge movement。三类计数相加即得 (RK-top) 和 (RK-fine)。

## Matching schedule

对每个 row block \(h\) 和 reduction block \(s\)：

1. root 将 \(A_{I_h,K_s}\) 发送到 row-middle，再发送到 owner \((h,s)\)；
2. root 将每个 \(B_{K_s,:}\) 发送到每个 row-middle，再发送到对应
   owner \((h,s)\)；
3. owner \((h,s)\) 完成该 block 的 products，并把每个 \(C_{i,j}\)
   partial 发送回 row-middle；
4. row-middle 对每个 \(C_{i,j}\) 的 \(S\) 个 partial 做归约；
5. row-middle 将 \(C_{i,j}\) 写回 root。

逐个 \(h,s\) 和 \(j\) 流式执行即可，且每条边的 movement 数恰好为

\[
V_{\mathrm{top}}=mk+Hkn+mn,\qquad
V_{\mathrm{fine}}=mk+Hkn+Smn.
\]

所以 (RK-top)--(RK-fine) 在这个明确的三层静态模型中 tight。

## Asymmetric edge/type costs

若 top/fine 两条边对 A、B、C movement 的成本分别为
\(\alpha_{\mathrm{top},X}\) 和 \(\alpha_{\mathrm{fine},X}\)，则同一个
matching schedule 给出 tight 的带权值：

\[
\begin{aligned}
Q_{\mathrm{asym}}
={}&
\alpha_{\mathrm{top},A}mk
+\alpha_{\mathrm{top},B}Hkn
+\alpha_{\mathrm{top},C}mn\\
&+
\alpha_{\mathrm{fine},A}mk
+\alpha_{\mathrm{fine},B}Hkn
+\alpha_{\mathrm{fine},C}Smn.
\end{aligned}
\tag{RK-asym}
\]

证明只需对三类 entry 分别使用上面的 incidence/cut 计数；非负成本下
逐类 schedule 仍然达到每一项。

## 与增量 T3 定理的关系

本定理把所有 source arrival 和最终 output write-back 都计入，因此比
“保留一个已有副本”的增量口径多出边界项。若改用 T3-static-vector 的
incremental convention，A/B/C 中被指定为 retained 的一份 copy 可以删去，
剩余项正好退化到对应 \(g_1=(H,S,1)\)、\(g_2=(H,1,1)\) 的 nested-grid
增量公式。

这个结果仍然是固定 row--k-block assignment 的定理。任意动态 owner、
有限容量 reload、free initial replication 和 recomputation 需要回到联合
phase/cut trace，而不能从 (RK-total) 直接外推。
