# 有限容量 row-split GEMM 的 tight 子定理

这是当前 finite-capacity 联合问题的第一个完整 tight 子定理。它固定一种
row-split owner assignment，并要求 local cache 足够保存一个 owner 的整行
A。这样可以同时计入 A/B arrivals、C accumulation 和最终 output write-back，
而不是把 C 当作免费状态。

## 模型

计算

\[
A\in\mathbb F^{R\times K},\qquad
B\in\mathbb F^{K\times N},\qquad
C=AB.
\]

owner \(r\in[R]\) 独占计算 C 的第 \(r\) 行。root 是 A/B source 和 C output
sink。child group 可以有一个只存 B 的 shared cache，容量为 \(G\)。

- 若 \(G=0\)，每个 B-entry 直接送到每个 owner；
- 若 \(G\ge1\)，parent→group edge 可以暂存一个当前 B-entry，并向所有
  owners 免费 promotion；
- 每个 owner 的 local cache 容量为 \(M\ge K+2\)，可以同时保存整行
  \(A_{r,:}\)、一个当前 \(C_{r,j}\) accumulator 和一个 B-entry；
- C accumulator 的第一次初始化在 owner 内免费，最终每个 \(C_{r,j}\)
  必须向 root 写回一次；
- shared-to-local promotion、eviction 和乘加计算不计 word volume；
- 不允许 recomputation、压缩或免费初始复制。

令 \(Q\) 统计 parent/child edge 上 A/B arrivals 加 child/root edge 上的
C final writes。这里不把多个 owner 的 local load 重复算成一次 shared arrival。

## 定理

在上述模型中，完成全部 \(RKN\) 个 products 的最小 word volume 为

\[
\boxed{
Q^\star(R,K,N,G)=RK+RN+
\begin{cases}
RKN,&G=0,\\
KN,&G\ge1.
\end{cases}}
\tag{FS-RS}
\]

### 证明：下界

每个 owner \(r\) 必须使用自己的 \(K\) 个 A-entry；由于 A 只有 root
source，至少需要 \(RK\) 次 A arrival。

若 \(G=0\)，每个 \(B_{qj}\) 都必须分别到达 R 个 owners，因此 B 至少贡献
\(RKN\)。若 \(G\ge1\)，每个 \(B_{qj}\) 至少需要从 root 穿过
parent→group edge 一次，因此 B 至少贡献 \(KN\)；shared cache 之后的
promotion 不另计 parent edge arrival。

每个 \(C_{r,j}\) 的最终值位于 owner 侧，而 root 是唯一 output sink，故
每个输出至少需要一次 write-back，共 \(RN\) 次。三类 movement 属于不同
word event，得到 (FS-RS)。

### 证明：matching schedule

先把每个 owner 的整行 \(A_{r,:}\) 送入 local cache，共 \(RK\) 次。
随后按 \(j=1,\ldots,N\) 外层流式执行：

1. 在 owner \(r\) 初始化一个 \(C_{r,j}\) accumulator；
2. 对 \(q=1,\ldots,K\)，若 \(G\ge1\)，root 将 \(B_{qj}\) 送入
   shared cache 一次，所有 owners promotion 后同时使用；若 \(G=0\)，
   则将该 B-entry 分别送到 R 个 owners；
3. 每个 owner 使用 resident 的 \(A_{r,q}\)、当前 B-entry 和
   \(C_{r,j}\) 完成一个 product；
4. 该 j 完成后把 \(C_{r,j}\) 写回 root。

每个 owner 同时只需 K 个 A-entry、一个 C accumulator 和一个 B-entry，故
\(M\ge K+2\) 足够。这个 schedule 的 A、B、C 费用分别恰好是
\(RK\)、\(KN\) 或 \(RKN\)、\(RN\)，达到下界。

## 这个定理说明什么

- 它是一个包含 C partial/final write-back 的 finite-capacity tight result，而
  不是 operand-only 诊断；
- shared cache 的收益可以严格写成 B projection lineage 从 R 份降为 1 份；
- 它仍然是受限 row-split assignment，不能外推到任意动态 owner、较小的
  local cache、C partial reduction 或 recomputation；
- 当 \(M<K+2\) 时，必须在 A retention、C accumulation 和 B streaming 之间
  做新的 phase/reload 优化，这正是一般 E-TRACE 尚未求解的部分。

\(R=2,K=N=2\) 时，公式给出 \(Q^\star=4+4+8=16\)（无 shared cache）
和 \(Q^\star=4+4+4=12\)（\(G\ge1\)）。前者与 operand-only 的 12 次
arrival 加 4 次 output write-back 一致；后者体现 shared B lineage 带来的
完整 GEMM traffic reduction。

## 非对称 read/write cost

若 A/B arrivals 和 C write-back 的单位成本分别为
\(\alpha_A,\alpha_B,\beta_C\)，同一证明给出并达到

\[
Q_{\rm asym}^\star=
\alpha_A RK+\beta_C RN+
\alpha_B
\begin{cases}
RKN,&G=0,\\
KN,&G\ge1.
\end{cases}
\]

这里的 tightness 仍只要求成本按 data type/direction 固定；若成本随拥塞、
消息大小或时间变化，则需要把 cost state 加入 E-TRACE。
