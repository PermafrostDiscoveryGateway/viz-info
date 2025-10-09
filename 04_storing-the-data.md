# Storing output tiles

Once the data has been processed, and we have the final output tiles, we need to:
1) Store and archive the `.gpkg` tiles and `.tiff` GeoTIFF files in the Arctic Data Center / DataONE in a directory that specifies the DOI (`datateam:/var/data/{DOI}`). Note that if there are subdirectories, a README should be provided to clarify how the files are organized.
2) Store the `.PNG` web tile images and `.B3DM`/`.JSON` Cesium 3D tilesets in a directory that is accessible from the web and contains the same DOI as the other archived tilsets (`datateam:/var/data/tiles/{DOI}`)
3) Make WMTSCapabilities.xml (Service Metadata) publicly available in the archive directory. 

The exact method that we will use to store and organize all these files is something that we still need to work out. Here is what we are doing for the time being.

## Servers
Data are stored on the NCEAS servers, including:
- **datateam**: `datateam.nceas.ucsb.edu` - Also where we process files
- **ADC demo**: `demo.arcticdata.io` Has web-accessible directories, e.g. it's where we host the MetacatUI files for the `demo.arcticdata.io` website

## Testing the web-accessible files

We move the web tiles and 3D tiles to a directory that is mounted on both the `datateam` server and the `adc-demo` server for testing: `datateam.nceas.ucsb.edu:/var/data/tiles/{DOI}`.

When PNG tilesets are here, you can access them on the web via: `https://arcticdata.io/data/tiles/{DOI}/web_tiles/{STAT}/WGS1984Quad/{TileMatrix}/{TileCol}/{TileRow}.png`. 

If you are displaying a JSON file instead of a tileset, you can create a publy accessible Metacat object and access that file on the web by specifying an object identifier at the end of the URL like `https://arcticdata.io/metacat/d1/mn/v2/object/{ID}`. You can also access a JSON file from another web accessible location besides our archive. We do the latter for the Local Stories layer; the data is pulled from [here](https://www.leonetwork.org/en/explore/posts?query=&type=TWEET&type=POST&type=ARTICLE&mode=geojson_compact&region=&polygon=&bbox=&minlat=&maxlat=&near=&radius=&categories=PERMAFROST%7cPermafrost+Change&categories_anyOrAll=ANY&fromdate=&todate=).

Before adding these tilesets as a new layer to the production portal, we can add them as a layer to the demo portal or view them in [local cesium](https://github.com/PermafrostDiscoveryGateway/viz-info/blob/main/05_displaying-the-tiles.md#option-1-run-cesium-locally) first. 

### Publishing

Once they are production-ready, we make the tilesets in `/var/data/{DOI}` public on the production server. The naming convention is documented [here](https://github.nceas.ucsb.edu/KNB/arctic-data/blob/master/misc/tileset-naming-convention.md).

The publishable GeoTIFF and geopackage tiles are not uploaded like other data objects in DataONE through the user interface. There's too many files for the UI to handle. The tilesets are instead moved to the production server, in the `/var/data/` directory, using the same directory convention as above. It's important that we preserve the directory structure (which reflects the TMS indices). We may also want to consider using STAC to catalog our geospaitial data (see [06: Roadmap](/Users/rtb/git/pdg-info/06_roadmap.md)).

# Common problems

---

**Problem**: Getting the `403 Forbidden Error` when attempting to view a file in a web-accessible location

**Solution**: The permissions on the directory and/or file need to be changed. [Check the permissions of files and folders](https://phoenixnap.com/kb/linux-file-permissions#:~:text=the%20Execute%20box.-,Check%20Permissions%20in%20Command%2DLine%20with%20Ls%20Command,in%20the%20long%20list%20format.) that are web accessible, then [change the permissions of the files or folders](https://www.tomshardware.com/how-to/change-file-directory-permissions-linux) that are giving the 403 error. How to do that [for many files & folders](https://stackoverflow.com/questions/3740152/how-do-i-change-permissions-for-a-folder-and-its-subfolders-files)

---

**Problem**: Moving files takes forever!

**Solution**: There are many solutions for this, and Matt & Juliet are good people to ask! At the very least, using [`rsync`](https://www.atlantic.net/vps-hosting/how-to-use-rsync-copy-sync-files-servers/) is faster than using [`scp`](https://linuxize.com/post/how-to-use-scp-command-to-securely-transfer-files/) within the same server, or for a few thousand files. Use Globus if moving files between servers. Ask Nick to get you setup with the ADC Data Upload endpoint.
