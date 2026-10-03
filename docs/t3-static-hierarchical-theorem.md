# 三层静态嵌套通信定理：逐边增量版本

这份定理是当前工作的第一个完整 lower-bound/matching 结果。它针对一个明确的三层 classical GEMM 模型，证明每条层间边必须承担多少**新增**复制或归约通信，并给出达到该向量下界的嵌套 broadcast/reduction schedule。

它故意不把旧的三层 affine line 直接相加：如果同一个矩阵元素已经在粗层有多个副本，细层只应为新增副本计费。旧的完整 line sum 是几何 proxy；本文件的增量式才是当前可以逐项证明的通信量。

## 模型

计算
\[
C=AB,\qquad A\in\mathbb R^{m\times k},\quad
B\in\mathbb R^{k\times n},\quad C\in\mathbb R^{m\times n}.
\]

三层处理器数满足
\[
P_1\ge P_2\ge P_3,
\]
其中 (P_1) 是最细粒度的计算层。第 \(\ell\) 层使用三维 block grid
\[
g_\ell=(a_\ell,b_\ell,c_\ell),
\qquad a_\ell b_\ell c_\ell=P_\ell.
\]
再定义源层
\[
g_4=(1,1,1).
\]
合法嵌套要求
\[
g_{\ell+1}\preceq g_\ell
\quad\Longleftrightarrow\quad
 a_\ell/a_{\ell+1},
 b_\ell/b_{\ell+1},
 c_\ell/c_{\ell+1}
\text{ 都是整数}.
\]

收费边按细到粗编号：

- (E_1)：(P_2\leftrightarrow P_1)；
- (E_2)：(P_3\leftrightarrow P_2)；
- (E_3)：慢存储\(\leftrightarrow P_3)。

(V_\ell) 表示穿过 (E_\ell) 的 aggregate word volume；一个 word 经过多条边时，在每条实际边上分别计数。

此外固定以下 owner 规则：

1. 每个 scalar product 只计算一次，并由 (P_1) 的唯一 block owner 负责；
2. A、B 的初始输入在源层各只有一份付费副本；
3. 在边 (E_\ell) 的粗侧，每个 A-entry 已有 (c_{\ell+1}) 个沿 c 方向的 owner copies，每个 B-entry 已有 (a_{\ell+1}) 个沿 a 方向的 copies；
4. 每个 C-entry 在细侧有 (b_\ell) 个 k-block partials，粗侧最终保留 (b_{\ell+1}) 个 partials；
5. 不允许 recomputation、免费初始 replication 或执行期间改变 block grid；每次广播、复制和归约都按 word 计费。

第 3–4 条是静态 owner-consistent 模型的定义。它们不是对动态 GEMM 实现的自动推论。

## 三层逐边下界

### 定理 T3-static-vector

对任意满足上述假设的合法执行，对每条边都有
\[
\boxed{
V_\ell\ge
(c_\ell-c_{\ell+1})mk
+(a_\ell-a_{\ell+1})kn
+(b_\ell-b_{\ell+1})mn,
\qquad \ell=1,2,3.
}
\tag{T3-V}
\]

因此，对任意非负边权 (w_1,w_2,w_3)，
\[
Q_w=\sum_{\ell=1}^3 w_\ell V_\ell
\ge
\Phi_w(g_1,g_2,g_3),
\]
其中
\[
\Phi_w(g_1,g_2,g_3)=
\sum_{\ell=1}^3w_\ell\left[
(c_\ell-c_{\ell+1})mk
+(a_\ell-a_{\ell+1})kn
+(b_\ell-b_{\ell+1})mn
\right].
\tag{T3-Φ}
\]

对固定处理器数 (P^*=(P_1,P_2,P_3))，定义增量嵌套 envelope
\[
N_{\rm inc,w}(m,k,n;P^*)=
\min_{g_3\preceq g_2\preceq g_1}
\Phi_w(g_1,g_2,g_3).
\tag{T3-N}
\]
则所有该模型中的静态执行满足
\[
Q_w\ge N_{\rm inc,w}.
\]

## 证明

### A-entry 的新增复制

固定一个 A-entry。粗层有 (c_{\ell+1}) 个 c-owner copies。每个粗 copy 对应
\[
\rho_c=c_\ell/c_{\ell+1}
\]
个细层 c 子组，因为细层的全部 (j)-blocks 都必须参与与该 A-entry 相关的产品。保留一个本地 copy 后，其余 (\rho_c-1) 个子组至少各接收一个 word。

