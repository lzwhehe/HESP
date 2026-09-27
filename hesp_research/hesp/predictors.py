"""Sources of the pre-registered predictive model P(o | h, a), and calibration metrics."""

from collections import defaultdict
import math


class TablePredictor:
    """Use the environment catalogue's designer table unchanged."""
    source = "designer_table"

    def likelihoods(self, action, hypotheses):
        return action.likelihoods


class FrozenPredictor:
    """Replay tables elicited earlier (e.g. loaded from a study's elicitation.json)."""

    def __init__(self, tables, source):
        self.tables, self.source = tables, source

    def likelihoods(self, action, hypotheses):
        return self.tables[action.id]


class EmpiricalEstimator:
    """Estimate P(o | h, a) by counting observed outcomes (PROTOCOL.md v0.6, RQ3).

    This is the non-oracle prediction source. It never sees the environment's generative
    function ``true_outcome_distribution`` -- it only counts what probing actually returned,
    exactly as a deployment would have to. Unobserved outcomes receive the epsilon share
    only, so a cell that was never exercised degrades to near-uniform rather than to a
    confident wrong answer.
    """

    def __init__(self, eps=0.01):
        self.eps = eps
        self.counts = defaultdict(lambda: defaultdict(int))
        self.episodes = 0
        self.skipped_invalid = 0

    def snapshot(self):
        """Independent copy of the current counts (for nested data-efficiency curves)."""
        copy = EmpiricalEstimator(eps=self.eps)
        for key, row in self.counts.items():
            copy.counts[key].update(row)
        copy.episodes, copy.skipped_invalid = self.episodes, self.skipped_invalid
        return copy

    def observe(self, action_id, hypothesis, outcome):
        self.counts[(action_id, hypothesis)][outcome] += 1

    def tables(self, catalog, hypotheses):
        """Smoothed tables keyed by action id; ``catalog`` supplies each action's vocabulary."""
        out = {}
        for action in catalog:
            vocab = list(action.outcome_notes)
            rows = {}
            for h in hypotheses:
                seen = self.counts.get((action.id, h), {})
                total = sum(seen.values())
                row = {o: (seen.get(o, 0) / total if total else 0.0) * (1 - self.eps) + self.eps / len(vocab)
                       for o in vocab}
                norm = sum(row.values())
                rows[h] = {o: v / norm for o, v in row.items()}
            out[action.id] = rows
        return out

    def coverage(self, catalog, hypotheses):
        """Share of (action, hypothesis) cells that were observed at least once."""
        cells = [(a.id, h) for a in catalog for h in hypotheses]
        return sum(1 for c in cells if self.counts.get(c)) / len(cells)


def calibration(pred_tables, true_fn, hypotheses, action_ids):
    """Compare predicted rows with the true outcome distribution, cell by cell.

    Returns mean expected log-loss (bits), mean KL(true || pred) in bits, mean expected
    multi-class Brier score, and the fraction of cells whose most-likely outcome matches.
    """
    cells = []
    for a in action_ids:
        for h in hypotheses:
            p, q = pred_tables[a][h], true_fn(a, h)
            logloss = sum(qo * -math.log2(max(p.get(o, 0.0), 1e-12)) for o, qo in q.items() if qo > 0)
            ent = sum(-qo * math.log2(qo) for qo in q.values() if qo > 0)
            brier = sum(qo * sum((p.get(o2, 0.0) - (1.0 if o2 == o else 0.0)) ** 2 for o2 in p)
                        for o, qo in q.items())
            agree = max(p, key=p.get) == max(q, key=q.get)
            cells.append((logloss, logloss - ent, brier, agree))
    n = len(cells)
    return {"cells": n,
            "expected_log_loss_bits": sum(c[0] for c in cells) / n,
            "kl_bits": sum(c[1] for c in cells) / n,
            "expected_brier": sum(c[2] for c in cells) / n,
            "argmax_agreement": sum(c[3] for c in cells) / n}
