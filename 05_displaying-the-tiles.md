# Displaying the tiles

The end goal of creating tiles is to display them in an interactive web map, where users can zoom in to see the highest resolution data, and zoom out to see an overview of the data. We are using a javascript library called **cesium** to create the map that renders the web-tiles and 3D tiles. We include a custom cesium map as an optional page in our **data portals**. Data portals are a feature of the software we build and maintain, called **MetacatUI**.

## MetacatUI
- MetacatUI is web software we build that includes features like a searchable data catalog, data submission form, and data portals
	- [MetacatUI documentation](https://nceas.github.io/metacatui/)
	- [MetacatUI on GitHub](https://github.com/NCEAS/metacatui)
- The [KNB](https://knb.ecoinformatics.org/), [ADC](https://arcticdata.io/catalog), [DataONE site](), all use the MetacatUI software. "Test" versions of these MetacatUI deployments also exist: [dev.nceas](https://dev.nceas.ucsb.edu/), [demo ADC](https://demo.arcticdata.io/), [test ADC](https://test.arcticdata.io/), [test DataONE](https://search.test.dataone.org), among others.
- We are continually adding features and fixing bugs, see [the list of issues](https://github.com/NCEAS/metacatui/issues)

## Portals
- Data portals are one of the features of MetacatUI.
- A portal is essentially a small website that users can build for their project. It includes a custom collection of data and ways to display information about that data as well as their project.
	- Learn more about portals [on the DataONE site](https://www.dataone.org/plus/) and [on the ADC site](https://arcticdata.io/data-portals/)
- Here are some example portals:
	- https://knb.ecoinformatics.org/portals/SASAP
	- https://arcticdata.io/catalog/projects/DBO
	- https://search.dataone.org/portals/mosaic
	- https://permafrost.arcticdata.io/ (the PDG portal)
- The tiled data that is created in the pipeline can be displayed in an optional "map" page in portals. So far, the map feature is only being used for a few projects, such as the PDG and the Defense Resiliency Platform Against Extreme Cold Weather.

### Creating & editing portals
- Portals can be created & edited in [the portal builder](https://demo.arcticdata.io/edit/portals) in MetacatUI.
- Under the hood, the portal builder is just editing a portal document, which is some XML that configures each portal.
- The XML that creates a portal is defined by the [portal & collections schema](https://github.com/DataONEorg/collections-portals-schemas). (Not all [version 1.1.0](https://github.com/DataONEorg/collections-portals-schemas/releases/tag/1.1.0) schema features are supported in MetacatUI yet. [Here](https://github.com/NCEAS/metacatui/issues?q=is%3Aopen+is%3Aissue+label%3A%22portals+1.1.0+support%22) is what we have left to do.)
- Changes to portals can also be made by downloading the portal XML, editing it, then uploading the new version via the DataONE API.
	- [Here](https://nceas.github.io/datateam-training/reference/customizing-data-portals.html#updating-portals) are instructions on how to do that in R. (Also feel free to ask Robyn for further help/explanation!)
		-  The `formatId` for portal xml documents is `https://purl.dataone.org/portals-1.1.0` defined [in DataONEorg/object-format](https://github.com/DataONEorg/object-formats/blob/fbef1ec3d3c6d14ac4331414627ad252b6cf314d/objectFormatListV2.xml#L987-L993) 
		- You can also search for a portal using the portal **label** (the part in the URL that is after `/portals/`), for example:

```R
df <- query(ucsb, list(q ="label:permafrost AND (*:* NOT obsoletedBy:*)",
                       fl = "identifier,formatId,seriesId"),
            as = "data.frame")
```
(The above `query` function is doing a [solr](https://solr.apache.org/) query, you can read more about that [here](https://nceas.github.io/datateam-training/reference/solr-queries.html))

### PDG portal
When we have tiles/layers to test or publish, we add them to either the demo or production version of the Permafrost Discovery Gateway portal.
- **production version of the PDG portal**: [permafrost.arcticdata.io](https://permafrost.arcticdata.io/)
	- This is the public version of the portal, where we publish tiles/layers that are ready to share with the world
	- solr query for the current public version of the PDG portal doc: https://arcticdata.io/metacat/d1/mn/v2/query/solr/?q=label:permafrost%20AND%20(*:*%20AND%20NOT%20obsoletedBy:*)&fl=label,dateUploaded,id,seriesId,formatId
	- The **XML document** that configures this portal: https://arcticdata.io/metacat/d1/mn/v2/object/urn%3Auuid%3A0973cea6-fedc-4a0b-a8a1-4eed8c9f4d3b

- **demo version of the PDG portal**: [demo.arcticdata.io/portals/permafrost](https://demo.arcticdata.io/portals/permafrost)
	- This is where we test tiles that we are working on
	- [**solr query**](https://dev.nceas.ucsb.edu/knb/d1/mn/v2/query/solr/?q=label:permafrost%20AND%20(*:*%20AND%20NOT%20obsoletedBy:*)&fl=label,dateUploaded,id,seriesId,formatId) for the current demo version of the PDG portal doc
	- [**XML document**](https://dev.nceas.ucsb.edu/knb/d1/mn/v2/object/urn%3Auuid%3Ab831ed0d-ec73-4b36-b9b0-845a87f8155a) that configures this portal

### Configuring map layers in a portal document

Using the PDG XML document as an example, notice that the map page is configured with a `<section>` element. We've named the section `Imagery Viewer` (this could be anything), we've told MetacatUI that the section should be a visualization type page, specifically a cesium map. The cesium map is then configured with JSON, which is wrapped in CDATA tags, and stored as the `optionValue` for the `mapConfig`.

```xml
...
<section>
	<label>Imagery Viewer</label>
	<title>Imagery Viewer</title>
	<option>
		<optionName>sectionType</optionName>
		<optionValue>visualization</optionValue>
	</option>
	<option>
		<optionName>visualizationType</optionName>
		<optionValue>cesium</optionValue>
	</option>
	<option>
		<optionName>mapConfig</optionName>
		<optionValue><![CDATA[ { ... JSON HERE ... } ]]></optionValue>
	</option>
</section>
...
```

All options for the `mapConfig` are outlined [in the MetacatUI docs](https://nceas.github.io/metacatui/docs/MapConfig). Explanations on how the map & configuration works, and examples of more configurations are detailed in [this Guide](https://nceas.github.io/metacatui/guides/maps/cesium.html).

The map tiles (PNG web tiles or B3DM/JSON 3D tiles) need to be uploaded to a web-accessible location to display them in a portal (more about that in `storing-the-data`). The `url` option in each layer's config is where you point to this web accessible location.

The `ConfigManager` class in the `pdgstaging` library includes a [`get_metacatui_configs`](https://github.com/PermafrostDiscoveryGateway/viz-staging/blob/5a8464fe92b22cbe0a793586febba89001c5188c/pdgstaging/ConfigManager.py#L851) method that will help you create config JSON to add to the layers list in the mapConfig. *Note: this method is not well tested, and may need to be adapted to different circumstances.*

## Cesium
- Cesium JS is the software that we use to make the map page in portals. We build our own UI (layers list, buttons, etc.) around the Cesium map. For more about Cesium, see the list of [useful links in the MetacatUI map guide](https://nceas.github.io/metacatui/guides/maps/cesium.html#useful-links)
- [Cesium Ion](https://cesium.com/platform/cesium-ion/) is a paid service from the same people who build the open source Cesium JS library. It can convert some file types to Cesium 3D tiles, but not shapefiles! [FME](https://www.safe.com/convert/arcgis-shp/cesium-3d-tiles/) is the only software out there, other than our `py3dtiles` library, that converts shapefiles to 3D tiles (and it's quite expensive!)

# Other ways to test your data

Other than updating a portal document and displaying data on the web, you can also test tiles you've created by either 1) running Cesium locally, or 2) testing with Cesium sandcastle.

## Option 1: Run Cesium Locally
- The `viz-3dtiles` repo has the files & instructions you need for an [easy setup](https://github.com/PermafrostDiscoveryGateway/viz-3dtiles/tree/main/test/run-cesium)

### Steps:

1. On your local machine, clone the `viz-3dtiles` repo.

2. Using Homebrew in the terminal, install `express.js` by running running `brew install node` then `npm install express`

3. In the terminal, navigate to the directory `viz-3dtiles/test/run-cesium` and run `node server.js`. This should return a print statement in your terminal like `Now running at http://localhost:3003`. Navigate to that URL in your browser.

4. On the [Cesium site](https://cesium.com/ion/signin), create an account to obtain a personal token.

5. Replace the entire contents of the `/viz-3dtiles/test/run-cesium/cesium.js` file with:

```
Cesium.Ion.defaultAccessToken = "YOUR TOKEN HERE"; // <- update this

const viewer = new Cesium.Viewer('cesiumContainer');

const imageryLayers = viewer.imageryLayers;

const myNewProvider = new Cesium.WebMapTileServiceImageryProvider({
  "url": "https://demo.arcticdata.io/cesium-layers/raster-imagery/bartsch_infrastructure/WorldCRS84Quad/{TileMatrix}/{TileCol}/{TileRow}.png",
  "tilingScheme": new Cesium.GeographicTilingScheme()
})
const myNewLayer = new Cesium.ImageryLayer(myNewProvider)
imageryLayers.add(myNewLayer)
```

and be sure to insert your token.

6. Refresh your browser to reflect these changes to `cesium.js`

7. To show the layer you created, transfer all the new PNG web tiles from the server to your local directory `viz-3dtiles/test/run-cesium/web-tiles`. For example, in your local machine's terminal, run `scp username@datateam:/home/username/viz-workflow/web_tiles ~/Documents/viz-3dtiles/test/run-cesium/web-tiles`

8. Within `cesium.js`, change

```
"url": "https://demo.arcticdata.io/cesium-layers/raster-imagery/bartsch_infrastructure/WorldCRS84Quad/{TileMatrix}/{TileCol}/{TileRow}.png",
```

to the path to your local web tiles, such as:

```
"url": "web-tiles/iwp_coverage/WGS1984Quad/{TileMatrix}/{TileCol}/{TileRow}.png",
```

The above file path needs to be adjusted to reflect the web tiles you want to visualize.

9. Refresh your browser and admire the data! 

10. To kill the local host, close the terminal window or use `ctrl` + `c`

### Small Datasets

If you are working with a small dataset or a subset of a large dataset for testing and you are having trouble finding the tiles you visualized because there just isn't very many of them, you can use the morecantile library and add a few more lines of code to `cesium.js` to fix your problem:

- In Python, run the following code to generate the bounding box coordinates for one of the web tiles (it can be any one!):

```
import morecantile

tms = morecantile.tms.get("WGS1984Quad")
tms.bounds(morecantile.Tile(x = {value}, y = {value}, z = {value}))
```

- The output will look something like this:

`BoundingBox(left=-177.47314453125, bottom=71.20788574218751, right=-177.4676513671875, top=71.21337890625001)`

- Modify `cesium.js` by adding 2 lines of code that define the `"rectangle"` and apply the `zoomTo()` function:

```
Cesium.Ion.defaultAccessToken = "YOUR TOKEN HERE"; // <- update this

const viewer = new Cesium.Viewer('cesiumContainer');

const imageryLayers = viewer.imageryLayers;

const myNewProvider = new Cesium.WebMapTileServiceImageryProvider({
  "url": "https://demo.arcticdata.io/cesium-layers/raster-imagery/bartsch_infrastructure/WorldCRS84Quad/{TileMatrix}/{TileCol}/{TileRow}.png",
  "tilingScheme": new Cesium.GeographicTilingScheme(),
  "rectangle": Cesium.Rectangle.fromDegrees(-177.47314453125, 71.20788574218751, -177.4676513671875, 71.21337890625001)
})
const myNewLayer = new Cesium.ImageryLayer(myNewProvider)
imageryLayers.add(myNewLayer)
viewer.zoomTo(myNewLayer);
```

Save the file and refresh the browser. The window should automatically zoom to the tile you specified! However, it is also _only visualizing that one tile_, so take note of where it zoomed to, then remove those `"rectangle"` and apply the `zoomTo()` lines from `cesium.js`, then refresh and manually zoom to that point to see all the tiles. Done!



## Option 2: Test in cesium sandcastle

- Cesium sandcastle is a free online sandbox for testing things in Cesium.
	- [Here](https://sandcastle.cesium.com/#c=bVPvb5swEP1XTuwLnYLN0k6qaFpN6pC6KWq6hLaaxBeDL4lXYyPbpD+m/u8zEFqiDoTw+e5x770zpVbWwU7gIxo4B4WPcIlWNBW56/bCPCi7+FIrx4RCkwdHZ7nKVdkhnZBo0R1C+9fx96xPhn9zBUAp3C7nCdxfpcsU7lNYZQu/WNwuIVvcRPP0Lp1D9mOertIMfq4W1y2oMTKBPNg6V9uEUo6VJsyUTpScOUaEpj27SLJnNJYe82jPyFIl3AtG03g69dkHjMotUxuk99pIfrlcnZ78ahincXuTP1arPJjk6rUX58leL7I0gd+6gUchpZeHHJyGF60rEArWjXFb79laG/CL3oi2wDpmHBhUHI1Qm1ztCRGDjD/fGF0Ji6024mEqXDfKy9EKwn3dEXR2wX4oxJaokNRGVMKJHVrCOH+rPTsobbllOuz3YJjNZIhHE7ryXDy5G+HK7bK15Q0EEJN48h5FMfk6CgcxhW5U+4VV7U1AYvznGgufYUriofioX/QcX7uIlMw3HGlGY7R5U9weKS2RSL3ZZ/bYs2AS5EEXDA/AzLpniRdDu2+iqrV33h+ZkBDqsKolc2hp0ZQPnnFp7WAXwCentSyYGTq3V8HKh41pdSVgNgULT6YTGJ6YnL6jAWo/BK8+gZP6abRdaOOnHvVuHCZfP7QWqm7cmMAOjT/YTEZMio1KoBKcS/zYNXK6TmB60HlIFdo5XR1m961ndGzYjIsdCH7+n/8bSsms9Zl1I+VKvGAeXMyor/8Albo7RgvP3P+Abdn2y8W83ySEzKgPx8h/)'s an editable example that renders some 3D tiles we made