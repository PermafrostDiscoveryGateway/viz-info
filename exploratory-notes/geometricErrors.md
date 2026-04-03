# Geometric Errors & Bounding Volume Notes (Lake Change Layer)

## Original Issue
We staged the Lake Change layer at z = 13, and we needed to create a pyramid of 3dtiles so that the files would load on the portal.

## Pyramid Layout
After using the viz-workflow functions for creating parent tiles, we weren't able to see the lake vectors until we were zoomed in all the way to z = 13 on the Cesium map. 

## Geometric Errors
There are 3 types of geometric errors in a json tile file: 
- [asset](https://github.com/PermafrostDiscoveryGateway/viz-3dtiles/blob/main/pdg3dtiles/TreeGenerator.py#L233): is chosen by taking the max of the children's geometric errors
    - This is metadata
- [root](https://github.com/PermafrostDiscoveryGateway/viz-3dtiles/blob/main/pdg3dtiles/TreeGenerator.py#L210): is chosen by taking the geometric error of the first child
    - This determines 
- [child](https://github.com/PermafrostDiscoveryGateway/viz-3dtiles/blob/main/pdg3dtiles/TreeGenerator.py#L217): contains the root geometric error of the children tiles
    - This determines

When the leaf tiles are created, the asset and root GEs are the max_width calcualted when creating the Cesium3DTile (B3DM) if not specified as an argument.

## Bounding Volume
There are 2 different bounding volumes to consider:
- root: if not specified, this is [chosen](https://github.com/PermafrostDiscoveryGateway/viz-workflow/blob/main/pdgworkflow/StagedTo3DConverter.py#L70) by taking the bounding [volume of the entire tile](https://github.com/PermafrostDiscoveryGateway/viz-workflow/blob/main/pdgworkflow/StagedTo3DConverter.py#L181). 
- content: it doesn't seem like we're recording content bounding volume, so it defaults to the root bounding volume.

## Current State of JSON Pyramids GEs
**Utqiagvik**
| z    | x/y      | asset ge | root ge |
|------|----------|----------|---------|
| 13   | 1064/859 | 1271     | 1271    |
| 12   | 532/429  | 1271     | 1271    |
| 11   | 266/214  | 13030    | 13030   |
| 10   | 133/107  | 90728    | 13030   |
| 9    | 66/53    | 90728    | 817     |
| 8    | 33/26    | 90728    | 817     |
| 7    | 16/13    | 90728    | 347     |
| 6    | 8/6      | 90728    | 347     |
| 5    | 4/3      | 451727   | 347     |
| 4    | 2/1      | 451727   | 347     |
| 3    | 1/0      | 451727   | 347     |
| 2    | 0/0      | 1402067  | 1397    |
| 1    | 0/0      | 3301201  | 1397    |
| 0    | 0/0      | 3301201  | 1397    |
| root | NA       | 3301201  | 990     |
 
| **Western Alaska**
| z    | x/y      | asset ge | root ge |
|------|----------|----------|---------|
| 13   | 541/1107 | 622      | 622     |
| 12   | 270/553  | 622      | 622     |
| 11   | 135/276  | 6839     | 622     |
| 10   | 67/138   | 10253    | 622     |
| 9    | 33/69    | 10253    | 622     |
| 8    | 16/34    | 10253    | 622     |
| 7    | 8/17     | 10253    | 622     |
| 6    | 4/8      | 30010    | 622     |
| 5    | 2/4      | 131342   | 622     |
| 4    | 1/2      | 390011   | 622     |
| 3    | 0/1      | 390011   | 2401    |
| 2    | 0/0      | 1402067  | 1397    |
| 1    | 0/0      | 3301201  | 1397    |
| 0    | 0/0      | 3301201  | 1397    |
| root | NA       | 3301201  | 990     |


## Fix Attempts
To make the lake vectors pop up at lower zoom levels, I wanted to try increasing the geometric errors (GE) so that vectors would appear earlier. 

### Approach 1