所以每个粗 copy 至少产生 (\rho_c-1) 次跨 (E_\ell) 的 word movement；对全部 (c_{\ell+1}) 个粗 copies 求和，得到
\[
c_{\ell+1}(\rho_c-1)=c_\ell-c_{\ell+1}
\]
次 movement。A 有 (mk) 个 entries，因此
\[
V_\ell^{(A)}\ge(c_\ell-c_{\ell+1})mk.
\]

### B-entry 的新增复制

同理，一个 B-entry 的粗层 copies 沿 a 方向扩展到
\[
\rho_a=a_\ell/a_{\ell+1}
\]
个细层子组，所以
\[
V_\ell^{(B)}\ge(a_\ell-a_{\ell+1})kn.
\]

### C 的新增归约

固定一个 C-entry。细层有 (b_\ell) 个来自不同 k-block 的 partials，粗层只保留 (b_{\ell+1}) 个 partials。一次 word movement 至多把两个当前 partial aggregates 合并成一个，因此至少需要
\[
b_\ell-b_{\ell+1}
\]
次 movement。对 (mn) 个 C-entries 求和，得到
\[
V_\ell^{(C)}\ge(b_\ell-b_{\ell+1})mn.
\]

三类 movement 属于不同的数据对象，求和即得 (T3-V)。这是一条逐边、逐 word 的计数，不使用连续近似，也不依赖 25-line arrangement。

## Tightness

在每个粗层 owner group 内：

1. 对每个 A copy 沿 c 子组建一棵 spanning tree，发送恰好 (\rho_c-1) 个新 word；
2. 对每个 B copy 沿 a 子组执行同样的 broadcast；
3. 对每个 C-entry 的 (b_\ell) 个 partials 沿 b 子组做一棵归约森林，使最终保留 (b_{\ell+1}) 个 partials，恰好使用 (b_\ell-b_{\ell+1}) 次 word movement。

因此在允许树形 broadcast/reduction、每条跨层链路按 word 计费的拓扑中，存在 schedule 使 (T3-V) 每条边同时取等号。对固定 chain，(Q_w=\Phi_w)；对所有 chain 取最小值，则
\[
\boxed{Q_w=N_{\rm inc,w}}
\]
在该静态模型中成立。

## 一层恢复

若只有一个 grid (g=(a,b,c))，令源层为 (g_2=(1,1,1))，(T3-V) 变成
\[
V\ge(c-1)mk+(a-1)kn+(b-1)mn.
\]
除以 (P=abc) 后得到
\[
\bar V\ge
\frac{mk}{ab}+\frac{kn}{bc}+\frac{mn}{ac}
-\frac{mk+kn+mn}{P},
\]
这正是现有 static-grid ownership lemma 的 SG-1/SG-2。

## 与旧 nested envelope 的关系

旧代码中的
\[
\sum_\ell\left(
\frac{mk}{a_\ell b_\ell}
+\frac{mn}{a_\ell c_\ell}
+\frac{kn}{b_\ell c_\ell}
\right)
\]
把每层完整 grid line 都相加。若粗层已经拥有多个副本，这个表达式会把一部分已存在的复制再次计算，因此只能作为 compatibility geometry proxy，不能直接称为物理通信下界。

当前定理应使用逐边增量函数
\[
\delta_\ell=
\frac{(c_\ell-c_{\ell+1})mk
+(a_\ell-a_{\ell+1})kn
+(b_\ell-b_{\ell+1})mn}{P_\ell}
\]
或其 aggregate-volume 版本。两者的归一化必须在实验中明确，不能混用。

## 这个定理还没有覆盖什么

T3-static-vector 是一个真实但受限的三层定理。它没有证明：

- 任意动态 ownership 都能被单一 nested chain 表示；
- 免费初始复制不会降低下界；
- recomputation 仍满足同一 projection/ownership 计数；
- 有限 local memory 下的 HBL phase 项自动与 (T3-V) 相加；
- 环、torus 或受限网络中的 message count 和 hop count；
- arbitrary-schedule 的一般 rectangularization。

因此下一步应当是证明一个 **time-expanded nested partition lemma**，或者寻找能破坏单一 chain 的最小动态反例。只有该引理成立，T3-static-vector 才能升级为 arbitrary-schedule T3-volume。

## 可复现实验

`experiments/check_t3_static_hierarchical_theorem.py` 检查：

- 一层 SG-1 精确恢复；
- 三层兼容 chain 的逐边 aggregate volume；
- 无权 aggregate volume 的 telescoping；
- 非等权边成本下增量 envelope 的确依赖 chain；
- 小型 (P^*=(24,12,6)) 的兼容 chain 数量和加权最小值。
