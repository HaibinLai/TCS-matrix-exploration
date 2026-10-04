# 三层 nested classical GEMM：主定理、证明与扩展边界

这份文件把当前项目的核心结果收束成一个正式的 theorem。它证明的是一个
**静态、owner-consistent、一次计算每个 product 的三层模型**；它不是对任意
动态 GEMM、有限容量 reload 或 recomputation 的普适定理。这样限定后，lower
bound 和 matching schedule 使用完全相同的计费规则，可以严格称为 tight。

## 1. 固定模型和计费方式

计算矩形 classical GEMM

\[
A\in\mathbb F^{m\times k},\qquad
B\in\mathbb F^{k\times n},\qquad
C=AB\in\mathbb F^{m\times n}.
\]

每个 scalar product 用三元组

\[
u=(i,q,j)\in T=[m]\times[k]\times[n]
\]

表示。它使用
\(a_{iq}\)、\(b_{qj}\)，并贡献一个 \(c_{ij}\) partial。

### 三层 hierarchy

从细到粗写四个 nested partitions：

\[
\Pi_1\preceq\Pi_2\preceq\Pi_3\preceq\Pi_4=\{T\}.
\]

\(\Pi_1\) 是 fine product owners，\(\Pi_2\) 是中间层，\(\Pi_3\) 是
最粗处理层，\(\Pi_4\) 是 root/source/output。每个 fine part 完全包含在
一个中间 part 中，每个中间 part 完全包含在一个粗 part 中；这就是
owner-consistent nested chain。

对 \(S\subseteq T\)，定义三种投影：

\[
\pi_A(S)=\{(i,q):(i,q,j)\in S\},\quad
\pi_B(S)=\{(q,j):(i,q,j)\in S\},
\]

\[
\pi_C(S)=\{(i,j):(i,q,j)\in S\}.
\]

定义 partition projection sums：

\[
X_A(\Pi)=\sum_{S\in\Pi}|\pi_A(S)|,\quad
X_B(\Pi)=\sum_{S\in\Pi}|\pi_B(S)|,
\]

\[
X_C(\Pi)=\sum_{S\in\Pi}|\pi_C(S)|.
\]

它们是 incidence 数：同一个矩阵 entry 在不同 owner parts 中出现多次，
每次出现都算一个 owner-side copy 或 partial incidence。

### 静态计费假设

1. 每个 \(u\in T\) 恰好计算一次，并由 \(\Pi_1\) 的 owner 负责。
2. A、B 在 root 各只有一个初始 source copy；C 在 root 最终只有一个
   output copy。
3. 在 edge \(E_\ell\) 上，粗侧已有
   \(X_A(\Pi_{\ell+1})\)、\(X_B(\Pi_{\ell+1})\) 个对应 incidence，
   且这些 copies 位于该 edge 的 parent side；child side 不允许有免费的
   retained copy。
4. C 的每个 fine incidence 是一个 partial。沿 edge 向上，partial 可以在
   child 或 parent 节点相加；每个跨 edge word movement 只减少一个尚未归并的
   partial incidence。
5. 一次 movement 传输一个 word；同一个 word 经过两条 edge 时在两条 edge
   上分别计费。只研究 word volume，不计 message startup、同步、拥塞和容量
   eviction。
6. 不允许 recomputation、压缩、编码替代或执行期间改变 partition chain。
7. 每个相邻层的 owner groups 之间可以使用任意 spanning tree；因此证明的是
   hierarchy-edge volume，而不是某个具体环或 torus 的 hop count。

记 \(V_\ell^A,V_\ell^B,V_\ell^C\) 为 edge
\(E_\ell:\Pi_{\ell+1}\to\Pi_\ell\) 上三类 word volume，\(V_\ell\) 为三者
之和。

## 2. 三层 nested lower-bound theorem

### 定理（T3-Nested-Incidence）

在上述模型中，对 \(\ell=1,2,3\)，任意执行满足

\[
\boxed{
V_\ell^A\ge X_A(\Pi_\ell)-X_A(\Pi_{\ell+1}),
}
\tag{T3-A}
\]

\[
\boxed{
V_\ell^B\ge X_B(\Pi_\ell)-X_B(\Pi_{\ell+1}),
}
\tag{T3-B}
\]

\[
\boxed{
V_\ell^C\ge X_C(\Pi_\ell)-X_C(\Pi_{\ell+1}).
}
\tag{T3-C}
\]

所以

\[
\boxed{
V_\ell\ge
\Delta_\ell^A+\Delta_\ell^B+\Delta_\ell^C,
}
\qquad
\Delta_\ell^X=X_X(\Pi_\ell)-X_X(\Pi_{\ell+1}).
\tag{T3-V}
\]

