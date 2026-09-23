"""Action-selection policies used by the controller in the HESP arm (and its ablations).

Every selector receives the same *legal* candidate list (scope, prerequisites, exact
dedup and budget already enforced) and returns one action id.
"""

import random

from .core import normalize

SELECTORS = ("eig_cost", "eig", "map_greedy", "random")


def _map_contrast(scores, action):
    """Confirmation contrast for the current MAP hypothesis (positive-test strategy)."""
    scores = normalize(scores)
    top = max(sorted(scores), key=lambda h: scores[h])
    rest = 1 - scores[top]
    best = 0.0
    for o in action.outcomes():
        others = (sum(scores[h] * action.likelihoods[h][o] for h in scores if h != top) / rest) if rest > 0 else 0
        best = max(best, action.likelihoods[top][o] - others)
    return best


class Selector:
    def __init__(self, name="eig_cost", seed=0):
        if name not in SELECTORS:
            raise ValueError("Unknown selector")
        self.name = name
        self.rng = random.Random(seed)

    def choose(self, rankings, scores, action_map):
        if not rankings:
            return None
        if self.name == "eig_cost":
            key = lambda r: (-r["score"], r["action_id"])
        elif self.name == "eig":
            key = lambda r: (-r["expected_information_gain_bits"], r["cost"], r["action_id"])
        elif self.name == "map_greedy":
            key = lambda r: (-round(_map_contrast(scores, action_map[r["action_id"]]), 12), r["cost"], r["action_id"])
        else:
            return self.rng.choice(sorted(r["action_id"] for r in rankings))
        return min(rankings, key=key)["action_id"]
