# Hypothesis scoring and ranking logic.
# Rule weights: recent deploy to affected service, dependency-chain timing, past-incident similarity.
# Produce 2-3 ranked hypotheses with evidence_score and supporting_evidence[] for eval top-1/top-3 accuracy.
