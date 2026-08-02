# Conclusion

<!-- FILL:verdicts -->
*(pending release run)*
<!-- /FILL -->

Full detail per claim is on [Current verification (2026-08-03)](#/current-verification)
and the six claim pages linked from it.

## What CARE's evaluation survives, and what it does not

**The method holds up where it can be checked, which is two columns of twelve.** On
CivilComments (Table 2) and ASSET (Table 1), CARE reproduces with the authors' own code
at `72f5b29`, over five seeds — against all nine competing methods on CivilComments and
all five on ASSET. The third released column, PKU-BETTER, yielded no number: its labels
are degenerate and it is BLOCKED, not reproduced.
That is the paper's real benchmark data, not a synthetic stand-in, and it directly
answers the earlier judgement that this reproduction tested nothing on the paper's
actual benchmarks.

**Claim 3's official generated conjunction is false even though its nearby paper prose is
correct.** The generated claim explicitly couples 13.4% to `0.814 vs 0.705`; exact rational
arithmetic gives 15.461%. Replacing only 0.705 with GLAD's actual strongest-baseline value
0.718 gives 13.3705%, recovering the paper's nearby prose. A second hand transcription of
all 54 Table 2 cells independently confirms both results and the surviving 5-of-6
conjunct. This is a literal falsification with a positive repair control, independent of
the unreleased benchmark matrices.

**The headline percentages are exact, but one of them is fragile.** Requiring 17.37 %
and 12.75 % *simultaneously* identifies the paper's definition of "average improvement"
uniquely: the pooled mean-MAE ratio. That definition pools unnormalised MAEs across
datasets on incommensurable scales, so ASSET's 0–100 scale sets nearly the whole figure.
Under the scale-free reading the improvement over AVG is smaller than published and the
improvement over MV is larger. Both are reported; neither is presented as the other.

**The paper disagrees with itself about the row that headline is computed from.**
Appendix E.8's Table 7 republishes CARE-SVD's six Table 1 MAEs, under a sentence that
says the setup is the same. Four columns match; FeedbackQA does not, by more than the
paper's own reported seed noise allows, and ASSET does not marginally. Recomputed from
the appendix's own row the average improvement is a different number. The audit needs no
data, and it is not one-sided: the same comparison **corroborates** Claim 1's
UltraFeedback value, which is the one quantity in this campaign we have no way to
measure ourselves.

**The main-text Proposition 4.1 is false as written, and the appendix version is not.**
The main text asks only for *orthogonal* columns, and asserts a stability bound free of
`‖K_JH‖₂` that the appendix earns only by assuming orthonormality (its proof carries
`‖K_JH‖₂` and discharges it with `‖K_JH‖₂ = 1`). Each
omission admits an exact counterexample that satisfies the main text's own hypotheses,
and the second grows without bound, so no hidden constant in the `≲` rescues it. The
appendix statement survives both, and we derive a strictly tighter constant — 2 rather
than 4 — for its perturbation bound. None of this threatens Algorithm 1, which works
with the eigenvectors of `L̂` regardless.

**Theorem 4.2 is false as literally stated.** D.5 omits the sign alignment that D.4
includes, so an equally valid `-u` has distance 2 at exact recovery against a zero
right-hand side. More substantively, D.5 defines `δ` only between positive eigenvalues,
omitting the last direction's separation from the zero eigenspace required by the cited
Yu–Wang–Samworth result. An exact family makes the paper-normalized perturbation ratio
diverge while the full-gap control stays bounded. A Gaussian two-point Le Cam argument
then forces every estimator to exceed a fixed eigenvector-error threshold with probability
above 0.436, beyond D.5's 0.0996 failure budget, while its advertised paper-gap rate tends
to zero. An independent 2x2 trace/log-determinant route agrees. The prior finite-grid
corroboration remains published, but it no longer carries the verdict.

**Theorem 4.3's displayed proof is defective; the theorem itself is not thereby decided.**
Composing the paper's own cited results reproduces its mean bound exactly and overshoots
its stated weight bound by exactly `σ³` — an unbounded factor no universal constant can
absorb. That is reached twice, by independent routes, and is exact. Whether the stated
weight bound *itself* fails is **undecided here**: the boundary probe meant to settle it
turns out to be uninformative, and the earlier revisions that read it as corroborating
the bound were relying on a normal quantile applied to a five-point fit.

A previous revision of this logbook additionally reported the stated `p·log(p/ε)`
sample-complexity factor as **FALSIFIED**. **That finding has been withdrawn.** Its
supporting agreement test compared only aggregate slope intervals while the two `n*`
estimators disagreed per setting by up to 8.6× in opposite directions, and the audit
meant to make the exponent attributable was assembled from `p`-independent constants.
Rebuilt to measure the model actually constructed at each `p`, that audit finds a real
confound — at fixed `n` the empirical second moment degrades as dimension grows — so no
falsification may rest on the exponent. The `σ⁶` and `π_min^{-2}` exponents remain NOT
MEASURED: both sweeps failed the admissibility test rather than passing a one-sided
contract by default.

## What this reproduction got wrong

Several findings went against our own hypotheses, and they are published rather than
dropped — see [Limitations and deviations](#/limitations). Three verdicts this campaign
reached were later withdrawn on its own evidence, before or without reaching a judged
revision; each withdrawal is recorded with the reasoning that produced it.

* We predicted the missing `σ³` factor in Theorem 4.3 would be *observable* along the
  sample-complexity boundary. It was not. The verdict was downgraded from FALSIFIED to a
  documented proof gap. Reporting the falsification would have been the more striking
  result and the wrong one. A later revision then reported a falsification of a
  *different* factor of the same theorem, by a different route; that one has since been
  withdrawn as well, by this logbook's own verifier. **No falsification of Theorem 4.3's
  *sample-complexity condition* survives.** What does survive, untouched by any of this,
  is the symbolic result on its second displayed bound: composing the paper's own (8) and
  (11) overshoots the stated weight bound by exactly `σ_max³`, so that bound's **displayed
  proof is falsified** — exactly, with no tolerance and no seed, by two independent
  routes. The withdrawals above are about the *empirical* probes of the theorem's
  condition, not about that derivation.
* **And the corroboration we replaced that falsification with was also wrong.** Having
  withdrawn the `σ` falsification on the strength of a boundary probe whose interval
  "excluded" the slope a missing `σ³` predicts, we then found the interval had been built
  with the normal 1.96 on a five-point, three-degrees-of-freedom fit. At its correct width
  it excludes neither hypothesis, and the probe's two estimators disagree eightfold. The
  probe decides nothing in either direction. Every interval in this campaign now uses
  `t(0.975, n−2)` from a single helper — the fix is one line, and it removes a published
  conclusion rather than adding one.
* An earlier revision of the Claim 6 page passed a sample-complexity check that had
  measured nothing: with the search grid floored at `n = 5 000`, every `π_min` setting
  returned `n* = 5 000`, giving an exponent of `0.000 ± 0.000` that satisfied a one-sided
  contract on a constant. The grid was extended, an admissibility precondition was made
  machine-checkable, and on the current run **all three** sweeps are reported as NOT
  MEASURED — the `p` sweep joined them once its interval was computed with the correct
  `t` quantile for a three-point fit.
* Our own sparse-plus-low-rank solver does not reach `n^{-1/2}` end-to-end at its
  iteration budget. Rather than quote only the flattering stage, the error is decomposed
  so that the theorem-governed stage and the implementation-limited stage are reported
  separately, each labelled for what it is.

## What remains blocked, and why

Nine of the twelve benchmark columns have no released judge-score matrix.
Regenerating one needs GPU inference over 11–20 LLM judges — the paper's own Appendix
E.2 reports up to three hours per dataset on an A100 — and this campaign is authorised
for CPU only. Those columns are recorded BLOCKED against that named capability. They are
**not** replaced by synthetic judges, which is precisely what the superseded 2026-07-30
revision did and what the judge correctly rejected.

A second obstacle would remain even with a GPU: the published MAE of 0.623 ± 0.006 is a
property of *the authors' particular judge outputs*. Re-running the judges under a
different serving stack yields a different score matrix, so those three decimal places
are not recoverable by regeneration at all — only the released matrices can decide them.
