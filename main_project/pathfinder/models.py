from dataclasses import dataclass
from typing import Dict

@dataclass
class Coordinate:
    lat: float
    lng: float

@dataclass
class Node:
    id: int
    coord: Coordinate
    connections: Dict[int, float]  # node_id -> distance
    node_type: str  # 'intersection', 'waypoint', etc.