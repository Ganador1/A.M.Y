# Climate regression dataset

`climate_nasa_gistemp.csv` is the historical NASA GISS GISTEMP Land-Ocean global-means table already present in AMY's main branch. It is retained unchanged as an input for `tests/unit/test_climate_loop.py` and the climate data loader. Credit: NASA Goddard Institute for Space Studies (GISS), GISTEMP team.

This is a fixed regression fixture, not a current data download or an AMY discovery. Its original retrieval date was not recorded in this distribution. Missing observations use the source table's `***` marker. The public source manifest records the exact file hash.
