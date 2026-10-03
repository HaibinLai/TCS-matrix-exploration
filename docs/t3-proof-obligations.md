# T3 证明骨架与缺口

这份文件区分已经证明的三类结果：静态 nested-partition 定理、固定层次树上任意叶端调度的 memory-independent Steiner 定理，以及仍待完成的 finite-capacity arbitrary-schedule 定理。旧的完整 affine-line sum 只作为矩形几何 proxy，不直接视为物理通信下界。

## 已证明目标：静态 nested-partition theorem

对 classical GEMM 的产品集合 `T = [m] × [k] × [n]`，令 `Π₁ ⪯ Π₂ ⪯ Π₃ ⪯ Π₄ = {T}` 是 owner-consistent nested partitions。定义投影和

$$
X_A(Π)=∑_{S∈Π}|π_A(S)|,
\quad
X_B(Π)=∑_{S∈Π}|π_B(S)|,
\quad
X_C(Π)=∑_{S∈Π}|π_C(S)|.
$$

在一次产品计算、单份初始输入、单份最终输出的模型中，第 `ℓ` 条边满足

$$
V_ℓ^A ≥ X_A(Π_ℓ)-X_A(Π_{ℓ+1}),
$$

$$
V_ℓ^B ≥ X_B(Π_ℓ)-X_B(Π_{ℓ+1}),
\quad
V_ℓ^C ≥ X_C(Π_ℓ)-X_C(Π_{ℓ+1}).
$$

树形 broadcast/reduction 在相同拓扑模型下达到这些计数。完整陈述见 `docs/nested-partition-static-theorem.md`。

矩形 grids 是该定理的特例；`docs/t3-static-hierarchical-theorem.md` 给出对应的闭式增量公式。

## Lemma A：单层 projection/phase bound

把执行切成第 `ℓ` 条通信边界上的 phases。一个 phase 至多读取或写出 `s` 个 words；在该 phase 内记 `S_A`、`S_B`、`S_C` 为出现过的 A、B 和 partial/output entries。每个完成的 scalar product 对应一个三元组 `(i,k,j)`，其三个 projections 分别落在这三个集合。Loomis–Whitney/HBL 给出

$$
|F| ≤ √(|S_A| |S_B| |S_C|).
$$

这恢复了单层的 phase 结构，但要接到多级模型，还必须明确本地容量 `M_ℓ`、replication、输入输出 materialization 和 phase 边界，并推导有限容量项的精确系数。预期形式是

$$
Λ_ℓ(g;z,y)=κ_ℓ(n,P_ℓ,M_ℓ)
\left(1/(ab)+z/(ac)+y/(bc)\right).
$$

目前已证明的是 projection boundary 和静态 ownership 计数；`κ_ℓ` 与 phase 项的联合 tightness 仍未完成。

## Lemma B：静态 nested ownership

对每个层次固定一个 owner map。第 `ℓ+1` 层的 owner 是第 `ℓ` 层 owner 的 quotient/coarsening，因此矩形特例满足

$$
g_{ℓ+1} ⪯ g_ℓ.
$$

静态 nested-partition theorem 不要求矩形 block；矩形 grid 只是可实现的子类。若允许执行期间动态重分块、动态 replication 或不同阶段使用不同 processor grid，就不能直接使用同一条 chain，需要 time-expanded owner labels。

## Lemma C：edge-volume additivity

慢存储↔`P₃`、`P₃↔P₂`、`P₂↔P₁` 是三条不同收费边。一个 word 经过多条边时，在每条实际边上分别计数，所以

$$
Q_vol = V₁ + V₂ + V₃.
$$

在静态 nested owner 模型中，逐边增量可以按数据类型和边权相加。对于纯 aggregate volume，增量会 telescoping 到最细 partition 的 projection boundary；对于非对称或按层归一化成本，中间 partitions 仍然影响目标。

## Arbitrary-schedule lifting target

`docs/t3-arbitrary-schedule-steiner-theorem.md` 已经给出一个不要求单一 componentwise-divisible grid chain 的结果：固定 rooted hierarchy tree 后，动态 owner labels 只需汇总成每个数据项的需求叶集合；每条 cut 上的 copy-lineage/partial-reduction indicator 给出加权 word-volume 下界，树形 broadcast/reduction 达到它。这个结果覆盖 arbitrary leaf assignment，但暂不加入容量和 phase reload。

