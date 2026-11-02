from mapmatching.repositories.base_repository import BaseRepository

from mapmatching.models.node import Node
from mapmatching.models.coordinate import Coordinate 

class NodeRepository(BaseRepository):

    def get_all(self) -> tuple[Node,...]:
        rows = self.fetch("SELECT osmid, x, y FROM osm_nodes")
        return tuple(self.convert_to_node(row) for row in rows)

    def convert_to_node(self, row: tuple) -> Node:
            return Node(
                id=row[0],
                coordinate=Coordinate(row[1], row[2])
            )