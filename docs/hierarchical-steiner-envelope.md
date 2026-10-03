# 层次树上的 Steiner/copy-lineage envelope

一般 nested-partition 定理已经说明：非对称边成本下，矩形 grid 不能作为普适最优结构。更自然的对象是固定层次树上的 copy-lineage envelope。

## 层次树模型

把处理器层次抽象成一棵 rooted tree `H`。叶节点是最细计算 owner；内部节点是较粗的 owner group。每个层次边 `e` 有非负 word cost `w(e)`。对每个数据项，规定一个已有的 source owner；在源 owner 所在的子树内，可以把一个已有 copy 留在一个 child，其余需求 child 需要接收新 copy。这是与 SG-1 和静态 nested-partition 定理相同的 local-copy convention。

对一个 A-entry `a`，令 `R_A(a)` 是需要它的最细 owner leaves 集合；A/B 各自从一个 source owner 开始。对 B-entry 定义 `R_B(b)`。对 C-entry，`R_C(c)` 是产生 partial contribution 的 leaves，另有规定的 output sink `t_C(c)`；C 的子树必须连接所有这些 source leaves 与 sink。

## Copy-lineage 下界

令 `Tree_H(s,R)` 是连接 source `s` 和需求集合 `R` 的最小层次子树，并按 local-copy convention 去掉无需传输的 source-to-retained-child 边。对 C，`Tree_H(R,t)` 表示连接多个 source leaves 与 sink `t` 的最小子树。定义

$$
\operatorname{cost}_H(s,R)=
\sum_{e\in Tree_H(s,R)} w(e),
\qquad
\operatorname{cost}_H(R,t)=
\sum_{e\in Tree_H(R,t)} w(e).
$$

在一次产品计算、无 recomputation、单份初始输入和单份最终输出的模型中，任意执行满足

$$
Q_{\rm weighted}\ge
\sum_{a\in A}\operatorname{cost}_H(s_A(a),R_A(a))
+
\sum_{b\in B}\operatorname{cost}_H(s_B(b),R_B(b))
+
\sum_{c\in C}\operatorname{cost}_H(R_C(c),t_C(c)).
\tag{STEINER-LB}
$$

证明是 cut counting：对 `Tree_H(s,R)` 的每一条边，删除该边后需求集合仍有节点在两侧；至少有一个对应 word 或 partial aggregate 穿过该边。不同数据项的 word volume 可以逐项相加。

## Tightness

如果通信拓扑允许沿 `H` 的 spanning tree 做逐项 broadcast 和 reduction，并且暂时忽略链路拥塞与 message startup，那么对每个数据项沿其最小子树广播或归约即可达到 `STEINER-LB`。因此该 envelope 在这个固定层次树的 word-volume 模型中是 tight 的。

这比矩形 grid envelope 更一般：它只要求知道每个数据项的需求 leaves，不要求需求集合是笛卡尔块。

## 嵌套分区公式是特例

若需求 leaves 由 nested partitions
\[
\Pi_1\preceq\Pi_2\preceq\Pi_3\preceq\Pi_4=\{T\}
\]
诱导，并且每个粗 part 为每个投影 incidence 保留一个 copy，则一条层次边上的 Steiner cost 展开为

$$
\Delta_\ell^A=X_A(\Pi_\ell)-X_A(\Pi_{\ell+1}),
$$

$$
\Delta_\ell^B=X_B(\Pi_\ell)-X_B(\Pi_{\ell+1}),
\qquad
\Delta_\ell^C=X_C(\Pi_\ell)-X_C(\Pi_{\ell+1}).
$$

因此 `NP-vector` 是 `STEINER-LB` 的分层写法。若每层边权相同，所有增量 telescopes；若边权不同，具体的 intermediate partition 和 owner tree 会改变最优成本。

## 研究边界

这个 envelope 仍然不包含 finite-memory phase constraint。phase/HBL 限制的是一个 owner 在一次装入窗口内能完成多少 products；Steiner envelope 限制的是这些 products 的数据依赖跨层传播。对一般 machine model，最终目标应是把两者用不重复 charging 组合起来，而不是未经证明直接相加。

它也不自动处理：

- free initial replication；
- recomputation；
- dynamic owner migration；
- message count、同步和链路拥塞；
- SYRK/SYMM 共享输入和对称输出的额外依赖。

因此下一步是：先在固定层次树上验证 `STEINER-LB` 的 cut proof 与 nested-partition 实现，再研究动态 migration 是否能低于固定树 envelope。
