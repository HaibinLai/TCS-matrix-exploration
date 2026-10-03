# 三层任意叶端调度的 Steiner 下界

## 结论先行

静态 `nested grid` 定理可以在不要求单一矩形 chain 的条件下推广一层：
固定三层处理器树以后，任意一次 classical GEMM 调度（每个
scalar product 只算一次）都会为每个数据项付出其需求叶集合与数据源之间
的最小树连接代价。这个结论允许产品在执行期间改变 owner，也允许不同的
产品使用不同的叶子；它只暂时忽略有限 local memory、链路拥塞和 message
startup。

因此，当前可以严格区分两个问题：

1. **无容量的多级 word-volume 定理**：下面的 Steiner/cut 定理已经闭合且
   有 matching broadcast/reduction schedule；
2. **有限容量的多级定理**：还必须把 phase/HBL 的 reload 约束接到同一棵
   time-expanded 树上，不能把两个下界未经 charging 直接相加。

## 模型

令

\[
T=[m]\times[k]\times[n]
\]

是 classical GEMM 的 product 集合。每个
\(u=(i,k,j)\in T\) 计算

\[
a_{ik}b_{kj}
\]

并把结果贡献给 \(c_{ij}\)。三层通信拓扑是 rooted tree \(H\)：根是慢层
或公共源，内部节点是粗粒度 owner group，叶子是最细计算 owner。每条边
\(e\) 的 word 成本为 \(w_e\ge0\)。一条 word 穿过多条边时，在每条实际边
上分别计费。

对一条执行，定义：

- \(R_A(a)\)：使用 A-entry \(a\) 的叶子集合；
- \(R_B(b)\)：使用 B-entry \(b\) 的叶子集合；
- \(R_C(c)\)：产生 \(c\) 的 partial contribution 的叶子集合；
- \(s_A(a),s_B(b)\)：输入源节点；
- \(t_C(c)\)：最终输出节点。

这里的需求集合是整个执行期间的并集，所以 owner 可以动态迁移。假设：

1. 每个 product 恰好计算一次；
2. A、B 初始各只有一个付费副本；
3. C 的每个 partial 只能由其对应 product 产生，最终输出只保留一个
   aggregate；
4. 数据可以沿树边转发，partial 可以在树上归约；
5. 暂不限制 local memory，也不计 message 数、同步和拥塞。

## 树上的 cut 数

对树边 \(e\) 按根到叶方向定向，记删去 \(e\) 后的 child-side 子树为
\(D_e\)。定义

\[
\chi_e(s,R)=
\mathbf 1\!\left[
\mathbf 1[s\in D_e]
\ne
\mathbf 1[R\cap D_e\ne\varnothing]
\right].
\]

对 C，\(\chi_e(R,t)\) 定义为删边后 \(R\) 和 \(t\) 分处两侧时为 1，
否则为 0。它正好表示一棵树上把所有 source leaves 连接到 output sink
时是否必须穿过该边。

## 定理 T3-Steiner

在上述模型中，任意执行的加权通信量满足

\[
\boxed{
Q_w\;\ge\;
\sum_{a\in A}\sum_{e\in E(H)}w_e\chi_e(s_A(a),R_A(a))
+\sum_{b\in B}\sum_{e\in E(H)}w_e\chi_e(s_B(b),R_B(b))
+\sum_{c\in C}\sum_{e\in E(H)}w_e\chi_e(R_C(c),t_C(c)).
}
\tag{T3-S}
\]

等价地，每个 A/B entry 的项是连接其 source 与需求叶子的最小层次子树
成本；每个 C-entry 的项是连接所有 partial source 与 output sink 的最小
层次子树成本。

### 证明

先固定一个 A-entry \(a\) 和一条边 \(e\)。若
\(\chi_e(s_A(a),R_A(a))=1\)，则 source 与需求集合在删边后的两侧；
执行第一次在 source 对侧使用 \(a\) 以前，至少有一个代表该 entry 的 word
穿过 \(e\)。同一 word 可以在该侧子树内复制并服务多个叶子，但不能让完全
没有穿过 cut 的数据出现在 cut 的另一侧。因此该 entry 对这条边至少贡献
一个 word。

