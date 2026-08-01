# Conclusion

<!-- FILL:verdicts -->
*(pending release run)*
<!-- /FILL -->

Full detail per claim is on [Current verification (2026-08-01)](#/current-verification)
and the six claim pages linked from it.

## What CARE's evaluation survives, and what it does not

**The method holds up where it can be checked.** On the two Table 2 columns and the one
Table 1 column whose judge-score matrices the authors released, CARE reproduces with the
authors' own code at `72f5b29`, over five seeds, against all nine competing methods.
That is the paper's real benchmark data, not a synthetic stand-in, and it directly
answers the earlier judgement that this reproduction tested nothing on the paper's
actual benchmarks.

**The headline percentages are exact, but one of them is fragile.** Requiring 17.37 %
and 12.75 % *simultaneously* identifies the paper's definition of "average improvement"
uniquely: the pooled mean-MAE ratio. That definition pools unnormalised MAEs across
datasets on incommensurable scales, so ASSET's 0–100 scale sets nearly the whole figure.
Under the scale-free reading the improvement over AVG is smaller than published and the
improvement over MV is larger. Both are reported; neither is presented as the other.

**The main-text Proposition 4.1 is false as written, and the appendix version is not.**
The main text asks only for *orthogonal* columns and drops the `‖K_JH‖₂²` factor. Each
omission admits an exact counterexample that satisfies the main text's own hypotheses,
and the second grows without bound, so no hidden constant in the `≲` rescues it. The
appendix statement survives both, and we derive a strictly tighter constant — 2 rather
than 4 — for its perturbation bound. None of this threatens Algorithm 1, which works
with the eigenvectors of `L̂` regardless.

**Theorem 4.2 is corroborated with named gaps rather than declared closed.** Its
composition and its cited Davis–Kahan constant are established directly, but its
`η`-dependence is a tail statement we do not measure and `ξ(T)` has no closed form we
can evaluate. Recorded as MEDIUM confidence with the reason attached.

**Theorem 4.3 is partly verified and partly falsified.** Its mean bound is reproduced
exactly and its weight bound is not violated along its own `σ` boundary, but the
displayed proof of that weight bound loses a `σ³` factor. Separately, the stated
`p·log(p/ε)` sample-complexity factor is **FALSIFIED**: with every other quantity in the
bound held fixed, `n*` grows as `(p·log(p/ε))^{3.63 ± 0.80}` against a stated exponent
of 1. The `σ⁶` and `π_min^{-2}` exponents are reported as NOT MEASURED — both sweeps
failed the admissibility test rather than passing a one-sided contract by default.

## What this reproduction got wrong

Two findings went against our own hypotheses, and both are published rather than
dropped — see [Limitations and deviations](#/limitations), items 10 and 11.

* We predicted the missing `σ³` factor in Theorem 4.3 would be *observable* along the
  sample-complexity boundary. It was not. The verdict was downgraded from FALSIFIED to a
  documented proof gap. Reporting the falsification would have been the more striking
  result and the wrong one. (The falsification this logbook *does* report is of a
  different factor, reached by a different route, and gated on three audits written
  before its outcome was known.)
* An earlier revision of the Claim 6 page passed a sample-complexity check that had
  measured nothing: with the search grid floored at `n = 5 000`, every `π_min` setting
  returned `n* = 5 000`, giving an exponent of `0.000 ± 0.000` that satisfied a one-sided
  contract on a constant. The grid was extended, an admissibility precondition was made
  machine-checkable, and two of the three sweeps are now reported as NOT MEASURED.
* Our own sparse-plus-low-rank solver does not reach `n^{-1/2}` end-to-end at its
  iteration budget. Rather than quote only the flattering stage, the error is decomposed
  so that the theorem-governed stage and the implementation-limited stage are reported
  separately, each labelled for what it is.

## What remains blocked, and why

Eight of the fourteen benchmark columns have no released judge-score matrix.
Regenerating one needs GPU inference over 11–20 LLM judges — the paper's own Appendix
E.2 reports up to three hours per dataset on an A100 — and this campaign is authorised
for CPU only. Those columns are recorded BLOCKED against that named capability. They are
**not** replaced by synthetic judges, which is precisely what the superseded 2026-07-30
revision did and what the judge correctly rejected.

A second obstacle would remain even with a GPU: the published MAE of 0.623 ± 0.006 is a
property of *the authors' particular judge outputs*. Re-running the judges under a
different serving stack yields a different score matrix, so those three decimal places
are not recoverable by regeneration at all — only the released matrices can decide them.
