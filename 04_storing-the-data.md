# Storing output tiles

Once the data has been processed, and we have the final output tiles, we need to:
1) Store the `.PNG` web tile images and `.B3DM`/`.JSON` Cesium 3D tile files in a location that is accessible from the web
2) Store and archive the `.GPKG` tiles and `.tiff` GeoTIFF files in the Arctic Data Center / DataONE

The exact method that we will use to store and organize all these files is something that we still need to work out. Here is what we are doing for the time being.

## servers
Data are stored on the NCEAS servers, including:
- **datateam**: `datateam.nceas.ucsb.edu` - Also where we process files
- **ADC demo**: `demo.arcticdata.io` Has web-accessible directories, e.g. it's where we host the MetacatUI files for the `demo.arcticdata.io` website
- **production**: Matt and Jeanette can help you move files here from `datateam`

## Testing the web-accessible files

We move the web tiles and 3D tiles to a directory that is mounted on both the `datateam` server and the `adc-demo` server for testing: `datateam.nceas.ucsb.edu:/var/data/`.

When the files are here, you can access them on the web via: `https://demo.arcticdata.io/tiles/FILENAME`. For example, if you have a directory in `/var/data/` called `my_3dtiles`, and within that directory you have a file named `tileset.json`, you can access that json file on the web at the URL: `https://demo.arcticdata.io/tiles/my_3dtiles/tileset.json`.

### Publishing

Once they are production-ready, we move the web tiles and 3D tiles files to the `/var/data/tiles` directory on the production server, under a sub-directory that reflects the DOI of the package that the data are from. This convention is documented [here](https://github.nceas.ucsb.edu/KNB/arctic-data/blob/master/misc/tileset-naming-convention.md).

The publishable GeoTIFF and geopackage tiles are not uploaded like other data objects in DataONE. They are instead moved to the production server, in the `/var/data/` directory, using the same directory convention as above. This is a temporary measure and we need to determine how to handle archiving these files in the future. We haven't yet finished building the infrastructure for handling datasets will thousands to million of files (but it's under active development), and it's important that we preserve the directory structure (which reflects the TMS indices). We may also want to consider using STAC to catalog our geospaitial data (see [06: Roadmap](/Users/rtb/git/pdg-info/06_roadmap.md)).


# Common problems

---

**Problem**: Getting the `403 Forbidden Error` when attempting to view a file in a web-accessible location

**Solution**: The permissions on the directory and/or file need to be changed. [Check the permissions of files and folders](https://phoenixnap.com/kb/linux-file-permissions#:~:text=the%20Execute%20box.-,Check%20Permissions%20in%20Command%2DLine%20with%20Ls%20Command,in%20the%20long%20list%20format.) that are web accessible, then [change the permissions of the files or folders](https://www.tomshardware.com/how-to/change-file-directory-permissions-linux) that are giving the 403 error. How to do that [for many files & folders](https://stackoverflow.com/questions/3740152/how-do-i-change-permissions-for-a-folder-and-its-subfolders-files)

---

**Problem**: Moving files takes forever!

**Solution**: There are many solutions for this, and Matt & Kastan are good people to ask! At the very least, using [`rsync`](https://www.atlantic.net/vps-hosting/how-to-use-rsync-copy-sync-files-servers/) is faster than using [`scp`](https://linuxize.com/post/how-to-use-scp-command-to-securely-transfer-files/). 
