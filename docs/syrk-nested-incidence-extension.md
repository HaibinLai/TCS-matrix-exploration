# SYRK 的多级 nested-incidence 扩展（受限静态定理）

这份文件给出一个直接但严格的 SYRK 扩展。它只处理
\(C=AA^{\mathsf T}\) 的静态、单源、一次 product 计算和 word-volume 模型；
不改写 2024 年已有的 sequential/distributed symmetric-kernel 结果，也不声称
已经解决有限容量或动态 recomputation。

## 对称 iteration space 和投影

取

\[
A\in\mathbb F^{m\times k},\qquad C=AA^{\mathsf T}.
\]

只存储下三角输出：

\[
O=\{(i,j):1\le j\le i\le m\},
\qquad
T_{\triangle}=\{(i,q,j):(i,j)\in O, 1\le q\le k\}.
\]

一个 product \((i,q,j)\) 使用两个 A-entry：\(a_{iq}\) 和 \(a_{jq}\)。
当 \(i=j\) 时二者是同一个 entry，因此不能把左右角色机械相加。
对 \(S\subseteq T_\triangle\) 定义 union projection

\[
\pi_A^{\triangle}(S)=
\{(r,q):\exists(i,q,j)\in S, r\in\{i,j\}\},
\]

\[
\pi_C^{\triangle}(S)=
\{(i,j):\exists q\ (i,q,j)\in S\}.
\]

对 nested partitions
\(Pi_1\preceq\Pi_2\preceq\Pi_3\preceq\Pi_4=\{T_\triangle\}\)，令

\[
X_A^{\triangle}(\Pi)=
\sum_{S\in\Pi}|\pi_A^{\triangle}(S)|,
\qquad
X_C^{\triangle}(\Pi)=
\sum_{S\in\Pi}|\pi_C^{\triangle}(S)|.
\]

## 定理（SYRK-T3-static）

在以下条件下：每个 product 恰好计算一次；A 在 root 只有一个 source
copy；C 的下三角输出在 root 各只有一个 final copy；parent side 没有免费的
child retained copies；partial reduction 和 A broadcast 只按跨 edge word
计费；不允许 recomputation 或压缩。则每条 hierarchy edge 满足

\[
\boxed{
V_\ell^A\ge
X_A^{\triangle}(\Pi_\ell)-X_A^{\triangle}(\Pi_{\ell+1}),
}
\tag{SYRK-A}
\]

\[
\boxed{
V_\ell^C\ge
X_C^{\triangle}(\Pi_\ell)-X_C^{\triangle}(\Pi_{\ell+1}).
}
\tag{SYRK-C}
\]

对任意非负 edge/type costs \(\alpha_{\ell,A},\beta_{\ell,C}\)，

\[
Q_w\ge\sum_\ell
\left(
\alpha_{\ell,A}\Delta_\ell^{A,\triangle}
+\beta_{\ell,C}\Delta_\ell^{C,\triangle}
\right).
\tag{SYRK-weighted}
\]

### 证明

固定 A-entry \(a_{rq}\)。设它在 fine partition 中出现 \(d_f\) 次，在
coarse partition 中出现 \(d_c\) 次。每个 fine part 都必须能读取该 entry；
coarse side 已有的 \(d_c\) 个 copies 至多覆盖 \(d_c\) 个 incidences，因而
至少需要 \(d_f-d_c\) 个新增 A words。对所有 \((r,q)\) 求和就是
(SYRK-A)。这里使用 union projection 正好处理了 diagonal product 的单份
A-entry 和 off-diagonal product 的两个不同 row entries。

固定输出 \(c_{ij}\)。fine side 的每个 partition incidence 是一个尚未在
coarse side 合并的 partial。一个跨 edge word 至多把两个 current partial
aggregate 合并为一个，因此从 \(d_f\) 个 partial 到 \(d_c\) 个 partial 至少
需要 \(d_f-d_c\) 次 movement，求和得到 (SYRK-C)。树形 broadcast/reduction
分别达到两项，故在该静态 hierarchy 模型中 tight。证毕。

## 与 2024 symmetric-kernel 结果的关系

2024 年的 symmetric-kernel 工作已经处理 SYRK/SYR2K/SYMM 的单层 sequential
和 distributed-memory lower bounds，以及对应的 triangle-block algorithms。
这里新增的对象是把对称 iteration space 的 union projection 放进任意 rooted
nested hierarchy，并允许每条 edge 使用独立的非对称 word 权重。它不声称改进
2024 年单层常数，也不声称已经覆盖 local-memory phase 项。

后续若要处理 SYMM，需要为 symmetric B-entry 定义类似的 alias-aware union
projection；若要处理 SYR2K，还需要区分两个输入矩阵的 source sets。普通 GEMM
中的三投影公式不能直接替代这些定义。

## SYMM 的同一静态模板

对 SYMM，取

\[
A\in\mathbb F^{m\times k},\qquad
B=B^{\mathsf T}\in\mathbb F^{k\times k},\qquad
C=AB.
\]

令 \(T_{\rm symm}=[m]\times[k]\times[k]\)，并把对称 B-entry 用无序 pair
索引。对 \(S\subseteq T_{\rm symm}\) 定义

\[
\pi_A^{\rm symm}(S)=\{(i,q):(i,q,j)\in S\},
\]

\[
\pi_B^{\rm symm}(S)=
\{\{q,j\}:(i,q,j)\in S\},
\qquad
\pi_C^{\rm symm}(S)=\{(i,j):(i,q,j)\in S\}.
\]

因此 \(B_{qj}\) 与 \(B_{jq}\) 在同一个 unordered-pair projection 中只算
一次。对任意 nested partitions，完全相同的 incidence proof 给出

\[
V_\ell^A\ge\Delta_\ell^{A,\rm symm},\qquad
V_\ell^B\ge\Delta_\ell^{B,\rm symm},\qquad
V_\ell^C\ge\Delta_\ell^{C,\rm symm},
\]

其中每个 \(\Delta\) 是相应 projection sum 的相邻层差值。树形 A/B
broadcast 与 C reduction 达到该 bound。这个 SYMM 结论仍然只是在固定静态
nested owner、single-source、no-recomputation word-volume 模型中的结构性
扩展；它没有覆盖 2024 工作中的 symmetric HBL 常数、有限 local memory 或
latency 最优性。
