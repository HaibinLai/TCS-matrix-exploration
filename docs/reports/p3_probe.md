# p=3 small-prime probe

本轮用 exact overlay 和有理数拓扑扫描检查了三层模型

\[
(P_1,P_2,P_3)=(6q,3q,3),\qquad q>3,
\]

其中 aspect-ratio domain 是 $0\le y\le z\le1$，并比较三个 independent
lower envelopes 与 coordinatewise-divisible nested chains。

## 直接 exact overlay

素数 $q$ 的若干结果都在 $(z,y)=(1,1/3)$ 达到最大值，并等于 endpoint
表达式

\[
R_3(q)=\frac{27q+21}{21q+39}.
\]

已直接检查小于 300 的全部 60 个 prime $q$，没有发现 endpoint 公式失败。
例如 $R_3(47)=215/171$，$R_3(97)=220/173$。

但不能把这个现象直接推广到所有整数 $q>3$：$q=44$ 的 exact overlay 最大值是

\[
\frac{311}{299}\approx1.04013,
\]

而 endpoint 公式给出 $403/321\approx1.25545$。这个失败来自 composite grid
的因子结构；因此这里的“prime $q$”条件是实质性的。

## 参数化 topology 检查

早期辅助脚本曾把含 anchor factor 的乘积错误地取了整数 floor，得到 $2/87$ 和
$2/141$；这些数值已撤销。修正为正确的 symbolic replacement 后，$q_0=29,47,61$
的 cover 都显示同一个 active triple event：

\[
u=1/66,
\qquad (z,y)=(0,0).
\]

这个 event 落在这些 anchor 的 $0<u\le1/q_0$ 区间内。取 $q_0=67$ 后，区间变成
$0<u\le1/67<1/66$。`prove_p3_envelope_stability.py` 进一步对全部 grid 和全部
coordinatewise-compatible nested chains 做了 symbolic endpoint dominance：

```text
independent[0] total=27 active=16 uncovered=0
independent[1] total=9 active=8 uncovered=0
independent[2] total=3 active=3 uncovered=0
nested total=27 active=16 uncovered=0
```

随后 exact quadratic Sturm scan（31 个 unique determinants）和 linear event scan 都没有
active event；q0-visible ratio candidate 的 54 个分支也全部通过 exact sign check。

## 当前结论

1. p=3 的 prime-$q$ endpoint witness 在抽样范围内稳定；以 $q_0=67$ 为起点时，已经有
   对全部 grid 的 fixed-cover dominance certificate，以及覆盖 prime $q\ge67$ 的 ratio
   certificate 候选。
2. composite $q$ 会改变 divisor grid，不能只用 prime-$q$ 公式。
3. event $u=1/66$ 说明 anchor 不能随意选；下一步是把 $q_0=67$ 的 topology-continuity
   与 ratio candidate 覆盖整理成正式 lemma，再检查 prime $p=5,7$ 是否有相同现象。

复现实验脚本：

- `work/check_p3_quadratic_sturm.py`
- `work/check_p3_linear_events.py`
- `work/p3probe/check_p3_ratio_candidate_family.py`
- `work/prove_p3_envelope_stability.py`
- `work/exact_overlay_2d.py --pstars 282 141 3` (replace 282/141 by 6q/3q for a chosen q)
