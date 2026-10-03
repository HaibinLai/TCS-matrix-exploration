# p=99 参数化证明线：已验证内容、缺口与下一步

## 已验证的 lemma

### Lemma 1：固定 active-line cover（已由 `prove_p99_envelope_stability.py` 证书化）

令 (u=1/q)、(u_0=1/997)，且 (q>99) 为素数。对 (p=99) 的三层模型

\[
P_1=2\cdot99\cdot q,
\qquad P_2=99q,
\qquad P_3=99,
\]

每个合法三维 processor grid 的 cost line 都可以从 (q_0=997) 的同一坐标因子分配中得到：把唯一的 (997) 因子替换为 (q)。因此每条 line 的系数是 (A+Bu)。

脚本对 (q_0) 上的全部 line 做了以下 exact 检查：对每条 candidate line，找到一条 (q_0)-active line 作为 dominator，并在

\[
u\in\{0,u_0\},
\qquad (z,y)\in\{(0,0),(1,0),(1,1)\}
\]

的所有组合上验证 candidate-minus-dominator 非负。差值对 ((z,y)) 与 (u) 都是 affine，因此这推出整个棱柱

\[
0\le u\le u_0,
\qquad 0\le y\le z\le1
\]

上的非负性。结果：

| envelope | 全部 lines | active cover |
|---|---:|---:|
| independent level 1 | 162 | 56 |
| independent level 2 | 54 | 24 |
| independent level 3 | 18 | 10 |
| nested | 162 | 51 |

所以对所有 prime (q\ge997)，不会出现新的 active line。这个 lemma 比有限 (q) 扫描强得多。

### Lemma 2：q0-visible candidate family 的符号检查（部分完成）

`check_p99_ratio_candidate_family.py` 从 (q_0) 的 active edge segments 构造 symbolic equality branches，得到：

* active segments：167；
* raw candidate intersections：2110；
* 在 (u_0) 落入 domain 的 candidate：1292；
* 经过 (q_0) 与 (q=100003) 两端 active-line 选择稳定性过滤：994；
* 与目标 ratio 比较时，endpoint sign failure：0；exact root-isolation sign failure：0。

目标点是 \((z,y)=(1,1/99))，其 exact 公式为

\[
I_*(q)=\frac{199q+2277}{6534q}
      =\frac{199+2277u}{6534},
\]
\[
N_*(q)=\frac{9q+7}{198q}
      =\frac{9+7u}{198},
\]
\[
R_*(q)=\frac{N_*}{I_*}
      =\frac{297q+231}{199q+2277}
      =\frac{297+231u}{199+2277u}.
\]

这还不是全局证明，因为 candidate family 的 edge topology 只从 (u=u_0) 观察得到，而且 line-choice 只在两个 (u) 端点测试过。

## 主要阻塞

1. **edge topology 事件尚未被 exact 排除。** 固定 active line 集合并不自动保证 active equality segments 的端点组合对所有 (u) 不变。潜在事件是三条 active lines 共点、pair equality 与 domain boundary 相切/平行、或两条 line 在某个 (u) 退化为同一条。
2. **994 个 symbolic branches 不是完整的参数化 overlay 证书。** 过滤条件只比较了 (u_0) 与一个很小的 (u=1/100003) 样本；某个 branch 可能在中间出现或切换 active owner。
3. **(u=0) 是退化端点。** 采样显示 (u=0) 的 edge counts 是 `(4,4,12,28)`，而任意 (u>0) 的样本是 `(60,29,12,51)`。因此不能把 (u=0) 当普通拓扑区间端点，需要单独处理极限值或取 (u\downarrow0)。

## 最短可执行的 exact proof 路线

### Step A：建立 topology-event sweep

对四个 fixed active envelopes，记 active line 为

\[
L_i(u,z,y)=a_i(u)+b_i(u)z+c_i(u)y,
\]

其中每个系数均为 affine in (u)。构造有限事件多项式：

1. 三线共点：
   \[
   \det\begin{pmatrix}
   a_i&b_i&c_i\\
   a_j&b_j&c_j\\
   a_k&b_k&c_k
   \end{pmatrix}=0.
   \]
2. pair equality 与三条 domain boundary 的交点退化：
   \[
   \det(E_{ij}(u),D_r)=0.
   \]
