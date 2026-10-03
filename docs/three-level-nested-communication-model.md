# 三层经典 GEMM 的嵌套通信下界：模型与定理目标

本文把当前实验代码中的 affine-envelope 模型，提升为一个明确的三层通信模型。这里先研究 classical GEMM；Strassen、矩形矩阵、重计算和 asymmetric costs 都放到后续扩展中。

## 1. 计算对象

先取 square classical matrix multiplication

\[
C=AB,\qquad A,B,C\in\mathbb R^{n\times n}.
\]

计算 DAG 包含 $n^3$ 个 scalar products

\[
v_{ikj}=a_{ik}b_{kj},
\]

以及将同一 $c_{ij}$ 的 $n$ 个 products 做加法归约的 reduction edges。基准模型采用以下限制：

1. 每个 scalar product 只计算一次；
2. replication 必须通过被计费的通信产生；
3. 输入可以任意初始分布，但输入从慢层读入、输出写回慢层都计入通信；
4. 每个最内层处理单元承担平衡的 $\Theta(n^3/P_1)$ 工作；
5. processor grid 在一次 GEMM 中固定，暂不允许执行期间动态改变 grid。

第 1–5 条是 **v0 theorem 的模型假设**，不是对所有实际 GEMM 实现的声明。重计算、动态重分块和不平衡调度将在后续版本单独处理。

## 2. 三层 hierarchy

设三个处理器层从内到外为

\[
P_1\ge P_2\ge P_3,\qquad P_2\mid P_1,\quad P_3\mid P_2.
\]

第 $\ell$ 层使用三维 processor grid

\[
g_\ell=(a_\ell,b_\ell,c_\ell),
\qquad a_\ell b_\ell c_\ell=P_\ell.
\]

写 $g'\preceq g$ 当且仅当 $g'$ 的三个坐标分别整除 $g$ 的三个坐标。一个合法的 nested chain 是

\[
g_3\preceq g_2\preceq g_1.
\]

因此

\[
\mathcal C(P^*)=
\{(g_1,g_2,g_3):g_\ell\in\mathcal G(P_\ell),
 g_3\preceq g_2\preceq g_1\}.
\]

当前代码中的 `compatible(inner, outer)` 正是在检查这个 componentwise-divisibility 条件。

## 3. Aspect ratio 与 affine communication line

把三个矩阵方向归一化为

\[
\theta=(1,z,y),\qquad 0\le y\le z\le1.
\]

当前 exact model 对 grid $g=(a,b,c)$ 使用归一化 affine line

\[
\ell(g;z,y)=
\frac1{ab}+\frac{z}{ac}+\frac{y}{bc}.
\]

真实 word-volume 模型需要把它乘上第 $\ell$ 层的尺度因子 $\kappa_\ell(n,P_\ell,M_\ell)$：

\[
\Lambda_\ell(g;z,y)=
\kappa_\ell(n,P_\ell,M_\ell)\,\ell(g;z,y).
\]

因此当前代码已经验证了 **归一化 grid geometry**，但还没有声称 $\kappa_\ell$ 已经从完整 machine model 中推导出来。恢复已知一层下界的第一步，就是确定这个尺度因子并检查量纲。

## 4. 通信计费

v0 只计 word volume。第 $\ell$ 层的 $V_\ell$ 是穿过该层边界的 word 数；一个 word 穿过多级边界时，在每条实际边上分别计数。总 volume 是

\[
Q_{\mathrm{vol}}=\sum_{\ell=1}^{3}V_\ell.
\]

v0 不把 latency、message count、同步次数和能耗混进同一个标量。后续可定义

\[
Q_{\alpha\beta}=
\sum_\ell(\alpha_\ell S_\ell+\beta_\ell V_\ell),
\]

但在没有先证明 volume bound 以后，不把联合目标称为 tight。

## 5. 两个 envelope

如果每层可以独立选 grid，归一化的 independent envelope 是

\[
I(z,y)=
\sum_{\ell=1}^{3}
\min_{g\in\mathcal G(P_\ell)}
\Lambda_\ell(g;z,y).
\]

