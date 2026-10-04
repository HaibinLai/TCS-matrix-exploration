# 重计算：从固定产品 owner 到 event-assignment 优化

## 1. 为什么原来的 C-partial 下界不能直接延伸

在固定的 row--k-block owner 模型中，每个输出 (c_{ij}) 的 (S) 个
reduction-block partial 分别在 (S) 个 fine owner 产生。于是 fresh-arrival
记账给出 (S) 个 partial/output arrivals；保留已有 partial 的 incremental
记账则给出相应的 (S-1) 个跨边增量。这个计数隐含了两个条件：

1. 每个 product event 只计算一次；
2. product event 的 owner assignment 已经固定。

允许 recomputation 后，第二个条件消失了。令

\[
\mathcal F(u)=\{(r,t):\text{owner }r\text{ 在时刻 }t\text{ 计算 product }u\}
\]

是 product (u=(i,k,j)) 的带重数 event 集合，并令

\[
R_A(a;\mathcal F),\quad R_B(b;\mathcal F),
\quad R_C(c;\mathcal F)
\]

分别是由这些 events 产生的 operand demand leaves、partial reduction
sources 和 output sinks。对一个已经固定的 (mathcal F)，逐条 edge 的
Steiner/forest cut 仍然成立；但对所有可能的 (mathcal F) 取最小值时，

\[
W'(\mathcal F)=\sum_u|\mathcal F(u)|\ge mkn
\]

也会进入 phase/HBL 项。因而不能把“原来的 C-reduction 下界”与一个独立的
recomputation penalty 相加；二者共享同一组 event 和 resident trace。

## 2. 一个必须先分清的边界例子

考虑 (1\times2) 乘 (2\times1) 的 GEMM，root 下有两个 fine owners
(r_1,r_2)，并把两个 (k)-products 分到不同 owner：

\[
c=a_1b_1+a_2b_2,
\qquad
u_1\text{ 在 }r_1,\;u_2\text{ 在 }r_2.
\]

若 A/B 从 root 单源送到 owner，每个 operand word 的边权为 1，而每个
C-partial 到 root 的边权为 (lambda)，则固定 split assignment 的成本是

\[
Q_{\rm split}=4+2\lambda .
\]

若把两个 products 都改在 (r_2) 计算，则只有一个 C arrival：

\[
Q_{\rm colocate}=4+\lambda .
\]

这不是 recomputation 定理的反例，而是一个重要的模型边界：在**没有固定
owner 约束**的普通 classical GEMM 中，直接改变 product assignment 已经能
消掉一个 partial；不应把这个收益误称为 recomputation。于是固定 row--k
定理只能声称“给定 assignment 的 tight bound”。

真正的 recomputation trade-off 需要额外约束。例如，若某个 event 在
(r_1) 是另一个 consumer 必须保留的结果，同时 (r_2) 需要同一个 product
来完成本地 reduction，那么在 (r_2) 再计算一次该 product 可以减少一个
C-partial arrival，但会多搬运一次 A/B。此时，在上述单位 operand 成本和
C 边权 (lambda) 下，复制该 event 的差额为

\[
\Delta Q=2-\lambda.
\]

当 (lambda>2) 时，额外计算和两次 operand arrivals 可能值得；当
(lambda<2) 时则不值得。这个例子说明优化变量必须同时包含 event multiplicity
和 edge weights，不能只看 scalar work 或只看 C partial 数量。

## 3. 固定 event assignment 的可证明下界

在固定层次树 (H)、固定 source sets (S_0(d))、无容量限制且不允许把
一个 event 的结果“凭空复制”的模型中，对任意固定 (mathcal F) 有

\[
Q(\mathcal F)\ge
\sum_{a,e}w_e\,\chi_e\!\left(S_0(a),R_A(a;\mathcal F)\right)
+\sum_{b,e}w_e\,\chi_e\!\left(S_0(b),R_B(b;\mathcal F)\right)
+\sum_{c,e}w_e\,\chi_e\!\left(R_C(c;\mathcal F),T_C(c)\right),
\]

其中 (chi_e(X,Y)) 表示连接 source set (X) 与 demand/sink set (Y)
的最小共享路径 forest 是否使用 edge (e)。树 broadcast/reduction 达到
这个 memory-independent bound。

因此更强的目标应写成联合优化：

\[
\min_{\mathcal F,\,\tau}
\left[
Q_{\rm forest}(\mathcal F;\tau)
+Q_{\rm reload}(\mathcal F;\tau)
+\mu\sum_u|\mathcal F(u)|
\right],
\]

其中 (	au) 是 resident/phase trace，(mu) 只是把额外 arithmetic work
纳入目标的示意权重。若目标只计 I/O，则应把第三项替换为由 finite-capacity
phase envelope 导出的 work-dependent 约束，而不是任意加入一个常数罚项。

## 4. 对本项目的直接结论

- `three-level-row-k-block-gemm-theorem.md` 和 `l-level-row-k-block-gemm-theorem.md`
  对固定 fresh-arrival assignment 是 tight 的；
- `replication-recomputation-boundaries.md` 的 RF/Steiner 结论可以逐 event
  使用，但不能对 (mathcal F) 的最优选择闭式化；
- 对普通 classical GEMM，第一步应区分“重新分配 product owner”和“同一
  product 的重复 event”，避免把前者误报成 recomputation gain；
- 真正的开放问题是：在有限容量、非均匀 edge weights、动态 owner labels
  下，求出 event-assignment 与 phase/reload 的联合下界，并构造达到它的
  schedule。这个问题也更适合先在 (2\times2\times2) 或单输出小 DAG 上
  做整数搜索，再尝试一般定理。

