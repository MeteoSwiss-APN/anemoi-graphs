from typing import Optional

import numpy as np
import torch
from sklearn.neighbors import NearestNeighbors


def get_nearest_neighbour(coords_rad: torch.Tensor, mask: Optional[torch.Tensor] = None) -> NearestNeighbors:
    """Get NearestNeighbour object fitted to coordinates.

    Parameters
    ----------
    coords_rad : torch.Tensor
        corrdinates in radians
    mask : Optional[torch.Tensor], optional
        mask to remove nodes, by default None

    Returns
    -------
    NearestNeighbors
        fitted NearestNeighbour object
    """
    assert mask is None or mask.shape == (coords_rad.shape[0], 1), "Mask must have the same shape as the number of nodes."

    nearest_neighbour = NearestNeighbors(metric="haversine", n_jobs=4)

    nearest_neighbour.fit(coords_rad)

    return nearest_neighbour


def get_grid_reference_distance(coords_rad: torch.Tensor, mask: Optional[torch.Tensor] = None) -> float:
    """Get the reference distance of the grid.

    It is the maximum distance of a node in the mesh with respect to its nearest neighbour.

    Parameters
    ----------
    coords_rad : torch.Tensor
        corrdinates in radians
    mask : Optional[torch.Tensor], optional
        mask to remove nodes, by default None

    Returns
    -------
    float
        The reference distance of the grid.
    """
    nearest_neighbours = get_nearest_neighbour(coords_rad, mask)
    dists, _ = nearest_neighbours.kneighbors(coords_rad, n_neighbors=2, return_distance=True)
    return dists[dists > 0].max()


def add_margin(lats: np.ndarray, lons: np.ndarray, margin: float) -> tuple[np.ndarray, np.ndarray]:
    """Add a margin to the convex hull of the points considered.

    For each point (lat, lon) add 8 points around it, each at a distance of `margin` from the original point.

    Arguments
    ---------
    lats : np.ndarray
        Latitudes of the points considered.
    lons : np.ndarray
        Longitudes of the points considered.
    margin : float
        The margin to add to the convex hull.

    Returns
    -------
    latitudes : np.ndarray
        Latitudes of the points considered, including the margin.
    longitudes : np.ndarray
        Longitudes of the points considered, including the margin.
    """
    assert margin >= 0, "Margin must be non-negative"
    if margin == 0:
        return lats, lons

    latitudes, longitudes = [], []
    for lat_sign in [-1, 0, 1]:
        for lon_sign in [-1, 0, 1]:
            latitudes.append(lats + lat_sign * margin)
            longitudes.append(lons + lon_sign * margin)

    return np.concatenate(latitudes), np.concatenate(longitudes)


def get_index_in_outer_join(vector: torch.Tensor, tensor: torch.Tensor) -> int:
    """Index position of vector.

    Get the index position of a vector in a matrix.

    Parameters
    ----------
    vector : torch.Tensor of shape (N, )
        Vector to get its position in the matrix.
    tensor : torch.Tensor of shape (M, N,)
        Tensor in which the position is searched.

    Returns
    -------
    int
        Index position of the tensor in the other tensor. -1 if tensor1 is not in tensor2
    """
    mask = torch.all(tensor == vector, axis=1)
    if mask.any():
        return int(torch.where(mask)[0])
    return -1
