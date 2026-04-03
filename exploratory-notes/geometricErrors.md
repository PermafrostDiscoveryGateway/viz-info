# Geometric Errors & Bounding Volume Notes (Lake Change Layer)

## Original Issue
We staged the Lake Change layer at z = 13, and we needed to create a pyramid of 3dtiles so that the files would load on the portal.

## Pyramid Layout
After using the viz-workflow functions for creating parent tiles, we weren't able to see the lake vectors until we were zoomed in all the way to z = 13 on the Cesium map. 

## Geometric Errors
There are 3 types of geometric errors in a json tile file: 
- [asset](https://github.com/PermafrostDiscoveryGateway/viz-3dtiles/blob/main/pdg3dtiles/TreeGenerator.py#L233): is chosen by taking the max of the children's geometric errors
- [root](https://github.com/PermafrostDiscoveryGateway/viz-3dtiles/blob/main/pdg3dtiles/TreeGenerator.py#L210): is chosen by taking the geometric error of the first child
- [child](https://github.com/PermafrostDiscoveryGateway/viz-3dtiles/blob/main/pdg3dtiles/TreeGenerator.py#L217): contains the root geometric error of the children tiles

When the leaf tiles are created, the asset and root GEs are the max_width calcualted when creating the Cesium3DTile (B3DM) if not specified as an argument.

## Bounding Volume

## Fix Attempts
To make the lake vectors pop up at lower zoom levels, I wanted to try increasing the geometric errors (GE) so that vectors would appear earlier. 

### Approach 1
