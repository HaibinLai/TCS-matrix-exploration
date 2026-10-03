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
K_{r,t+1}\subseteq
K_{r,t}\cup G_t\cup\operatorname{supp}(X_{e,t})\cup U_{r,t},
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

这里的 \(K_{r,t+1}\) 转移显式包含本 phase 的 shared-cache entries 和
edge arrivals；否则一个刚刚到达的 entry 不能在下一 phase 继续 resident，
会把合法的 reuse trace 错误地排除。\(U_{r,t}\) 允许 phase 内新产生的
partial/output entry 在下一 phase 被保留。若只研究输入 broadcast 边，可令
\(U_{r,t}\) 中的 output entries 通过单独的 \(\rho_e\) 反向事件处理。

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

`experiments/check_exact_trace_phase.py` 进一步重放 \(M=3\) 的最短 trace，
按每个 phase 至多 3 次 load 切分为 4 个 phases。其 projection/work 摘要为

```text
(loads, work, (A, B, C), HBL)
(3, 2, (1, 2, 2), 2.0000)
(3, 3, (2, 3, 2), 3.4641)
(3, 1, (1, 1, 1), 1.0000)
(3, 2, (2, 1, 2), 2.0000)
```

第二个 phase 的实际 work 是 3，而 HBL 连续上界是
\(\sqrt{2\cdot3\cdot2}\approx3.4641\)。因此即使 projection 计数正确，
整数 product set 和 resident partial 的可实现性仍会造成严格 slack；typed
envelope 的一般 tightness 需要额外的整数/状态约束。


## Exact shared-cache operand trace

`experiments/exact_shared_cache_trace.py` 对一个按 \(i\) 分工的两个 owner \(2\timesimes2\timesimes2\) GEMM 做精确最短路。
模型只保留 A/B operand traffic：每个 owner 的 local capacity 为 \(M=2\)，child group 的 shared cache 只存 B-entry；C 的计算和写回在这个诊断模型中免费。
parent-to-owner direct arrival 和 parent-to-group shared arrival 各计一个 word，shared-to-local promotion 免费。结果为

```text
shared capacity G=0: 12 arrivals
shared capacity G=1:  8 arrivals
shared capacity G=2:  8 arrivals
```

四个 B-entry 在两个 owner 之间共享，因此一个 shared slot 便可流式复用全部 B-entry；继续增加容量没有收益。这个结果说明 shared-cache state 会改变 edge-arrival optimum，不能把 owner-private phase bound 简单相加。由于 C partial、最终写回和三层嵌套都被省略，这里是联合 trace 的精确子模型证据，不是完整 GEMM tight theorem。

## Restricted shared-operand cut lemma

在上面的两个 owner row-split 子模型中，令 \(A_0,A_1\) 是各自只被一个 owner 使用的四个 A-entry，令 \(B\) 是两个 owner 都需要的四个 B-entry。parent 对每个 entry 只有一个 source copy，且不允许 recomputation。对 A-entry，每个 entry 至少跨 parent-child 边一次，所以 A 的下界是 4。

若 shared capacity \(G=0\)，每个 B-entry 必须分别送到两个 owner，因此

\[
Q_{AB}\ge 4+2\cdot4=12.
\]

若 \(G\ge1\)，每个 B-entry 可以先跨边一次，再在 child group 内复用，所以

\[
Q_{AB}\ge 4+4=8.
    \tag{SC-AB}
\]

当每个 owner 的 local capacity 为 2 时，逐个保持一个 A-entry 和一个 shared B-entry 的流式 schedule 分别达到 12 和 8；因此这个受限模型中 \(SC\text{-}AB\) 是 tight。精确搜索和下界核对由 `experiments/check_shared_operand_cut_lemma.py` 完成。

这个 lemma 的作用是说明 shared-cache 状态本身可以进入下界公式；它没有 处理 C partial、最终归约或多个层次，因此只能作为完整 E-TRACE theorem 的 operand-only 子定理。

## Typed projection envelope

总 footprint \(M_r+M_g+B\) 会抹掉 A、B、C 三类数据的形状。为保留
rectangular 和 asymmetric 信息，对一个 phase 写

\[
\mathbf m_r=(m_{r,A},m_{r,B},m_{r,C}),\qquad
\mathbf g=(g_A,g_B,g_C),\qquad
\mathbf b=(b_A,b_B,b_C),
\]

并要求

\[
\sum_X m_{r,X}\le M_r,\qquad
\sum_X g_X\le M_g,\qquad
\sum_X b_X\le B,
\tag{TP-1}
\]

其中 \(X\in\{A,B,C\}\)。不允许 recomputation 且把 materialization/eviction
计入 edge arrivals 时，每个 owner 的 projection sizes 满足