3. (E_{ij}(u)) 的三个系数同时为零（line identity 事件）以及 pair equality 的方向退化。

用 Sturm/root-isolation exact 求出所有事件根在 ((0,u_0)) 内的集合，按根排序；每两个相邻根之间取一个 rational sample，运行 `active_edge_segments` 并记录 pair keys。事件根本身单独验证。若没有 interior event，便可以正式证明 q0-visible topology 对所有 (u\in(0,u_0]) 都成立；若有事件，则把每个 interval 的 candidate family 并入后续检查。

这一步应优先利用坐标置换对称性，把 level-1/2/3 的 pair/triple 组合压缩，否则直接 SymPy 枚举所有三元组会较慢。最好使用小整数多项式算术而不是逐个调用通用符号 determinant。

一个快速的 Fraction 多项式原型已经给出规模估计：pair-domain 事件有 258 个唯一多项式（257 个一次式），三线 determinant 有 6356 个唯一多项式（5980 个一次式、375 个二次式）。落在 ((0,1/997)) 内的候选根分别为 11 和 205。逐一求交点并检查其是否位于 domain 且达到对应 envelope minimum 后，数值筛查得到 **0 个 actual active event**；一次式根已经用 Fraction 精确筛过。剩余工作是对 375 个二次式的代数根做 Sturm isolation 后，用 exact sign/feasibility 排除，而不是依赖浮点筛查。

诊断脚本已保存为 `work/scan_p99_topology_events.py`，可运行：

```text
PYTHONPATH=work python work/scan_p99_topology_events.py
```

它输出上述 line counts、事件多项式次数、候选根数量和 `actual events 0`。其中 `actual events 0` 对一次根是 exact Fraction 过滤；对二次根目前只是 `numpy.roots` 后的数值过滤，不能在论文中当作最终证明。

### Step B：将 ratio 证明写成有限 univariate sign certificates

对每个 topology interval：

1. 枚举 domain vertices、pair/domain intersections 和 edge-edge intersections；
2. 写出每个候选点的 (z(u),y(u))；
3. 在该候选点选择 interval 内实际 active 的 four-envelope owners，形成 (I(u))、(N(u))；
4. 验证
   \[
   R_*(u)I(u)-N(u)\ge0.
   \]

清除所有显然为正的分母后，这是一个一元多项式符号问题。用 Sturm intervals 在每个 topology interval 内检查根和端点即可。ratio 的线性分式事实保证：在固定 (u) 的每个 overlay cell 内，(N/I) 的最大值出现在 cell vertex，所以这个有限候选集足够。

目标点本身给出 equality；其余所有候选点应当严格正。

### Step C：处理 (u=0)

不要强行延拓 (u>0) 的 combinatorial topology。直接对 (u=0) 的退化 envelope 做一次 exact overlay，证明

\[
\lim_{u\downarrow0}R_*(u)=\frac{297}{199},
\]

且退化端点的 ratio 不超过该值。若所有 (u>0) branches 的 sign certificate 在极限保持非负，也可将 (u=0) 作为连续性 corollary。

## 预期结论与边界

完成 Step A--C 后，可以得到一个真正的 p=99 定理：

> 对所有素数 (q\ge997)，三层 p=99 模型的 global ratio 在 ((1,1/99)) 达到，值为 ((297q+231)/(199q+2277))。

这会把当前结果从“有限扫描 + candidate-family 证据”提升为“固定 p 的参数化 exact theorem”。它仍然不等于一般 (p) 或任意 (L\ge3) 的新紧下界；下一步才是把 event sweep 和 sign certificate 抽象到一般奇数 (p)。

## Audit correction

The earlier diagnostic counts in this report used an incorrect floor operation for terms of the
form $1/(d q)$. After replacing the anchor prime symbolically, the authoritative p=99 rerun is:

```text
quadratic_unique 1405 source_triples 11219
sturm_roots_open_interval 0 endpoint_polys 146
parallel_roots 0 active_pair_parallel_roots 0
active_linear_triple_events 0
```

The ratio wrapper still reports 994 positive-$u$ branches and zero exact sign failures. The older
258/6356/375 diagnostic figures are superseded historical estimates.