剩下的更强目标是把 Steiner cut 与 time-expanded phase trace 接起来。`docs/finite-capacity-phase-cut-envelope.md` 已把这个接口写成 (TR-1)--(TR-5) 的联合可行域，并证明任何真实执行都映射到该 envelope；目前还没有求出其一般闭式值或 matching finite-capacity schedule。当前已证明的动态 corollary 只有

$$
∑_{ℓ=1}^{L} V_ℓ ≥ ∂(Π_fine),
$$

它不提供 finite-capacity 的逐边 phase envelope。要得到带容量的 T3-volume，还需要证明 phase/HBL 项与 cut/Steiner 项如何 charging，不能由 arrangement enumeration 单独推出。

## 必须继续检查的边界

1. 一个 word 是否可能在一次跨层传输中同时满足两个层次的 projection budget；
2. replication 是否让某层的 `V_ℓ` 低于固定-grid line；
3. 动态 grid 是否产生没有单一 chain 的执行；
4. recomputation 是否改变 HBL phase 的 product count；
5. 不平衡 work 是否绕过以 `P₁` 为基准的 phase bound。

如果任一项成立，应扩大 schedule class 或修改下界对象，而不是把反例隐藏在 `N/I` 计算之外。

## 当前验证文件

- `check_one_level_recovery.py`：验证矩形 GEMM 的 affine geometry；
- `check_three_level_model.py`：验证 grid compatibility、envelope counts 和 `N ≥ I`；
- `check_t3_static_hierarchical_theorem.py`：验证三层逐边增量定理；
- `check_nested_partition_weighted_counterexample.py`：证明非对称成本下矩形化反例；
- `check_l_level_static_theorem.py`：验证静态 `L`-level 增量定理；
- `check_t3_arbitrary_schedule_steiner.py`：枚举小树上的任意需求集合，验证 cut 下界与显式 broadcast/reduction 的边集计数一致；
- `check_finite_capacity_joint_envelope.py`：验证联合 trace 中首次加载与 phase 项的重叠算术；
- `exact_small_gemm_pebble.py`：在明确省略最终写回的 toy pebble 模型中，精确搜索 (2\times2\times2) 的 resident-state optimum；
- `check_free_replication_forest.py`：验证多 source 免费复制下的最小共享路径 forest；
- `check_shared_cache_edge_accounting.py`：验证边级 arrival 与 owner-private local load 的计费差异；
- `check_shared_cache_hbl_relaxation.py`：验证共享 cache 的显式 HBL 弱化式及其一层退化；
- `check_shared_cache_hbl_optimum.py`：验证均匀 owner 情形下 phase budget 的唯一根；
- `check_typed_projection_envelope.py`：验证 typed A/B/C projection relaxation；
- `check_typed_projection_tightness.py`：验证笛卡尔 typed phase 的 HBL 取等条件；
- `check_nested_partition_theorem.py`：穷举 \(2\times2\times2\) nested partition chains，验证逐 entry incidence 增量与 broadcast/reduction forest 计数；
- `check_trace_state_transition.py`：检查联合 trace 中 shared/arrival 到 resident state 的转移闭合；
- `check_exact_trace_phase.py`：重放最短 pebble trace，检查实际 projection 与 HBL slack；
- `exact_shared_cache_trace.py`：精确求解 \(2\times2\times2\) shared-cache operand 子模型；
- `check_shared_operand_cut_lemma.py`：验证共享 B-entry 的受限 operand cut 下界与精确 trace；
- `prove_2r_subfamily_empty_cell_certificates.py`：验证固定 divisor profile 的 arrangement cells。

因此目前最重要的下一步是对联合 trace 做小型 GEMM 的整数搜索，再补出 phase/HBL 的物理尺度推导和 matching trace，而不是继续增加 `r` 的样本。

## 状态边界

`T3-static-vector`、一般 nested-partition theorem、固定层次树上的 `T3-Steiner`
以及多 source 免费复制的 Steiner-forest 版本都已经有 matching schedule，分别
覆盖静态兼容 grid、一般静态分区、无容量 arbitrary leaf assignment 和固定
initial-source sets。recomputation 的 event-assignment 优化、拥塞，以及有限
容量 phase coupling 仍未覆盖。
