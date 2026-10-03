# 有限容量下的联合 phase/cut envelope

## 目的

固定层次树上的 T3-Steiner 定理处理 memory-independent word volume；经典
HBL/phase 引理处理一个 owner 在容量 \(M\) 下的 reload traffic。两者都
可能把同一个首次加载事件算进去，所以不能把两个标量下界未经证明直接相加。

本文件给出一个可用于三层 GEMM 的联合可行域。它把边级到达事件、每个 phase
的 product set、resident set、local load set 和 cut 事件显式写出。任何真实
执行都映射到该可行域，因此其最小通信量是合法的 lower-bound envelope；若
后续构造 schedule 达到该最小值，才得到 tightness。

## 单条层次边的 trace

固定一条从 parent 到 child hierarchy group 的收费边 \(e\)。child 侧有
owners \(r\in R_e\)。边级多重集合 \(X_{e,t}\) 表示第 \(t\) 个边级时间
窗口真正穿过 \(e\) 的 arrivals，\(|X_{e,t}|\) 按传输次数计费。同一 entry
在 child group 内被多个 owner 复用时，只需在 \(X_{e,t}\) 中出现一次；若
child group 没有共享 cache，可以把每个 owner 的窗口分开，此时 \(X\) 退化
为 local load sets 的不交并。写 \(\operatorname{supp}(X_{e,t})\) 表示
多重集合的 entry support。

对 owner \(r\)，把执行切成 phases \(t=1,\ldots,T_r\)。定义：

- \(F_{r,t}\subseteq [m]\times[k]\times[n]\)：该 phase 完成的 products；
- \(U_{r,t}=\pi_A(F_{r,t})\cup\pi_B(F_{r,t})\cup\pi_C(F_{r,t})\)：
  phase 需要出现的 data entries；
- \(K_{r,t}\)：phase 开始时 owner-local resident entries；
- \(L_{r,t}=U_{r,t}\setminus K_{r,t}\)：该 phase 的 local missing entries；
- \(G_t\)：边 \(e\) 的 child-side shared cache（没有共享 cache 时取空集）。

在单份初始输入模型中取 \(K_{r,1}=G_1=\varnothing\)；允许非空初始状态只会
把该 envelope 放宽到 free-initial-replication 模型。

trace 必须满足

\[
F_{r,t}\cap F_{r,t'}=\varnothing\quad(t\ne t'),
\qquad
\bigcup_{r,t}F_{r,t}=T,
\tag{TR-1}
\]

\[
|K_{r,t}|\le M_r,
\qquad
K_{r,t+1}\subseteq K_{r,t}\cup U_{r,t},
\qquad
|K_{r,t+1}|\le M_r,
\tag{TR-2}
\]

\[
G_{t+1}\subseteq G_t\cup\operatorname{supp}(X_{e,t}),
\qquad
|G_t|\le M_e^{\rm group},
\tag{TR-3}
\]

以及每个 phase 的 HBL 投影约束

\[
|F_{r,t}|
\le
\sqrt{|\pi_A(F_{r,t})|\,|\pi_B(F_{r,t})|\,|\pi_C(F_{r,t})|}.
\tag{TR-4}
\]

每个 local missing entry 必须来自 shared cache 或边级到达：

\[
L_{r,t}\subseteq G_t\cup\operatorname{supp}(X_{e,t}).
\tag{TR-5}
\]

若采用 owner-private 的标准 \(M_r\)-transfer phase 切分，还要求

\[
|L_{r,t}|\le M_r.
\tag{TR-6}
\]

对每个 entry \(d\)，设 \(b_e(d)\) 是 T3-Steiner cut indicator：当 \(d\)
的唯一 source 在 parent 侧而 child 侧某个 owner 需要它时，\(b_e(d)=1\)。
copy-creation 约束为

\[
\sum_t\mathbf 1[d\in\operatorname{supp}(X_{e,t})]\ge b_e(d).
\tag{TR-7}
\]

C 的 partial reduction 另加 \(\rho_e(c)\) 事件，要求每个被 cut 分开的
source/sink 至少有一个 aggregate crossing \(e\)。

## 联合 envelope

令 \(\mathfrak T_e(M_e)\) 是满足 \(TR\text{-}1\)--\(TR\text{-}7\) 以及
C-reduction 约束的所有 phase traces。定义

\[
\mathcal E_e(M_e)=
\inf_{\mathcal T\in\mathfrak T_e(M_e)}
\left[
\sum_t|X_{e,t}|
+\sum_{c\in C}\rho_e(c)
\right].
\tag{E-TRACE}
\]

目标函数只统计真正跨过边 \(e\) 的 arrivals，因而不会把一次
parent→group 传输重复算成多个 leaf loads。local phase constraints 仍会限制
\(X\) 能否提供足够的复用；这正是共享 cache 下尚需求解的耦合部分。

### 联合下界定理