对任意非负的类型/层级 edge weights
\(\alpha_{\ell,A},\alpha_{\ell,B},\beta_{\ell,C}\)，也有

\[
\boxed{
Q_w\ge\sum_{\ell=1}^3
\left(
\alpha_{\ell,A}\Delta_\ell^A
+\alpha_{\ell,B}\Delta_\ell^B
+\beta_{\ell,C}\Delta_\ell^C
\right).
}
\tag{T3-weighted}
\]

### 证明

固定一个 A-entry \(a\)。它在 \(\Pi_{\ell+1}\) 中出现
\(d_c\) 次，在 \(\Pi_\ell\) 中出现 \(d_f\) 次，其中
\(d_f\ge d_c\)。每个 fine incidence 必须在其 owner part 中可用；parent
side 已经只有 \(d_c\) 个 copies，因此至少要在 edge 上创建
\(d_f-d_c\) 个新 copy。对所有 A-entry 求和：

\[
\sum_a(d_f(a)-d_c(a))
=X_A(\Pi_\ell)-X_A(\Pi_{\ell+1}).
\]

B-entry 完全相同，得到 (T3-B)。

再固定一个 C-entry \(c_{ij}\)。在 child side 有 \(d_f\) 个来自不同
fine parts 的 partial，在 parent side 最多保留 \(d_c\) 个 aggregate partial。
一个跨 edge movement 至多把两个当前 aggregate 合并成一个，因此至少需要
\(d_f-d_c\) 次 movement。对所有 \(c_{ij}\) 求和得到 (T3-C)。

三类 word 是不同的 data object；按类型计费后加权求和即得
(T3-weighted)。证毕。

这个证明的关键不是 processor-grid 的整除性，而是“parent side 的已有
incidence”和“child side 的新增 incidence”这两个静态计费条件。若 child side
允许免费 retained copies，差值就不再是通信下界；若允许 recomputation，
product event 集合也不再是固定的 \(\Pi_1\)。

## 3. 恢复已知的一层结果

把只有一个计算层的 block grid 写成

\[
g=(a,b,c),\qquad abc=P,
\]

并令 root partition 为 \(\Pi_2=\{T\}\)。对标准三维 block ownership：

\[
X_A(\Pi_1)=c\,mk,\qquad
X_B(\Pi_1)=a\,kn,\qquad
X_C(\Pi_1)=b\,mn,
\]

而 root 的三个 projection sums 是 \(mk,kn,mn\)。因此主定理退化为

\[
\boxed{
V\ge(c-1)mk+(a-1)kn+(b-1)mn.
}
\tag{1-level-volume}
\]

这是该静态 owner 模型的 memory-independent one-level result。若
\(a=b=c=P^{1/3}\) 且 \(m=n=k=N\)，aggregate volume 为

\[
3N^2(P^{1/3}-1),
\]

平均到 \(P\) 个 owners 是

\[
\Theta\!\left(\frac{N^2}{P^{2/3}}\right)
\]

（另有输入/输出边界项）。这和三维 broadcast/reduction 的通信阶一致。

它与经典两级存储的 phase/HBL 结果是互补的，而不是同一个 bound。容量为
\(M\) 的 fast memory 中，一个 phase 的 A/B/C projection 总量至多为
\(O(M)\)，Loomis--Whitney 给出每 phase 至多 \(O(M^{3/2})\) 个 products，
所以在标准 large-work/balanced phase regime（边界项单独计费）可写成

\[
Q_{\mathrm{seq}}=\Omega\!\left(\frac{mkn}{\sqrt M}\right)
\quad\text{and}\quad
Q_{\mathrm{seq}}=\Omega(mk+kn+mn).
\tag{1-level-phase}
\]

两项在同一模型中只能取经证明的最大值；若要写成加和，必须额外证明
输入/输出扫描与 phase reload 事件不重叠。对极端长宽比或容量边界，应使用
HBL 的精确 projection envelope，而不能机械地把两项相加。

这里的 \(N^2/P^{2/3}\) 是静态并行 owner/copy 计数，
\(mkn/\sqrt M\) 是容量 phase 计数；不能在没有 overlap lemma 时直接相加。

## 4. 三层矩形 grid 特例与 tightness

若每个 partition 来自 componentwise-coarsened block grid
\(g_1=(a_1,b_1,c_1)\succeq g_2\succeq g_3\)，令
\(g_4=(1,1,1)\)。则

\[
\Delta_\ell^A=(c_\ell-c_{\ell+1})mk,
\quad
\Delta_\ell^B=(a_\ell-a_{\ell+1})kn,
\quad
\Delta_\ell^C=(b_\ell-b_{\ell+1})mn.
\]

于是

\[
V_\ell\ge
(c_\ell-c_{\ell+1})mk
+(a_\ell-a_{\ell+1})kn
+(b_\ell-b_{\ell+1})mn.
\tag{grid-T3}
\]

