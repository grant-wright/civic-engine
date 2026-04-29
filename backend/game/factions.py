from game.state import Faction, Metrics
from game.rules import Happiness


def recompute_citizen_happiness(factions: list[Faction], metrics: Metrics) -> float:
    total_weight = sum(f.population_weight for f in factions)
    if total_weight == 0:
        return Happiness.default
    faction_component = (
        sum(f.happiness * f.population_weight for f in factions) / total_weight
    )
    return (
        (faction_component * Happiness.faction_weight)
        + (metrics.aesthetic_index * Happiness.aesthetic_weight)
    )


def faction_affected(faction: Faction, turn_summary: str) -> bool:
    """
    Cheap filter: True if any of the faction's political_sensitivities appear
    in the turn summary string.  Used in step 11 (claude/citizens.py) to decide
    which factions receive a Claude reaction call.  Does not determine whether
    the reaction is positive or negative — that is Claude's job.
    """
    summary_lower = turn_summary.lower()
    return any(s.lower() in summary_lower for s in faction.political_sensitivities)