如果三个层次必须使用同一条兼容 chain，nested envelope 是

\[
N(z,y)=
\min_{(g_1,g_2,g_3)\in\mathcal C(P^*)}
\sum_{\ell=1}^{3}\Lambda_\ell(g_\ell;z,y).
\]

当前实验中的 $N/I$ 是 **compatibility penalty**：它衡量层间兼容性相对于“每层各自最优”的额外开销。它本身还不是完整 machine-model lower bound，除非第 6 节的 lifting lemma 被证明。

## 6. 三层 lower-bound theorem 的正式目标

### Theorem T3-volume（目标）

在第 1 节的 classical/no-recomputation/static-grid 假设和第 4 节的 edge-volume 计费下，存在可由 HBL/phase-partition 证明的尺度因子 $\kappa_\ell$，使得任意合法 GEMM schedule $\mathcal A$ 满足

\[
Q_{\mathrm{vol}}(\mathcal A;z,y)
\ge
N(z,y)-O(n^2).
\]

这里的 $O(n^2)$ 允许输入输出 materialization 的边界项；主项应与 $n^3$ 级计算量同阶。

### Theorem T3-tight（更强目标）

在同一模型下，对每个实现 $N(z,y)$ 的 active chain，存在静态 blocked SUMMA/2.5D/3D schedule，使

\[
Q_{\mathrm{vol}}(\mathcal A_{\mathrm{chain}};z,y)
\le
N(z,y)+O(n^2).
\]

T3-volume 是 lower bound；T3-tight 还要求 matching construction。只有两者都成立，才能称为 tight multilevel communication theorem。

## 7. 与当前 25-line 实验的关系

当前 $P^*=(2pq,pq,p)$ 实验做了三件事：

1. 精确枚举每层的 lower envelope lines；
2. 精确枚举兼容 chain 并形成 $N(z,y)$；
3. 在三角形 $0\le y\le z\le1$ 上寻找 $N/I$ 的最大 cell。

它还没有完成两件关键工作：

1. 从真实 GEMM DAG 和 memory capacities 推导 $\kappa_\ell$；
2. 构造达到 $N(z,y)$ 的真实三层 schedule。

因此，当前的 109 个退化 cell 是 arrangement proof 的一部分，但不是 T3-volume 的全部证明。

## 8. 验证门槛

研究顺序固定为：

1. **量纲门槛：** 从 $L=1$ 或 $L=2$ 恢复已知 classical parallel-MM volume bound；
2. **模型门槛：** 证明 nested chain 的 phase/ownership lemma；
3. **几何门槛：** 完成三层 envelope、退化 cell 和参数阈值的 exact proof；
4. **算法门槛：** 对每个 active chain 给出 matching blocked schedule；
5. **反例门槛：** 测试 replication、动态 grid 和 recomputation 是否破坏 T3 的假设。

任何一关失败，都应明确报告为模型边界，而不是继续把 $N/I$ 写成无条件的矩阵乘法下界。

## 9. One-level geometry recovery

For a rectangular GEMM $A_{m\times k}B_{k\times n}$, the standard three-dimensional grid geometry is

\[
\lambda_{m,k,n}(a,b,c)=
\frac{mk}{ab}+\frac{mn}{ac}+\frac{kn}{bc}.
\]

This is the unnormalized version of the affine line used by the exact scripts. For square matrices and a balanced cubic grid $a=b=c=P^{1/3}$,

\[
\lambda_{n,n,n}=\frac{3n^2}{P^{2/3}},
\]

which recovers the standard memory-independent $n^2/P^{2/3}$ geometry up to the convention-dependent communication constant. `work/check_one_level_recovery.py` verifies the exact value for $P=1,8,27,64,125$ and checks a rectangular instance without substituting the square formula.

This check validates the geometry and units of the affine envelope. It does not by itself prove the HBL/phase-partition lower bound or account for finite local memory; those remain part of the T3-volume proof.