在一次产品计算、计费复制、无 recomputation 的模型中，任意真实执行诱导一条
合法 trace，因此

\[
\boxed{V_e\ge \mathcal E_e(M_e).}
\tag{E-LB}
\]

证明是 trace projection：把真实执行每个 phase 的 products、local resident
entries、shared-cache state、边级 arrivals、首次/重复加载和 partial
reduction 记录下来，即得到 \(TR\text{-}1\)--\(TR\text{-}7\)；真实跨边传输
数不小于目标函数。\(\square\)

这个定理的价值在于：ownership 与 phase 是同一个可行域中的事件，而不是两个
需要事后相加的数字。它适用于任意叶端 product assignment，不要求矩形 grid
chain。若容量趋于无限且每个 owner 只需一个边级 arrival，\(X\) 只剩首次
到达事件，\(E\text{-}TRACE\) 退化为 T3-Steiner 的 copy-lineage 计数。

## 两个可立即推出的弱化下界

### Cut 项

从 \(TR\text{-}7\) 直接得到

\[
\mathcal E_e(M_e)
\ge B_e,
\qquad
B_e=\sum_d b_e(d)+\sum_c\rho_e(c).
\tag{E-CUT}
\]

这正是 memory-independent Steiner boundary，适用于 shared-cache 和
owner-private 两种情况。

### Owner-private phase/HBL 项

若边的 child owners 没有共享 cache，且每个 owner \(r\) 完成 \(W_r\) 个
products、容量为 \(M_r\)，由 \(TR\text{-}2\)、\(TR\text{-}4\) 和
Loomis--Whitney/HBL，单个 phase 至多完成

\[
f(M_r)=\left(\frac{2M_r}{3}\right)^{3/2}
\]

个 products。标准 full-phase 计数给出 owner-private 特例

\[
V_e\ge
\sum_{r\in R_e}
\left(
 f(M_r)^{-1}W_r-1
\right)_+M_r,
\tag{E-PHASE-private}
\]

或在均匀容量 \(M_r=M\) 时

\[
V_e\ge
\left(
 f(M)^{-1}\sum_r W_r-|R_e|
\right)_+M.
\]

共享 cache 时不能把这个式子直接套到每个 leaf 再求和；共享 arrivals 必须
通过 \(E\text{-}TRACE\) 的 \(X_{e,t}\) 和 \(G_t\) 共同优化。这是当前真正
的 finite-capacity multilevel gap。

## 为什么不能直接相加

取一个抽象但合法的 owner-private phase 事件记录：\(M=6\)，每个 phase 的
HBL work 上限取 \(f=8\)，总 work \(W=27\)，首次到达事件数 \(B=6\)。
一个标准 full-phase trace 可以有 4 个 phases、总 load volume \(Q=18\)；
连续 HBL 式给出 \(Q_{\rm phase}=6(27/8-1)=57/4\)。于是

\[
\max\{B,Q_{\rm phase}\}=57/4<18,
\qquad
B+Q_{\rm phase}=81/4>18.
\]

同一批首 phase loads 同时属于 cut 的首次到达和 phase 预算。这个算术例子
不是 GEMM 算法的 tightness 声明；它证明了在没有额外不相交事件定义时，
“owner bound + phase bound”不是一个普遍有效的 lower bound。

## 下一步的可证伪目标

1. 在 \(2\times2\times2\) 和 \(3\times3\times3\) GEMM 上枚举合法小 trace，
   计算 \(E\text{-TRACE}\) 的整数最优值；
2. 比较它与 \(\max(E\text{-CUT},E\text{-PHASE-private})\) 的差距，判断
   是否存在非平凡 overlap correction；
3. 对标准 blocked/SUMMA schedule 记录同一 trace，测试何时达到
   \(E\text{-TRACE}\)；
4. 若某个阶段需要 child 内共享 cache，扩展 \(G_t\) 的 copy-lineage 状态，
   而不是把每个 leaf 的 reload 简单相加；
5. 在此基础上再定义 \(L\)-level、非对称 \(M_\ell\) 和 weighted-edge
   版本。

在完成第 1--3 步以前，不把 \(E\text{-TRACE}\) 简化成一个新的闭式常数，也不
声称有限容量下已经得到三层 tight theorem。

## 共享 child cache 的显式 HBL 弱化下界

虽然一般的 \(E\text{-TRACE}\) 仍需要求解，但可以先得到一个不重复计费的显式
弱化。取一个边级 phase budget \(B>0\)，把执行切成除最后一个 phase 外每个
phase 恰好发生 \(B\) 次 arrival 的窗口。设 child group shared cache 容量为
\(M_g\)，owner \(r\) 的 local capacity 为 \(M_r\)。在任一窗口中，owner
\(r\) 能看到的三类 entries 来自 phase 开始时的 local state、shared cache
和本窗口的边 arrivals。因此在把输出 materialization/eviction 也计入 edge
事件的模型中，

