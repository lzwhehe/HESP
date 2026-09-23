"""Sources of the pre-registered predictive model P(o | h, a), and calibration metrics."""

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