\[
|\pi_X(F_{r,t})|
\le m_{r,X}+g_X+b_X,\qquad X\in\{A,B,C\}.
\tag{TP-2}
\]

因此该 phase 的 work 满足

\[
|F_{r,t}|
\le
\psi_r(\mathbf m_r,\mathbf g,\mathbf b)
:=
\sqrt{
(m_{r,A}+g_A+b_A)
(m_{r,B}+g_B+b_B)
(m_{r,C}+g_C+b_C)
}.
\tag{TP-3}
\]

定义 typed phase envelope：

\[
\Psi(B)=
\max_{\substack{\mathbf b,\mathbf g,\mathbf m_r\\
\text{satisfying }TP\text{-}1}}
\sum_{r\in R_e}\psi_r(\mathbf m_r,\mathbf g,\mathbf b).
\tag{TP-4}
\]

同一个 \(\mathbf g\) 出现在所有 owners 中，表示 shared cache 的 entries
只被装入一次。于是 full-phase 计数给出

\[
\boxed{
V_e\ge
\sup_{B>0}
B\left(\frac{W_e}{\Psi(B)}-1\right)_+.
}
\tag{TP-HBL}
\]

对 \(\psi_r\) 使用 AM--GM 会恢复上一节的 scalar \(SC\text{-}1\)--\(SC\text{-}3\)，
因此 typed envelope 是一个不弱于 scalar relaxation 的 lower bound。它在
A/B/C 容量或边成本不对称、以及 rectangular GEMM 中可以严格保留 projection
shape；同时共享 \(\mathbf g\) 防止一个 shared B tile 被按 owner 重复计数。

这仍然是 phase relaxation，不是 tightness 证明。下一步应研究 typed maximizer
何时对应实际 blocked tile，以及何时 projection overlap 使 \(TP\text{-}4\)
仍然过松。

## Typed rectangular phase 的取等条件

可以先把 \(TP\text{-}4\) 的一个可证明 tight 子族单独抽出来。对 owner
\(r\)，设 phase 中完成的乘法恰好是

\[
F_{r,t}=I_{r,t}\times K_{r,t}\times J_{r,t}.
\]

记

\[
i_{r,t}=|I_{r,t}|,\qquad
k_{r,t}=|K_{r,t}|,\qquad
j_{r,t}=|J_{r,t}|.
\]

三个 operand projection 的大小于是必须满足

\[
x_{r,A}=i_{r,t}k_{r,t},\qquad
x_{r,B}=k_{r,t}j_{r,t},\qquad
x_{r,C}=i_{r,t}j_{r,t}.
\tag{TP-EQ-1}
\]

如果 typed allocation 正好给出

\[
x_{r,X}=m_{r,X}+g_X+b_X,
\tag{TP-EQ-2}
\]

并且 local、shared、arrival 三类 entry 在每个 projection 上互不重叠，
那么

\[
|F_{r,t}|=i_{r,t}k_{r,t}j_{r,t}
=\sqrt{x_{r,A}x_{r,B}x_{r,C}}
=\psi_r.
\tag{TP-EQ-3}
\]

因此，在以下四个条件同时成立时，typed HBL 对该 phase 逐 owner 取等：

1. 乘法集合是 \(I\times K\times J\) 的笛卡尔积；
2. 三个 projection 的大小满足 \(TP\text{-}EQ\text{-}1\)；
3. \(TP\text{-}EQ\text{-}2\) 的三类 entry 没有隐藏 overlap；
4. shared entries 只在 edge 上 arrival 一次，随后在 child group 内复用，
   且没有 recomputation 或未计费的 materialization。

若连续 \(q\) 个 full phases 都满足这些条件，并且每个 phase 的 edge arrival
恰好达到 \(B\)，则

\[
W_e=q\sum_r\psi_r,\qquad V_e=qB
\]

（最后一个不足 full phase 的 remainder 另行计数）。换句话说，\(TP\text{-}HBL\)
的 phase packing 项在这个受限 schedule family 上是可达到的。这个结论不等于
一般有限容量定理：一般执行可能有非笛卡尔 product set、不同 owner 之间的
projection overlap，或跨 phase 保留 partial；把任意执行规约到上述四个条件，
正是当前尚未解决的 tightness 问题。

一个实用的可检验条件是，给定 typed projection 三元组
\((x_A,x_B,x_C)\)，检查

\[
i=\sqrt{\frac{x_Ax_C}{x_B}},\qquad
k=\sqrt{\frac{x_Ax_B}{x_C}},\qquad
j=\sqrt{\frac{x_Bx_C}{x_A}}
\]

是否都是整数。若不是，HBL 仍给出合法下界，但这个 phase 不可能由单个
整数笛卡尔 tile 直接达到，只能通过多个 tile 或带 remainder 的构造逼近。
