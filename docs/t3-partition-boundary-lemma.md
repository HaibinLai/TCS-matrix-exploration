# 任意 owner partition 的单边通信下界

这是把静态矩形网格定理推广到任意一次计算调度的第一步。它只处理一条通信边；多级嵌套和动态 owner 还需要额外的 time-expanded compatibility lemma。

## 单边模型

令
\[
T=[m]\times[k]\times[n]
\]
是 classical GEMM 的 scalar-product 集合。一次执行把每个产品恰好分配给一个 fine-side owner group，得到一个互不相交的分区
\[
\Pi=\{S_1,\ldots,S_P\},
\qquad \bigsqcup_{r=1}^{P}S_r=T.
\]
对每个 part 定义
\[
A_r=\pi_A(S_r)\subseteq[m]\times[k],
\quad
B_r=\pi_B(S_r)\subseteq[k]\times[n],
\quad
C_r=\pi_C(S_r)\subseteq[m]\times[n].
\]
假设：

1. 每个 A-entry 和 B-entry 在这条边的粗侧初始只有一个付费副本；
2. 每个 product 只计算一次；
3. 每个 C-entry 最终只保留一个输出副本；
4. 复制、部分和迁移和输出归并都按 word 计费；
5. 不允许通过重新计算来避免输入或 partial 的传输。

定义投影边界
\[
\partial(\Pi)=
\sum_{r=1}^{P}
\bigl(|A_r|+|B_r|+|C_r|\bigr)
-(mk+kn+mn).
\tag{PB}
\]

## 定理：partition-boundary lemma

令 (V_E) 是这条边上的 aggregate word volume。则
\[
\boxed{V_E\ge\partial(\Pi).}
\tag{PB-LB}
\]

### 证明：A 和 B

对每个 A-entry (a)，令
\[
d_A(a)=|\{r:a\in A_r\}|.
\]
因为 part (S_r) 中至少有一个产品使用 (a)，该 owner group 必须在计算前获得一个 (a)-copy。初始只有一个 copy，因此至少有 (d_A(a)-1) 次额外 word arrival 或等价的跨边复制。

对所有 A-entries 求和：
\[
V_E^{(A)}
\ge\sum_a(d_A(a)-1)
=\sum_r|A_r|-mk.
\]
同样地，
\[
V_E^{(B)}\ge\sum_r|B_r|-kn.
\]

### 证明：C partials

对每个 C-entry (c)，令
\[
d_C(c)=|\{r:c\in C_r\}|.
\]
这表示有多少 owner groups 产生了该 C-entry 的 partial contribution。最终只保留一个输出副本；一次 word movement 至多把两个当前 aggregates 合并成一个，因此至少需要 (d_C(c)-1) 次跨边 movement。于是
\[
V_E^{(C)}
\ge\sum_c(d_C(c)-1)
=\sum_r|C_r|-mn.
\]
三项相加即得 (PB-LB)。证毕。

这个证明只使用“每个 part 需要哪些投影数据”和“一次计算/单份最终输出”两个事实，不要求 (S_r) 是矩形块。

## HBL/AM–GM 推论

对任意 (S\subseteq T)，Loomis--Whitney 给出
\[
|S|\le
\sqrt{|\pi_A(S)|,|\pi_B(S)|,|\pi_C(S)|}.
\]
令
\[
x_r=|A_r|,\qquad y_r=|B_r|,\qquad z_r=|C_r|.
\]
则
\[
x_ry_rz_r\ge |S_r|^2,
\]
从而由 AM--GM 得
\[
x_r+y_r+z_r
\ge3|S_r|^{2/3}.
\]
若工作完全平衡，
\[
|S_r|=\frac{mkn}{P},
\]
则
\[
\sum_r(x_r+y_r+z_r)
\ge3(mkn)^{2/3}P^{1/3}.
\]
代入 (PB) 得到任意 balanced owner partition 的通信下界
\[
\boxed{
V_E\ge
3(mkn)^{2/3}P^{1/3}-(mk+kn+mn).
}
\tag{HBL-PB}
\]
除以 (P) 后，得到每个 owner 的平均量
\[
\bar V_E\ge
3\frac{(mkn)^{2/3}}{P^{2/3}}
-\frac{mk+kn+mn}{P}.
\]
对 square GEMM，这恢复了熟知的 (n^2/P^{2/3}) memory-independent geometry（常数取决于是否把 A、B、C 三类 movement 全部计入）。

## 与三层模型的关系

在三层 hierarchy 中，可以对每条边分别构造 owner partition \(\Pi_1,\Pi_2,\Pi_3\)。但是不能直接把三次 (PB-LB) 相加，原因是细边的初始侧可能已经含有粗边产生的多个副本。正确做法有两种：

1. **静态 nested owner**：显式记录粗层 copies，并用 `docs/t3-static-hierarchical-theorem.md` 的逐边增量项；
2. **动态 owner**：建立 time-expanded partition，使每个 edge boundary 的初始 copies、重复使用和最终归并都被单独标记。

因此，(PB-LB) 解决的是“任意形状 part 的单边投影边界”问题；它本身不证明矩形化，也不自动证明三层 chain compatibility。

## 反例边界

以下情况需要修改定理或增加项：

- 免费初始 replication：把初始副本数从 (mk+kn+mn) 改成真实初始 copy budget；
- recomputation：一个 product 可多次计算时，不能直接用唯一 owner partition；
- 不平衡 work：HBL/AM--GM 推论需使用实际的 \(|S_r|\)，不能代入 (mkn/P)；
- 动态 migration：应使用 product-owner pairs 或 time-expanded parts，而不是静态分区。

`experiments/check_small_partition_boundary.py` 和
`experiments/check_nested_partition_boundary.py` 对 (2\times2\times2) 的任意分区进行了穷举检查；它们验证有限实例，但不替代上述证明。

## 多级 time-expanded corollary：不要求单一 chain

设一个 $L$ 层执行允许 owner 在不同时间变化，但仍满足：每个 product 只计算一次、输入没有免费初始复制、最终每个 C-entry 只有一个输出。令 (Pi_{\rm fine}) 是最细计算层在产品计算事件上诱导的 owner partition。

对一个 A-entry $a$，记 $d_A(a)$ 为最终需要该 entry 的不同最细 owner group 数。源层只有一个 copy，而一次跨任意层边的 word transfer 至多使可达 copy 数增加一个。因此所有层合计的 A traffic 满足
\[
\sum_{\ell=1}^{L}V_\ell^A
\ge\sum_a(d_A(a)-1).
\]
对 B 同理。对一个 C-entry，若最终有 $d_C(c)$ 个不同 owner group 产生 partial contribution，则把这些 partials 合并为一个输出至少需要 (d_C(c)-1) 次跨层 movement。于是
\[
\sum_{\ell=1}^{L}V_\ell
\ge \partial(\Pi_{\rm fine}).
\tag{TE-PB}
\]

(TE-PB) 不需要固定 grid，也不需要不同层的 owner map 形成单一 chain。它的代价是只给出总 volume 下界，不能分别给出每条边的 $V_\\ell$ 下界，也不能产生旧的 compatibility penalty。若要恢复逐边或带权的 nested theorem，仍需证明 time-expanded owner labels 的兼容性与 copy lineage 约束。

这个 corollary 说明了当前研究的分界：

- **已经可证明**：静态 nested grids 的逐边向量下界，以及动态多级执行的总 volume projection 下界；
- **尚未证明**：任意动态执行的逐边 chain envelope；
- **需要反例或新引理**：动态 grid 是否能避免某个静态 chain 的加权通信成本。
