## Default

```
(model:monograph
OR model:periodical
OR (model:collection AND collection.is_standalone:true)
OR model:graphic
OR model:map
OR model:sheetmusic
OR model:soundrecording
OR model:archive
OR model:manuscript
OR model:convolute
OR model:monographunit)
```

## Public `access=open`

```
(model:monograph
OR model:periodical
OR (model:collection AND collection.is_standalone:true)
OR model:graphic
OR model:map
OR model:sheetmusic
OR model:soundrecording
OR model:archive
OR model:manuscript
OR model:convolute
OR model:monographunit)

AND
## probably public tag ↓
(licenses:mzk_public-muo
OR contains_licenses:mzk_public-muo
OR licenses_of_ancestors:mzk_public-muo
OR licenses:mzk_public-contract
OR contains_licenses:mzk_public-contract
OR licenses_of_ancestors:mzk_public-contract
OR licenses:public OR contains_licenses:public
OR licenses_of_ancestors:public)
```

## Login `access=login`

```
(model:monograph
OR model:periodical
OR (model:collection AND collection.is_standalone:true)
OR model:graphic OR model:map OR model:sheetmusic
OR model:soundrecording
OR model:archive
OR model:manuscript
OR model:convolute
OR model:monographunit)

AND
## login tag
(licenses:dnnto
OR contains_licenses:dnnto
OR licenses_of_ancestors:dnnto)
```

## In library `access=terminal`

```
(model:monograph
OR model:periodical
OR (model:collection AND collection.is_standalone:true)
OR model:graphic
OR model:map
OR model:sheetmusic
OR model:soundrecording
OR model:archive
OR model:manuscript
OR model:convolute
OR model:monographunit) 


AND 

## terminal tag
((licenses:dnntt OR contains_licenses:dnntt OR licenses_of_ancestors:dnntt OR licenses:onsite OR contains_licenses:onsite OR licenses_of_ancestors:onsite OR licenses:onsite-sheetmusic OR contains_licenses:onsite-sheetmusic OR licenses_of_ancestors:onsite-sheetmusic)
AND
NOT (licenses:dnnto OR contains_licenses:dnnto OR licenses_of_ancestors:dnnto))
```

## Public `licences=public`

```
(model:monograph OR model:periodical OR (model:collection AND collection.is_standalone:true) OR model:graphic OR model:map OR model:sheetmusic OR model:soundrecording OR model:archive OR model:manuscript OR model:convolute OR model:monographunit)

AND
# public tag
(licenses:public OR contains_licenses:public OR licenses_of_ancestors:public)
```

## Hudebniny Kroměříž `licences=mzk_public-muo`

```
(model:monograph OR model:periodical OR (model:collection AND collection.is_standalone:true) OR model:graphic OR model:map OR model:sheetmusic OR model:soundrecording OR model:archive OR model:manuscript OR model:convolute OR model:monographunit)

AND
# kromeriz tag
(licenses:mzk_public-muo OR contains_licenses:mzk_public-muo OR licenses_of_ancestors:mzk_public-muo)
```

## Díla nedostupná na trhu - online `licences=dnnto`

```
(model:monograph OR model:periodical OR (model:collection AND collection.is_standalone:true) OR model:graphic OR model:map OR model:sheetmusic OR model:soundrecording OR model:archive OR model:manuscript OR model:convolute OR model:monographunit)

AND
# dnnto tag
(licenses:dnnto OR contains_licenses:dnnto OR licenses_of_ancestors:dnnto)
```

## Smluvně zveřejněná díla `licences=mzk_public-contract`

```
(model:monograph OR model:periodical OR (model:collection AND collection.is_standalone:true) OR model:graphic OR model:map OR model:sheetmusic OR model:soundrecording OR model:archive OR model:manuscript OR model:convolute OR model:monographunit)

AND
# licence tag
(licenses:mzk_public-contract OR contains_licenses:mzk_public-contract OR licenses_of_ancestors:mzk_public-contract)
```

## Studovna - hudebniny `lincences=onsite-sheetmusic`

```
(model:monograph OR model:periodical OR (model:collection AND collection.is_standalone:true) OR model:graphic OR model:map OR model:sheetmusic OR model:soundrecording OR model:archive OR model:manuscript OR model:convolute OR model:monographunit)

AND
# studovan tag
(licenses:onsite-sheetmusic OR contains_licenses:onsite-sheetmusic OR licenses_of_ancestors:onsite-sheetmusic)
```

## Díla nedostupná na trhu - studovna `licences=dnntt`

```
(model:monograph OR model:periodical OR (model:collection AND collection.is_standalone:true) OR model:graphic OR model:map OR model:sheetmusic OR model:soundrecording OR model:archive OR model:manuscript OR model:convolute OR model:monographunit)


AND
# dnntt tag
(licenses:dnntt OR contains_licenses:dnntt OR licenses_of_ancestors:dnntt)
```

## Studovna `licences=onsite`

```
(model:monograph OR model:periodical OR (model:collection AND collection.is_standalone:true) OR model:graphic OR model:map OR model:sheetmusic OR model:soundrecording OR model:archive OR model:manuscript OR model:convolute OR model:monographunit)

AND 
# onsite tag
(licenses:onsite OR contains_licenses:onsite OR licenses_of_ancestors:onsite)
```

## Knihy `doctypes=monograph`

```
(model:monograph
OR model:periodical
OR (model:collection AND collection.is_standalone:true)
OR model:graphic
OR model:map
OR model:sheetmusic
OR model:soundrecording
OR model:archive
OR model:manuscript
OR model:convolute
OR model:monographunit)

AND (model:monograph OR model:monographunit)
```

Rest:

| query          | sorl request                           |
|----------------|----------------------------------------|
| archive        | archive                                |
| collection     | colection                              |
| convolute      | convolute                              |
| graphic        | graphic                                |
| manuscript     | manuscript                             |
| map            | map                                    |
| monograph      | model:monograph OR model:monographunit |
| periodical     | periodical                             |
| sheetmusic     | sheetmusic                             |
| soundrecording | soundrecording                         |

## Date `from, to`

```
(model:monograph OR model:periodical OR (model:collection AND collection.is_standalone:true) OR model:graphic OR model:map OR model:sheetmusic OR model:soundrecording OR model:archive OR model:manuscript OR model:convolute OR model:monographunit)

AND
# date tag
((date_range_start.year:[* TO 2013] AND date_range_end.year:[150 TO *]))
```

## Other

| name       | command                    |
|------------|----------------------------|
| places     | publication_places.search: |
| publishers | publishers.search:         |
| locations  | physical_locations.facet:  |
| languages  | languages.facet:           |
| keywords   | keywords.search:           |
| authors    | authors.search:            |
| geonames   | geographic_names.search:   |
| genres     | genres.search:             |

```
(model:monograph OR model:periodical OR (model:collection AND collection.is_standalone:true) OR model:graphic OR model:map OR model:sheetmusic OR model:soundrecording OR model:archive OR model:manuscript OR model:convolute OR model:monographunit)

AND

(geographic_names.search:"Československo") AND (publishers.search:"Ústredná správa geodézie a kartografie") AND (genres.search:"Školní mapy")
```
