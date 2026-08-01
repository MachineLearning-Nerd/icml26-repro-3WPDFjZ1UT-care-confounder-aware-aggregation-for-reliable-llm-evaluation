"""Frozen paper source of truth for arXiv 2603.00039 (CARE).

Every number here was transcribed from the ar5iv HTML render whose SHA-256 is
recorded in SOURCE. Nothing downstream may edit these values; verifiers compare
against them.
"""

from __future__ import annotations

SOURCE = {
    "arxiv_id": "2603.00039",
    "openreview": "3WPDFjZ1UT",
    "url": "https://ar5iv.labs.arxiv.org/html/2603.00039",
    "retrieved_utc": "2026-08-01T04:20:00Z",
    "sha256": "2e733a1609e1dd907dd839b9eed8d9fb7d88549f45d40fafbca7af94ee5e77ea",
    "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/120 Safari/537.36",
    "official_code": "https://github.com/SprocketLab/CARE",
    "official_code_sha": "72f5b29a822d9934d31777c10a5c38369884c9dc",
}

# Table 1: MAE (lower is better) across continuous-scoring datasets.
TABLE1_DATASETS = ["ASSET", "FeedbackQA", "Review-5K", "Summarize", "UltraFeedback", "Yelp"]
TABLE1_MAE = {
    "MV":       [31.153, 0.822, 2.608, 1.417, 0.851, 0.923],
    "AVG":      [33.663, 0.830, 2.274, 1.394, 0.686, 1.037],
    "WS":       [29.073, 0.793, 2.593, 1.364, 0.829, 0.977],
    "UWS":      [33.928, 0.875, 2.602, 1.362, 0.680, 0.987],
    "CARE-SVD": [27.629, 0.730, 1.957, 1.325, 0.623, 0.694],
}
TABLE1_STD = {
    "MV":       [0.000, 0.000, 0.000, 0.000, 0.000, 0.000],
    "AVG":      [0.000, 0.000, 0.000, 0.000, 0.000, 0.000],
    "WS":       [0.436, 0.009, 0.052, 0.007, 0.009, 0.008],
    "UWS":      [0.000, 0.000, 0.000, 0.000, 0.000, 0.000],
    "CARE-SVD": [0.156, 0.002, 0.018, 0.004, 0.006, 0.004],
}

# Table 2: Accuracy (higher is better) across classification / preference datasets.
TABLE2_DATASETS = [
    "Chatbot-Arena", "CivilComments", "PKU-BETTER", "PKU-SAFER", "SHP", "Summarize",
]
TABLE2_ACC = {
    "MV":           [0.517, 0.691, 0.701, 0.698, 0.626, 0.600],
    "AVG":          [0.551, 0.690, 0.726, 0.717, 0.634, 0.683],
    "WS":           [0.543, 0.739, 0.575, 0.570, 0.619, 0.705],
    "UWS":          [0.507, 0.713, 0.703, 0.701, 0.629, 0.713],
    "Dawid-Skene":  [0.546, 0.735, 0.551, 0.548, 0.612, 0.705],
    "GLAD":         [0.510, 0.695, 0.697, 0.671, 0.644, 0.718],
    "MACE":         [0.550, 0.732, 0.734, 0.735, 0.580, 0.706],
    "CARE-SVD":     [0.580, 0.778, 0.691, 0.690, 0.543, 0.695],
    "CARE-Tensor":  [0.564, 0.749, 0.779, 0.731, 0.695, 0.814],
}
TABLE2_BASELINES = ["MV", "AVG", "WS", "UWS", "Dawid-Skene", "GLAD", "MACE"]
TABLE2_CARE = ["CARE-SVD", "CARE-Tensor"]
# Bold (best) cell per column as typeset in the paper.
TABLE2_BOLD = {
    "Chatbot-Arena": "CARE-SVD",
    "CivilComments": "CARE-SVD",
    "PKU-BETTER": "CARE-Tensor",
    "PKU-SAFER": "MACE",
    "SHP": "CARE-Tensor",
    "Summarize": "CARE-Tensor",
}

# Prose quantifiers under test (Section 5.1).
PROSE = {
    "ultrafeedback_mv_reduction_pct": 26.8,
    "avg_relative_improvement_over_AVG_pct": 17.37,
    "avg_relative_improvement_over_MV_pct": 12.75,
    "table2_best_of_n_datasets": (5, 6),
    "table2_care_tensor_leads_on": ["PKU-BETTER", "SHP", "Summarize"],
    "summarize_relative_improvement_pct": 13.4,
    # The claim string circulated with this reproduction quotes
    # "0.814 +- 0.001 vs 0.705 +- 0.000" for the Summarize comparison. 0.705 is the
    # WS / Dawid-Skene entry, not the strongest baseline on that column; the paper's
    # own words are "over the strongest baseline", which is GLAD at 0.718. Both
    # readings are decided explicitly by the verifier.
    "summarize_claimstring_pair": (0.814, 0.705),
}

# Datasets for which the authors released judge-score matrices in the official repo.
# Everything else in Tables 1-2 requires re-running 11-20 LLM judges, which the
# paper itself (Appendix E.2) reports doing on an NVIDIA A100.
RELEASED_JUDGE_OUTPUTS = {
    "table1": ["ASSET"],
    "table2": ["CivilComments", "PKU-BETTER"],
}
