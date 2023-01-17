# Update py3dtiles package with Oslandia updates

Overview instructions documented in the [repo README.](https://github.com/PermafrostDiscoveryGateway/py3dtiles/blob/main/README.rst). Update this repo from your local machine rather than a server.

Oslandia git lab repo is [here.](https://gitlab.com/Oslandia/py3dtiles) 

## Steps:
- Pull updates for `viz-staging`, `viz-raster`, `viz-3dtiles`, and `py3dtiles`
- `cd` into `py3dtiles`, switch into branch `gitlab-oslandia`
    - this branch is essentially a mirror of the oslandia gitlab repo
- run `git remote -v` to see all remote branches. If this is your first time, you'll need to add the http link for the oslandia gitlab repo using `git remote add` and name the remote `gitlab`
- run `git pull gitlab master` (the master part was necessary the first time, may or may not be necessary next times)
- run `git push origin`
- run `git checkout develop`
- run `git merge gitlab-oslandia`
    - This is where conflicts will arise if there are any. Conflicts will occur if 1) any changes _we_ have made to our fork conflict with any of the code they changed, regardless if the changes we made were since the last pull or not, because any code we ever modified was not merged into their repo, so if they modified their version of that code, it's new to our repo.
    - After resolving conflicts, don't forget to save modified files.
- run `git commit` no message necessary
- Time to test the changes. The point of this is to see if any of the changes made result in errors in our workflow, or changes something that can only be identified after visualizing the files. Switch into `viz-3dtiles` repo, main branch is fine.
- activate python environment that has _local_ versions of all these packages installed
- run `python test/test.py`
    - ignore a warning from `geopandas` if one comes up
    - an error message might be printed in the terminal, if so trace error to file in the traceback. Can also ctrl+shift+f in the file explorer for a keyword like the module that is at the root of the error, like 'class moduleName` to find the file you're looking for.
- switch into `test/run-cesium`, open `cesium.js` and enter token for the cesium baselayer, and run `node cesium.js`
    - take a look at the url printed in the terminal and see if any of the web tiles look like they are obviously in the wrong places, such as over water
- `cd` into `py3dtiles` again, develop branch, commit & push changes 
- switch to main branch, `git merge develop`, push changes

Done!

**Notes:**
- can subscribe to changes from oslandia
- do this about every 2 weeks to avoid getting too far behind
- if you're not sure if you should accept a merged change, can accept the merge and run the test, and if it goes poorly, can just unmerge changes and make opposite decision and run the test again