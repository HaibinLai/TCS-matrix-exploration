# 有限容量下的联合 phase/cut envelope

## 目的

固定层次树上的 T3-Steiner 定理处理了 memory-independent word volume；经典
HBL/phase 引理处理了一个 owner 在容量 (M) 下的 reload traffic。两者都
会把同一个首次加载事件算进去，所以不能把两个标量下界未经证明直接相加。

本文件给出一个可用于三层 GEMM 的联合可行域。它不是把困难藏在一个新常数
里，而是把每个 phase 的 product set、resident set、load set 和 cut 事件
显式写出。任何真实执行都映射到该可行域，因此其最小通信量是一个合法的
lower-bound envelope；若后续构造 schedule 达到该最小值，才得到 tightness。

## 单条层次边的 trace

先固定一条从 parent 到 child hierarchy group 的收费边 (e)。在 child 侧
有 owners (rin R_e)，每个 owner 的容量是 (M_e)。对 owner (r)，把
执行切成 phases (t=1,ldots,T_r)。定义：

- (F_{r,t}subseteq [m]	imes[k]	imes[n])：该 phase 完成的 products；
- (U_{r,t}=pi_A(F_{r,t})cuppi_B(F_{r,t})cuppi_C(F_{r,t}))：
  phase 需要出现的 data entries；
- (K_{r,t})：phase 开始时 resident 的 entries；
- (L_{r,t}=U_{r,t}setminus K_{r,t})：该 phase 新加载的 entries。

trace 必须满足：

\[
F_{r,t}\cap F_{r,t'}=\varnothing\quad(t\ne t'),
\qquad
\bigcup_{r,t}F_{r,t}=T,
\tag{TR-1}
\]

\[
|K_{r,t}|\le M_e,
\qquad
K_{r,t+1}\subseteq K_{r,t}\cup U_{r,t},
\qquad
|K_{r,t+1}|\le M_e,
\tag{TR-2}
\]

以及每个 (F_{r,t}) 的三投影满足

\[
|F_{r,t}|le
\sqrt{|\pi_A(F_{r,t})|,|\pi_B(F_{r,t})|,|\pi_C(F_{r,t})|}.
\tag{TR-3}
\]

若 phase 采用标准的 (M_e)-transfer 切分，还要求

\[
|L_{r,t}|\le M_e,
\tag{TR-4}
\]

并可把除最后一个 phase 外的 phase 规范化为恰好 (M_e) 次新加载。

对每个 entry (d)，设 (b_e(d)) 是 T3-Steiner cut indicator：当 (d) 的
唯一 source 在 parent 侧而 child 侧某个 owner 需要它时，(b_e(d)=1)。
copy-creation 约束为

\[
\sum_{r,t}\mathbf 1[d\in L_{r,t}]\ge b_e(d).
\tag{TR-5}
\]

如果 (d) 在 child 侧由多个 owner 使用，(TR-5) 还可按 child subtree
分支分别写出；这就是 Steiner cut 的逐边版本。C 的 partial reduction 另加
一个 (\rho_e(c)\) 事件，要求每个被 cut 分开的 source/sink 至少有一个
aggregate crossing (e)。

## 联合 envelope

令 (mathfrak T_e(M_e)) 是满足 (TR-1)--(TR-5) 以及 C-reduction 约束的
所有 phase traces。定义

\[
\mathcal E_e(M_e)=
\inf_{\mathcal T\in\mathfrak T_e(M_e)}
\left[
\sum_{r,t}|L_{r,t}|
 +\sum_{c\in C}\rho_e(c)
\right].
\tag{E-TRACE}
\]

这里的第一项是跨 (e) 的 load/reload word volume；若某个 trace 使用了
child 内部共享 cache，应把首次到达 parent-child group 的事件放进同一个
entry 的 (L) 集合，而不把一次物理传输复制计成多个 leaf load。

### 联合下界定理

在一次产品计算、计费复制、无 recomputation 的模型中，任意真实执行诱导一条
合法 trace，因此

\[
\boxed{V_e\ge \mathcal E_e(M_e).}
\tag{E-LB}
\]

证明只是 trace projection：把真实执行每个 phase 的 products、开始时的
resident entries、首次/重复加载和 partial reduction 记录下来，即得到
(TR-1)--(TR-5)；真实跨边传输数正好不小于目标函数。\(\square\)

这个定理的价值在于：ownership 与 phase 不是两个需要事后相加的数字，而是
同一个可行域中的事件。它适用于任意叶端 product assignment；不要求矩形
grid chain。若容量趋于无限且每个 owner 只需一个 phase，(L) 只剩首次
到达事件，(E-TRACE) 退化为 T3-Steiner 的 copy-lineage 计数。

## 两个可立即推出的弱化下界

### Cut 项

从 (TR-5) 直接得到

\[
\mathcal E_e(M_e)
\ge B_e,
\qquad
B_e=\sum_d b_e(d)+\sum_c\rho_e(c).
\tag{E-CUT}
\]

这正是 memory-independent Steiner boundary。

### Phase/HBL 项

若 owner (r) 完成 (W_r) 个 products，容量为 (M_e)，由 (TR-2)--(TR-4)
和 Loomis--Whitney/HBL，单个 phase 至多完成

\[
f(M_e)=\left(\frac{2M_e}{3}\right)^{3/2}
\]

个 products。标准 full-phase 计数给出

\[
\mathcal E_e(M_e)
\ge
\left(
 f(M_e)^{-1}\sum_r W_r-|R_e|
\right)M_e,
\tag{E-PHASE}
\]

并与非负性取最大值。整数 phase 版本可把右侧替换为

\[
M_e\left(\sum_r\left\lceil W_r/f(M_e)\right\rceil-|R_e|\right)_+.
\]

这里 phase 项仍然包含首次加载；这是它与 (B_e) 重叠的根源。

## 为什么不能直接相加

取一个抽象但合法的 phase 事件记录：(M=6)，每个 phase 的 HBL work
上限取 (f=8)，总 work (W=27)，首次到达事件数 (B=6)。一个标准
full-phase trace 可以有 4 个 phases、总 load volume (Q=18)；连续 HBL
式给出 (Q_{\rm phase}=6(27/8-1)=57/4)。于是

\[
\max\{B,Q_{\rm phase}\}=57/4<18,
\qquad
B+Q_{\rm phase}=81/4>18.
\]

同一批首 phase loads 同时属于 cut 的首次到达和 phase 预算。这个算术例子
不是 GEMM 算法的 tightness 声明；它证明了在没有额外不相交事件定义时，
“owner bound + phase bound”不是一个普遍有效的 lower bound。

## 下一步的可证伪目标

1. 在 (2\times2\times2) 和 (3\times3\times3) GEMM 上枚举合法小 trace，
   计算 (E-TRACE) 的整数最优值；
2. 比较它与 (max(E\text{-CUT},E\text{-PHASE})) 的差距，判断是否存在
   非平凡 overlap correction；
3. 对标准 blocked/SUMMA schedule 记录同一 trace，测试何时达到 (E-TRACE)；
4. 若某个阶段需要 child 内共享 cache，扩展 trace 的 copy-lineage 状态，
   而不是把每个 leaf 的 reload 简单相加；
5. 在此基础上再定义 (L)-level、非对称 (M_\ell) 和 weighted-edge
   版本。

在完成第 1--3 步以前，不把 (E-TRACE) 简化成一个新的闭式常数，也不声称
有限容量下已经得到三层 tight theorem。

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
