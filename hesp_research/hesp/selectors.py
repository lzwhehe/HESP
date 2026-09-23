"""Action-selection policies used by the controller in the HESP arm (and its ablations).

Every selector receives the same *legal* candidate list (scope, prerequisites, exact
dedup and budget already enforced) and returns one action id.
"""

import random

from .core import normalize

SELECTORS = ("eig_cost", "eig", "map_greedy", "random", "lookahead")


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


def _lookahead_value(scores, actions, cost_left, calls_left, depth, memo):
    """Expected max-posterior reachable with at most `depth` more affordable probes (Bayes accuracy)."""
    key = (scores, cost_left, calls_left, depth)
    if key in memo:
        return memo[key]
    best = max(scores)
    if depth > 0 and calls_left > 0:
        for _, cost, table in actions:
            if cost <= cost_left:
                best = max(best, _action_value(scores, table, actions, cost_left - cost, calls_left - 1,
                                               depth - 1, memo))
    memo[key] = best
    return best


def _action_value(scores, table, actions, cost_left, calls_left, depth, memo):
    total = 0.0
    for o in range(len(table[0])):
        joint = [p * row[o] for p, row in zip(scores, table)]
        mass = sum(joint)
        if mass > 0:
            post = tuple(round(j / mass, 6) for j in joint)
            total += mass * _lookahead_value(post, actions, cost_left, calls_left, depth, memo)
    return total


class Selector:
    def __init__(self, name="eig_cost", seed=0):
        if name not in SELECTORS:
            raise ValueError("Unknown selector")
        self.name = name
        self.rng = random.Random(seed)

    def choose(self, rankings, scores, action_map, remaining_cost=None, remaining_calls=None):
        if not rankings:
            return None
        if self.name == "lookahead":
            return self._lookahead(rankings, scores, action_map, remaining_cost, remaining_calls)
        if self.name == "eig_cost":
            key = lambda r: (-r["score"], r["action_id"])
        elif self.name == "eig":
            key = lambda r: (-r["expected_information_gain_bits"], r["cost"], r["action_id"])
        elif self.name == "map_greedy":
            key = lambda r: (-round(_map_contrast(scores, action_map[r["action_id"]]), 12), r["cost"], r["action_id"])
        else:
            return self.rng.choice(sorted(r["action_id"] for r in rankings))
        return min(rankings, key=key)["action_id"]

    def _lookahead(self, rankings, scores, action_map, remaining_cost, remaining_calls, depth=3):
        """Budget-aware: maximize expected max-posterior after spending the remaining budget
        (depth-limited expectimax under the supplied predictive model). Ties -> EIG / cost."""
        hyps = sorted(scores)
        probs = normalize(scores)
        state = tuple(probs[h] for h in hyps)
        cost_left = remaining_cost if remaining_cost is not None else max(r["cost"] for r in rankings)
        calls_left = remaining_calls if remaining_calls is not None else depth
        actions = []
        for r in rankings:
            a = action_map[r["action_id"]]
            outs = a.outcomes()
            actions.append((a.id, a.cost, tuple(tuple(a.likelihoods[h][o] for o in outs) for h in hyps)))
        memo, best, best_key = {}, None, None
        for (aid, cost, table), r in zip(actions, rankings):
            if cost > cost_left:
                continue
            value = _action_value(state, table, actions, cost_left - cost, calls_left - 1,
                                  min(depth, calls_left) - 1, memo)
            key = (-round(value, 9), -r["score"], aid)
            if best_key is None or key < best_key:
                best, best_key = aid, key
        return best