B-entry 完全相同。对 C-entry，若 \(\chi_e(R_C(c),t_C(c))=1\)，partial
贡献的 source 和 output sink 位于 cut 两侧；无论 partial 在哪一侧先归约，
最终 aggregate 至少要有一个 word 穿过 \(e\)。

最后，对所有数据项和所有边求和。一次传输只对应某个具体 data item 或
partial aggregate 的一次跨边事件，逐项计数不会低估实际 aggregate volume，
得到 (T3-S)。\(\square\)

### Tightness

对每个 A/B-entry，在其 source 与需求叶子的最小子树上做一次 tree broadcast；
对每个 C-entry，在连接 partial sources 与 output sink 的最小子树上做一次
tree reduction。树边上每个 data item 恰好发送一次，当且仅当对应的 cut
indicator 为 1。因此在允许逐项树转发、忽略拥塞和 message startup 的模型中，

\[
Q_w=\text{右侧的 (T3-S)}.
\]

不同 data item 的 broadcast/reduction 可以按任意拓扑序交错，故 owner 标签
是否随时间改变不会破坏 tightness；它只改变需求叶集合 \(R_A,R_B,R_C\)。

## 与 nested-partition 定理的关系

若每个内部节点的叶子集合形成嵌套分区

\[
\Pi_1\preceq\Pi_2\preceq\Pi_3\preceq\Pi_4=\{T\},
\]

并规定粗 part 保留一个 local copy，则同一条层次边上的 cut indicator
总和等于投影 incidence 增量：

\[
\Delta_\ell^A=X_A(\Pi_\ell)-X_A(\Pi_{\ell+1}),
\quad
\Delta_\ell^B=X_B(\Pi_\ell)-X_B(\Pi_{\ell+1}),
\quad
\Delta_\ell^C=X_C(\Pi_\ell)-X_C(\Pi_{\ell+1}).
\]

所以 `NP-vector` 和 `T3-static-vector` 是 (T3-S) 的分层、笛卡尔特例。
反过来，(T3-S) 不要求需求集合是块，也不要求一个执行存在唯一的
componentwise-divisible grid chain。这正是它可以覆盖动态 owner 的原因。

对矩形 grid \(g_\ell=(a_\ell,b_\ell,c_\ell)\)，它恢复

\[
\Delta_\ell^A=(c_\ell-c_{\ell+1})mk,\quad
\Delta_\ell^B=(a_\ell-a_{\ell+1})kn,\quad
\Delta_\ell^C=(b_\ell-b_{\ell+1})mn.
\]

单层时再除以叶子数 \(P=abc\)，得到

\[
\frac{mk}{ab}+\frac{kn}{bc}+\frac{mn}{ac}
-\frac{mk+kn+mn}{P},
\]

即 static-grid ownership 下界的 aggregate-to-per-owner 形式。

## 这个定理没有偷偷解决的部分

T3-Steiner 是一个完整的 arbitrary-schedule **memory-independent** theorem，
但不是最终的 finite-memory multilevel theorem。它没有给出：

- 每个叶子的容量受限时 phase reload 的精确额外费用；
- owner-copy cut 项与 HBL phase 项的可加性；
- free initial replication 或 recomputation 下的最优 Pareto frontier；
- message count、latency、拥塞或关键路径下界；
- SYRK/SYMM 的对称投影集合。

因此下一步的严格目标不是再枚举 factor arrangement，而是定义一个
time-expanded phase trace，证明其 projection/cut 约束，并寻找同时达到该约束
的调度。如果 phase trace 不能保留逐边树结构，最终 theorem 应报告一个联合
envelope 或显式 overlap correction，而不能把 T3-S 与标准 HBL 项直接相加。
