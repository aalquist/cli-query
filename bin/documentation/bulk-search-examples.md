### Bulk Search - Putting it together
Here are a few examples how you can use built-in options or your own customized filters & searches.

### First Example:
Many times its useful to get the list CPCODEs for a set of properties. This is the most common use case, so its the default search. The default filter output shows all of the results for each property on a single line. The default output is one JSON Array per line. If needed, this output can easily be converted into a CSV file [JQ and @CSV formatting](https://stedolan.github.io/jq/manual/#Formatstringsandescaping). 

#### Default Search and Filter:
```
akamai query bulksearch --network Production 

```
Output:

```
["propertyName", "results"]
["configuration_1", 10000]
["configuration_2", 20000]
["configuration_3", "30000,30001,30002,30003"]
["configuration_4", 40000]

```

Using JQ @CSV:

```
akamai query bulksearch --network Production | jq ' . | @csv'

```
CSV Output:

```
"\"propertyName\",\"results\""
"\"configuration_1\",\"10000\""
"\"configuration_2\",\"20000\""
"\"configuration_3\",\"30000,30001,30002,30003\""
"\"configuration_4\",\"40000\""

```

#### Default Search w/ Built-in Results Only filter:
For simple output that returns a flattened list of one value per line, modify the above command to use the result.json filter.


```
akamai query bulksearch --network Production --filtername result.json

```

Outputs Flattened List:

```
10000
20000
30000
30001
30002
30003
40000

```

#### Default Search - JSON Only:
In some cases you might want to write your own filter or rather use JQ querying syntax; you can output JSON instead.

```
akamai query bulksearch --network Production --show-json

```

Outputs:

```
[
 {
  "propertyId": "prp_00001",
  "propertyVersion": 100,
  "propertyName": "configuration_1",
  "productionStatus": "ACTIVE",
  "stagingStatus": "ACTIVE",
  "isLatest": true,
  "isLocked": true,
  "matchLocations": [
   "/rules/behaviors/1/options/value/id"
  ],
  "lastModifiedTime": "2019-01-01T00:00:00Z",
  "isSecure": false,
  "matchLocationResults": [
   10000
  ]
 }

 //...

```


#### Default Search - Write your own filter:
To build your own filter, check out the syntax of the built-in filters, copy one, and build your own. Each filter is a map of JSONPath statements where the key is the result's column name and the value of the colum is the result of the JSONPath. Each JSONPath is executed independently and repeatedly on each result row/item. 

In the example below, I copied the default.json built-in filter and added 3 more columns of my own:  PropertyVersion, ProductionStatus, StagingStatus. Now-- I run the same command as before, but have the configuration's version and the activation status for both networks.

Create My Custom Filter:

```
{
 "PropertyName": "$.propertyName",
 "PropertyVersion": "$.propertyVersion",
 "ProductionStatus": "$.productionStatus",
 "StagingStatus": "$.stagingStatus",
 "results": "$.matchLocationResults[*]"
}
```

Option 1: Pipe In My Custom Filter using STDIN:

```
echo '{
 "PropertyName": "$.propertyName",
 "PropertyVersion": "$.propertyVersion",
 "ProductionStatus": "$.productionStatus",
 "StagingStatus": "$.stagingStatus",
 "results": "$.matchLocationResults[*]"
}' | akamai query bulksearch --network Production --use-filterstdin

```

Option 2: Save My Custom Filter to a file and read from file:

```
echo '{
 "PropertyName": "$.propertyName",
 "PropertyVersion": "$.propertyVersion",
 "ProductionStatus": "$.productionStatus",
 "StagingStatus": "$.stagingStatus",
 "results": "$.matchLocationResults[*]"
}' > myfilter.json

akamai query bulksearch --network Production --filterfile myfilter.json

```

Both Output:

```
["PropertyName", "PropertyVersion", "ProductionStatus", "StagingStatus", "results"]
["configuration_1", 11, "ACTIVE", "ACTIVE", 10000]
["configuration_2", 22, "ACTIVE", "INACTIVE", 20000]
["configuration_3", 33, "ACTIVE", "INACTIVE", "30000,30001,30002,30003"]
["configuration_4", 44, "ACTIVE", "INACTIVE", 40000]

```