### Matching schedule

对每一个 edge、每一个 data entry：

1. A 的每个 parent-side copy 在需要它的 child incidences 上建立一棵
   broadcast tree，发送恰好新增的 child copies；
2. B 同样 broadcast；
3. C 的 fine partial 沿 child-to-parent tree 做 reduction，直到只留下
   parent partition 所需的 partial incidences；
4. 三类 movement 可以按任意顺序流式执行，且不需要额外的跨 edge word。

因此每个 edge 都恰好使用
\(\Delta_\ell^A+\Delta_\ell^B+\Delta_\ell^C\) 个 words，任意非负权下
同时达到 (T3-weighted)。这证明了固定 nested chain 的 tightness；对 chain
再取最小值得到该静态模型的 weighted optimum。

注意：row--\(k\)-block 的另一种 fresh-arrival 口径会得到
\(mk+Hkn+mn\) 和 \(mk+Hkn+Smn\) 之类的式子。它把每一级第一份 arrival
也收费，见 `docs/three-level-row-k-block-gemm-theorem.md`；不能和本节的
retained-copy increment 直接相加。

## 5. 五类扩展的状态

### 任意 \(L\) 层

把 chain 延长为
\(\Pi_1\preceq\cdots\preceq\Pi_L\preceq\Pi_{L+1}=\{T\}\)，同一个 incidence
证明逐 edge 成立：

\[
V_\ell^X\ge X_X(\Pi_\ell)-X_X(\Pi_{\ell+1}),
\qquad 1\le\ell\le L.
\]

`docs/l-level-static-extension.md` 记录了矩形 grid 和非对称 edge cost 的
推论；`docs/l-level-row-k-block-gemm-theorem.md` 则是 fresh-arrival 的
rectangular 版本。

### Rectangular GEMM

主定理从一开始就对 \(m\times k\) 乘 \(k\times n\) 成立；square case 只是
\(m=k=n\) 的特例。row partition 与 k/reduction partition 的显式 tight
schedule 见 `docs/three-level-row-k-block-gemm-theorem.md`。

### Asymmetric read/write costs

若 A/B 的 downlink read、C 的 uplink write 具有方向相关成本，只需为每种
movement 使用对应的非负权。更一般地，把一次 movement 标为
\((X,\mathrm{dir})\)，则

\[
Q=\sum_{\ell,X,\mathrm{dir}}
\alpha_{\ell,X,\mathrm{dir}}V_{\ell,X,\mathrm{dir}}
\]

而上述逐 incidence 计数分别给出每个 \(V\) 的下界。匹配 schedule 仍然 tight，
前提是成本只依赖 edge/type/direction，不依赖拥塞或消息大小。

### Replication 和 recomputation

免费初始 replication 不能直接使用单源差值；固定 source sets 时应改用
multi-source Steiner forest。允许 recomputation 后，一个 product 可能有多个
compute events，需用 event-aware finite-capacity envelope；固定 event
assignment 可以套 Steiner lower bound，但对 event assignment 的全局优化仍未
完成。见 `docs/replication-recomputation-boundaries.md`、
`docs/recomputation-event-tradeoff.md` 和
`docs/finite-capacity-phase-cut-envelope.md`。

### SYRK/SYMM 等结构化 kernel

对 SYRK、SYR2K、SYMM，\(C\) 的独立 entries、A/B 的对称 alias 和 partial
incidences 都会改变；不能把 GEMM 的 \(X_A,X_B,X_C\) 公式原样套用。2024 年
已有工作覆盖若干 sequential/distributed symmetric kernels，因此本项目当前
不把“首次证明这些 kernel 的通信下界”作为贡献。合理的超出方向是：在同一
多层 rooted hierarchy 上定义 symmetry-aware projection/forest，并比较它与
2024 结果在多层嵌套和非对称 edge cost 下的差异。

## 6. 结论和真正的研究缺口

当前可以严格声称：

> 在静态、单源、一次 product 计算、owner-consistent nested partitions、
> word-volume 计费的三层 classical GEMM 模型中，逐 edge 的 projection-incidence
> difference 是通信下界；在允许树形 broadcast/reduction 的同一拓扑模型中，
> 该下界对任意非负 edge/type 权重都可达到。

这已经是一个真正的多级通信定理，但范围是静态模型。尚未完成的更强目标是：

- 任意动态 ownership 是否可 time-expand 成同一类 nested demand，而不重复计费；
- 有限容量 phase/HBL 与 projection/cut 项的联合 tightness；
- replication、recomputation 和拥塞的联合优化；
- symmetry-aware kernels 的多层 tight schedule。

所以因子结构、25-line arrangement 和自动 Farkas 证书应继续作为验证工具，而
不是主定理本身。
