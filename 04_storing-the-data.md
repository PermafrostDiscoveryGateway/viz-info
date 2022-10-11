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

- We move the web tiles and 3D tiles to a directory that is mounted on both the `datateam` server and the `adc-demo` server for testing.
TODO

### Publishing
We move these files to the `/var/data/tiles` directory on the production server, under a sub-directory that reflects the DOI of the package that the data are from. This convention is documented [here](https://github.nceas.ucsb.edu/KNB/arctic-data/blob/master/misc/tileset-naming-convention.md).



TODO:
- Common problems:
  - permissions on files
  - moving data takes a long time (rsync)
