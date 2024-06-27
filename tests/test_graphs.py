# (C) Copyright 2024 European Centre for Medium-Range Weather Forecasts.
# This software is licensed under the terms of the Apache Licence Version 2.0
# which can be obtained at http://www.apache.org/licenses/LICENSE-2.0.
# In applying this licence, ECMWF does not waive the privileges and immunities
# granted to it by virtue of its status as an intergovernmental organisation
# nor does it submit to any jurisdiction.


from pathlib import Path

import torch
from torch_geometric.data import HeteroData

from anemoi.graphs import create


def test_graphs(config_file: tuple[Path, str], mock_grids_path: tuple[str, int]):
    """Test GraphCreator workflow."""
    tmp_path, config_name = config_file
    graph_path = tmp_path / "graph.pt"
    config_path = tmp_path / config_name

    create.GraphCreator(graph_path, config_path).create()

    graph = torch.load(graph_path)
    assert isinstance(graph, HeteroData)
    assert "test_nodes" in graph.node_types
    assert ("test_nodes", "to", "test_nodes") in graph.edge_types
