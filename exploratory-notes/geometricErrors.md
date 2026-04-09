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
### **Utqiagvik**
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
 
### **Western Alaska**
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
What I understood was that making a geometric error too large would overload the portal if we were zoomed out and it tried loading all 2 million files. I used a ramp of geometric errors and updated the jsons with this mapping of zoom levels to GEs:

```
ge_ramp = {
    8: 32000.0,
    9: 24000.0,
    10: 18000.0,
    11: 15000.0,
    12: 12000.0,
    13: 9000.0
}
```

I kept the tiles from z = 0 to z = 7 the same. I then changed the geometric errors from z = 8 to z = 12 to be larger, but cascading down. I chose 8 as the "Transition Zoom", which is the height where I want the lakes to start appearing. 

I left the z = 13 tiles as they were as well at first with GE=1397. I was hoping they would appear once we hit z = 8, but it still wasn't showing up until I zoom all the way in.

That's when I decided to try changing the z = 13 tiles to have a GE of 9000 as well. Google Gemini had given this explanation as to why increasing the z = 13 GEs would work: 

> Why this should work better 
> 1. The Parent-Child Chain: In your previous attempt, the parents (z=7−12) were likely opening up correctly, but when the engine looked at the children (z=13), it saw GE=1397 and said, "That's too much detail for this distance, I'll wait until the user gets closer."\
> 2. The Force-Render: By setting the leaf GE to 8000, you are telling the engine: "Even if I am 50km in the air, this tile still has '8000 units' of error, so you MUST draw the vector to reduce that error."

I think the first attempt might have worked if there were b3dm files at each zoom level. 

It might not be traveling all the way down to the pyramid at the intermediate z-levels.

### Approach 2
With the help of a debugging mode
```
{
  "debug": true,
  "show3DTilesInspector": true
}
```
I got the lake vectors to begin popping up a bit earlier in zoom levels. I had to increase the GEs from the root json to z = 5 by a lot. Then, I decreased them from 6 to 13. From Gemini, it pointed out that the Bounding Volume could be an important factor in calculating the ideal GE since a tighter or larger colume compared to the tile could affect the distance, which would affect the SSE.

These were the GEs I used at each zoom level
```
ges = {0: 1000000,
       1: 1000000,
       2: 1000000,
       3: 1000000,
       4: 1000000,
       5: 1000000,
       6: 10000,
       7: 5000,
       8: 2500,
       9: 1200,
       10: 800,
       11: 600,
       12: 400,
       13: 0}
```

Previously, I thought that we just needed a larger GE at the sepcific z-level we wanted them to pop out on. But Gemini said that having the z = 0 to z = 5 be much larger forces them to skip through those levels. 

I noticed that the jsons weren't being loaded in the network tab at other points in the map, even at z = 8. So, it seemed like the cammera was stuck at z = 0 when the geometric error wasn't big enough. 