# Conversation thread summary

The exploration began with the classical two-level matrix multiplication lower bound

\[
Q(n,M)=\Omega\left(n^2+\frac{n^3}{\sqrt M}\right),
\]

and the Loomis–Whitney explanation that $M$ fast-memory words support only $O(M^{3/2})$ scalar products per communication phase.

The literature discussion then separated several settings:

- Hong–Kung and classical sequential GEMM;
- Strassen-like algorithms and recomputation;
- distributed-memory and processor-grid lower bounds;
- two-level versus multilevel hierarchies;
- structured kernels and asymmetric memories.

The current research direction is to test whether a structured multilevel model leaves a genuinely open tight-bound problem after the general parallel GEMM results. Exact two-dimensional arrangements were chosen because they expose the lower envelopes, compatible nested chains, and aspect-ratio transitions without hiding the constants.

The main computational discovery is that a simple prime-family formula extends to a special composite profile $p=2r, q=4r+3$ for many cases, but fails for other factor profiles such as $p=18$. This motivated the current proof-gap workflow: prove the independent envelope, add enough compatible nested chains, enumerate cells exactly, then separate full-dimensional cells, empty combinations, and parameter-degenerate cells.

The present repository preserves the notes and scripts produced during that process. Claims are intentionally labeled as exact finite results, symbolic branch certificates, empirical sweeps, or open proof obligations.