\[
|\pi_A(F_{r,t})|+|\pi_B(F_{r,t})|+|\pi_C(F_{r,t})|
\le M_r+M_g+B.
\tag{SC-1}
\]

这是一个放宽式约束：同一批 \(B\) arrivals 可以被所有 owners 免费复用。由
HBL 与 AM--GM，窗口内 owner \(r\) 至多完成

\[
\varphi_r(B)=\left(\frac{M_r+M_g+B}{3}\right)^{3/2}
\]

个 products，所有 owners 的总 work 至多为

\[
\Phi(B)=\sum_{r\in R_e}\varphi_r(B).
\tag{SC-2}
\]

若 child group 总共负责 \(W_e=\sum_r W_r\) 个 products，phase 数至少为
\(W_e/\Phi(B)\)。除最后一个 phase 外每个 phase 有 \(B\) 次 edge arrivals，
所以得到

\[
V_e\ge
B\left(\frac{W_e}{\Phi(B)}-1\right)_+.
\tag{SC-3}
\]

对任意 \(B>0\) 都成立，因此可与 cut 项取最大值：

\[
\boxed{
V_e\ge
\max\left\{
B_e,\,
\sup_{B>0}B\left(\frac{W_e}{\Phi(B)}-1\right)_+
\right\}.
}
\tag{SC-HBL}
\]

当 \(R_e=1\)、\(M_g=0\)、\(M_r=M\)、\(B=M\) 时，\(SC\text{-}3\) 退化为
标准 one-owner phase 的量纲
\[
M\left(\frac{W}{(2M/3)^{3/2}}-1\right).
\]
当 \(M_g>0\) 或多个 owners 共享 arrivals 时，\(SC\text{-}HBL\) 明确反映了
shared cache 的复用，但通常不是 tight；它只是 \(E\text{-TRACE}\) 的一个可
计算 lower bound。

### 均匀 owner 时的 phase-budget 优化引理

若所有 child owners 都有相同容量 \(M_r=M\)，共有 \(R\) 个 owners，令
\(A=M+M_g\)，并定义

\[
D=\frac{3\sqrt 3\,W_e}{R}.
\]

则 \(SC\text{-}2\) 给出

\[
\Phi(B)=\frac{R}{3\sqrt 3}(A+B)^{3/2},
\]

从而 phase 项化为

\[
H(B)=B\left(\frac{D}{(A+B)^{3/2}}-1\right)_+.
\tag{SC-H}
\]

如果 \(D\le A^{3/2}\)，则 \(\sup_{B>0}H(B)=0\)。如果
\(D>A^{3/2}\)，正区间内的唯一最大点 \(B^\star\) 满足

\[
D\left(A-\frac{B^\star}{2}\right)
=(A+B^\star)^{5/2},
\tag{SC-root}
\]

且

\[
0<B^\star<\min\{2A,D^{2/3}-A\}.
\]

证明：在 \(H(B)>0\) 的区间，

\[
H'(B)=D\left(A-\frac B2\right)(A+B)^{-5/2}-1,
\]

而

\[
H''(B)
=-\frac{3D}{4}(4A-B)(A+B)^{-7/2}<0
\]

对 \(B<2A\) 成立。\(H'(0)>0\)，并且 \(H'(2A)=-1\)，所以在
\((0,2A)\) 内恰有一个根；正区间的右端点处 \(H=0\)，不会产生更大值。
因此 \(SC\text{-}HBL\) 在均匀 owner 模型中可以通过一个唯一的一维根求解，
无需枚举 factor arrangement。这仍然是弱下界的优化，不是 tightness 证明。

这个推导的假设必须保留：不允许 recomputation，所有 partial/output 的丢弃或
写回都算 edge event，且 \(B\) 的 arrival 可以在 child group 内免费复制。若
允许免费初始 replication、压缩或把 partial 留在未计费的第三层状态中，
\(SC\text{-}1\) 的可见 entries 集合必须重新定义，不能直接套用。

## 第一条精确小实例

`experiments/exact_small_gemm_pebble.py` 对一个单 owner 的
\(2\times2\times2\) GEMM 做有限状态最短路搜索。模型明确规定：容量为
\(M\) 的 fast memory、A/B/已初始化 C 的每次加载收费一个 word、逐产品只
计算一次、第一次 C 零初始化免费、最终写回暂不计费。所得最少加载量为

```text
M=3: 12,  M=4: 10,  M=5: 9,  M=6: 8.
```

在 \(M=3\) 时，A/B 的 one-copy compulsory term 为 8；用
\(f(M)=(2M/3)^{3/2}\) 得到的连续 phase 项约为 5.49，所以简单
\(\max\{\text{cut},\text{phase}\}=8\)，而精确 trace optimum 是 12。
这不是完整 GEMM I/O 定理（模型省略最终写回并允许第一次 C 初始化免费），
但它证明联合 envelope 需要 resident-state/partial-accumulation 信息，不能
由两个现成标量下界的 `max` 自动闭合。
