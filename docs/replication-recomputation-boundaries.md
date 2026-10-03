# Replication 与 recomputation 的模型边界

## 免费初始复制：从单源树到多源 forest

T3-Steiner 假定一个 A/B entry 只有一个 source。若允许免费初始复制，entry
\(d\) 的 source 是节点集合 \(S_0(d)\)，需求是叶子集合 \(R(d)\)。通信
不再由单棵 source-to-demand 子树描述，而是由

\[
\operatorname{Forest}_H(S_0,R)=
\min_{f:R\to S_0}
\operatorname{cost}\!left(
\bigcup_{r\in R}\operatorname{path}_H(r,f(r))
\right)
\tag{RF}
\]

给出：每个需求选择一个已有 source，所有选中的路径共享已经经过的树边。
若 \(S_0\) 只有一个节点，(RF) 退化为 T3-Steiner 的最小子树成本。

### 定理 RF

在无 recomputation、固定层次树、word-volume 计费且初始复制不收费的模型中，
任意执行对每个 A/B entry 至少付出

\[
\operatorname{Forest}_H(S_0(a),R_A(a)),
\qquad
\operatorname{Forest}_H(S_0(b),R_B(b)).
\]

证明是逐需求 cut/path：每个需求必须从某个初始 source 得到 entry；其 source-
demand path 上的每条边都需要一次代表该 entry 的传输。把需求分配给实际
使用的 source，并对共享边合并，即得到 (RF)。沿最小 forest 做 tree broadcast
达到同样的边集，因此在忽略容量、拥塞和 message startup 时该 bound tight。

一个简单的 per-edge “只要两侧都有 source 就免费”规则一般不 tight：多个需求
可能竞争同一侧的 source，最小 forest 仍需在若干候选边中选择一条。必须保留
(RF) 的全局 path-sharing 结构。

C 的免费初始 partial/output copies 同理，但 source 是 partial aggregate 的
集合，sink 也可能是多个输出节点；应把连接需求与 sinks 的 forest 单独定义，
不能把 A/B 的复制公式直接套过去。

## Recomputation：需求是 compute events

允许 recomputation 后，一个 product \(u=(i,k,j)\) 可以在多个叶子或多个时刻
计算。令

\[
\mathcal F(u)=\{(r,t):\text{owner }r\text{ 在时刻 }t\text{ 重新计算 }u\}
\]

是 compute-event 多重集合，要求每个 product 至少有一个 event。A/B 的需求
叶集合应从所有相关 events 取并集；C 则有更多 partial sources。对**固定的**
event assignment，RF/Steiner cut 仍然是合法的 memory-independent 下界。

但优化时不能把原始工作量 \(W=mkn\) 直接代入 phase/HBL：总 work 变成

\[
W'=\sum_u |\mathcal F(u)|\ge W.
\]

额外的 events 可能增加 HBL phase 项，却可能减少某条昂贵层次边上的 operand
通信；所以正确目标是对 event assignment、copy forest 和 phase trace 联合
优化，而不是声称 recomputation “保持同一个下界”。

## 当前可证明范围

- 单源、无重算：T3-Steiner 给出任意叶端调度的 tight memory-independent bound；
- 多源免费复制、无重算：RF 给出固定初始 source sets 的 tight
  memory-independent bound；
- 有重算：固定 event assignment 时可套用 RF/Steiner，允许选择 assignment
  的全局 tight theorem 仍未完成；
- 有限容量：上述 forest 还必须和 `finite-capacity-phase-cut-envelope.md`
  的 resident/reload trace 组合，不能把 forest cost 与 phase 项直接相加。

`experiments/check_free_replication_forest.py` 对一个小树穷举 source-demand
匹配，验证 RF 的最小路径并集与显式 broadcast schedule 一致。
