import networkx as nx

from game.state import CityMap, CanalTier, SegmentStatus, Metrics, NodeType
from game.rules import CanalEfficiency


def check_canal_connectivity(city_map: CityMap) -> CanalTier:
    """
    Return the highest canal tier the network currently achieves.

    G is built from complete segments only.  A major node absent from G simply
    means no complete canal touches it yet — that is normal early-game state
    and produces CanalTier.NONE.  A major node that does not exist in
    city_map.nodes at all is a map-generation error and should be caught at
    setup time (not handled here).

    Tiers:
        BRONZE: all PORT+INDUSTRIAL nodes reachable from each other.
        SILVER: Bronze + all RESIDENTIAL nodes in the same component.
        GOLD:   80%+ of all districts in the connected component.
    """
    G = nx.Graph()
    for seg in city_map.canal_segments.values():
        if seg.status == SegmentStatus.COMPLETE:
            G.add_edge(seg.from_node, seg.to_node)

    major = city_map.get_major_nodes()
    if not major:
        return CanalTier.NONE

    # None of the major nodes have a complete canal touching them yet.
    if not all(G.has_node(n) for n in major):
        return CanalTier.NONE

    # All major nodes must be in the same connected component.
    major_component = nx.node_connected_component(G, major[0])
    if not all(n in major_component for n in major[1:]):
        return CanalTier.NONE

    # Bronze achieved — check Silver and Gold.
    all_nodes = list(city_map.nodes.keys())
    if not all_nodes:
        return CanalTier.BRONZE

    # Gold: sufficient fraction of all districts in the connected canal component.
    coverage = len(major_component) / len(all_nodes)
    if coverage >= CanalEfficiency.gold_coverage_threshold:
        return CanalTier.GOLD

    # Silver: all RESIDENTIAL nodes also reachable.
    residential = [
        n for n, data in city_map.nodes.items()
        if data.node_type == NodeType.RESIDENTIAL
    ]
    if residential and all(n in major_component for n in residential):
        return CanalTier.SILVER

    return CanalTier.BRONZE


def recompute_canal_efficiency(city_map: CityMap, metrics: Metrics) -> None:
    tier = check_canal_connectivity(city_map)
    base = metrics.canal_freight_pct * CanalEfficiency.freight_factor
    network_bonus = {
        CanalTier.BRONZE: CanalEfficiency.bronze_bonus,
        CanalTier.SILVER: CanalEfficiency.silver_bonus,
        CanalTier.GOLD:   CanalEfficiency.gold_bonus,
    }
    metrics.canal_efficiency_index = min(100.0, base + network_bonus.get(tier, 0.0))
