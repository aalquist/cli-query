[![Build Status](https://travis-ci.com/aalquist/cli-query.svg?branch=master)](https://travis-ci.com/aalquist/cli-query)

# cli-query
CLI-Query is a command line interface indended to simplify the interaction of multiple API endpoints available on [developer.akamai.com](https://developer.akamai.com/). 

## sample install

First install [Akamai CLI](https://developer.akamai.com/cli/docs/getting-started), then run:

```
akamai install https://github.com/aalquist/cli-query

```

## Table of Contents:

 * [Bulk Search](#querying-property-mangager-configurations)
 * [NetStorage Users](#querying-netstorage-users)
 * [NetStorage Groups](#querying-netstorage-ns4)
 * [Log Delivery Service](#querying-log-delivery-service-lds)


## Commandline Help Text

``` 
usage: akamai query help [command] [--version]
                                   {help,filtertemplate,bulksearchtemplate,ldslist,netstoragelist,netstorageuser,groupcpcodelist,bulksearch}
                                   ...

Akamai Query CLI

positional arguments:
  {help,filtertemplate,bulksearchtemplate,ldslist,netstoragelist,netstorageuser,groupcpcodelist,bulksearch}
                        commands
    help                Show available help
    filtertemplate      prints a filter template
    bulksearchtemplate  prints a bulksearch template
    ldslist             List all cpcode based log delivery configurations
    netstoragelist      List storage groups
    netstorageuser      List netstorage users
    groupcpcodelist     CPCODES assigned to groups
    bulksearch          bulk search property manager configurations

optional arguments:
  --version             show program's version number and exit

``` 
## Querying Log Delivery Service (LDS)

``` 
usage: akamai query [command] ldslist [--show-json] [--use-filterstdin]
                                      [--file FILE] [--template TEMPLATE]
                                      [--edgerc EDGERC] [--section SECTION]
                                      [--debug] [--account-key ACCOUNT_KEY]

optional arguments:
  --show-json           output json
  --use-filterstdin     use stdin for query
  --file FILE           the json file for query
  --template TEMPLATE   use template name for query
  --edgerc EDGERC       Location of the credentials file [$AKAMAI_EDGERC]
  --section SECTION     Section of the credentials file
                        [$AKAMAI_EDGERC_SECTION]
  --debug               DEBUG mode to generate additional logs for
                        troubleshooting
  --account-key ACCOUNT_KEY
                        Account Switch Key

``` 
## Querying Netstorage NS4

``` 
usage: akamai query [command] netstoragelist [--show-json] [--use-filterstdin]
                                             [--file FILE]
                                             [--template TEMPLATE]
                                             [--edgerc EDGERC]
                                             [--section SECTION] [--debug]
                                             [--account-key ACCOUNT_KEY]

optional arguments:
  --show-json           output json
  --use-filterstdin     use stdin for query
  --file FILE           the json file for query
  --template TEMPLATE   use template name for query
  --edgerc EDGERC       Location of the credentials file [$AKAMAI_EDGERC]
  --section SECTION     Section of the credentials file
                        [$AKAMAI_EDGERC_SECTION]
  --debug               DEBUG mode to generate additional logs for
                        troubleshooting
  --account-key ACCOUNT_KEY
                        Account Switch Key

``` 
## Querying Netstorage Users

``` 
usage: akamai query [command] netstorageuser [--show-json] [--use-filterstdin]
                                             [--file FILE]
                                             [--template TEMPLATE]
                                             [--edgerc EDGERC]
                                             [--section SECTION] [--debug]
                                             [--account-key ACCOUNT_KEY]

optional arguments:
  --show-json           output json
  --use-filterstdin     use stdin for query
  --file FILE           the json file for query
  --template TEMPLATE   use template name for query
  --edgerc EDGERC       Location of the credentials file [$AKAMAI_EDGERC]
  --section SECTION     Section of the credentials file
                        [$AKAMAI_EDGERC_SECTION]
  --debug               DEBUG mode to generate additional logs for
                        troubleshooting
  --account-key ACCOUNT_KEY
                        Account Switch Key

``` 
## Querying Control Center Group CPCodes

``` 
usage: akamai query [command] groupcpcodelist [--show-json]
                                              [--use-filterstdin]
                                              [--file FILE]
                                              [--template TEMPLATE]
                                              [--only-contractIds ONLY_CONTRACTIDS [ONLY_CONTRACTIDS ...]]
                                              [--edgerc EDGERC]
                                              [--section SECTION] [--debug]
                                              [--account-key ACCOUNT_KEY]

optional arguments:
  --show-json           output json
  --use-filterstdin     use stdin for query
  --file FILE           the json file for query
  --template TEMPLATE   use template name for query
  --only-contractIds ONLY_CONTRACTIDS [ONLY_CONTRACTIDS ...]
                        limit the query to specific contracts
  --edgerc EDGERC       Location of the credentials file [$AKAMAI_EDGERC]
  --section SECTION     Section of the credentials file
                        [$AKAMAI_EDGERC_SECTION]
  --debug               DEBUG mode to generate additional logs for
                        troubleshooting
  --account-key ACCOUNT_KEY
                        Account Switch Key

``` 
## Generic Filter Template Utility

``` 
usage: akamai query [command] filtertemplate [--get GET] [--type TYPE]
                                             [--filterfile FILTERFILE]
                                             [--args-use-stdin]
                                             [--arg-list ARG_LIST [ARG_LIST ...]]
                                             [--edgerc EDGERC]
                                             [--section SECTION] [--debug]
                                             [--account-key ACCOUNT_KEY]

optional arguments:
  --get GET             get template details
  --type TYPE           the templates by filter type
  --filterfile FILTERFILE
                        define your own template. Intended to be used with one
                        of the arg list flags
  --args-use-stdin      use stdin as alternative to arg-list param
  --arg-list ARG_LIST [ARG_LIST ...]
                        additional args for a JSONPath condition:
                        #JSONPATHCRITERIA.somekey#
  --edgerc EDGERC       Location of the credentials file [$AKAMAI_EDGERC]
  --section SECTION     Section of the credentials file
                        [$AKAMAI_EDGERC_SECTION]
  --debug               DEBUG mode to generate additional logs for
                        troubleshooting
  --account-key ACCOUNT_KEY
                        Account Switch Key

``` 
## Querying Property Mangager Configurations

``` 
usage: akamai query [command] bulksearch [--show-json] [--use-filterstdin]
                                         [--filterfile FILTERFILE]
                                         [--filtername FILTERNAME]
                                         [--contractId CONTRACTID]
                                         [--network NETWORK]
                                         [--use-searchstdin]
                                         [--searchfile SEARCHFILE]
                                         [--searchname SEARCHNAME]
                                         [--edgerc EDGERC] [--section SECTION]
                                         [--debug] [--account-key ACCOUNT_KEY]

optional arguments:
  --show-json           output json
  --use-filterstdin     get filter json from stdin
  --filterfile FILTERFILE
                        the json file to filter results from bulksearch
  --filtername FILTERNAME
                        template name to filter results from bulksearch
  --contractId CONTRACTID
                        limit the bulk search scope to a specific contract
  --network NETWORK     filter the bulk search result to a specific network
                        (staging or production)
  --use-searchstdin     get bulksearch json from stdin
  --searchfile SEARCHFILE
                        get bulksearch from json file
  --searchname SEARCHNAME
                        get bulksearch by name
  --edgerc EDGERC       Location of the credentials file [$AKAMAI_EDGERC]
  --section SECTION     Section of the credentials file
                        [$AKAMAI_EDGERC_SECTION]
  --debug               DEBUG mode to generate additional logs for
                        troubleshooting
  --account-key ACCOUNT_KEY
                        Account Switch Key

``` 
## Bulk Search Template Utility

``` 
usage: akamai query [command] bulksearchtemplate [--get GET] [--edgerc EDGERC]
                                                 [--section SECTION] [--debug]
                                                 [--account-key ACCOUNT_KEY]

optional arguments:
  --get GET             get template by name
  --edgerc EDGERC       Location of the credentials file [$AKAMAI_EDGERC]
  --section SECTION     Section of the credentials file
                        [$AKAMAI_EDGERC_SECTION]
  --debug               DEBUG mode to generate additional logs for
                        troubleshooting
  --account-key ACCOUNT_KEY
                        Account Switch Key

``` 
### Bulk Search Built-In Templates

Ready to go bulk searches. See them when running the command:

``` 
akamai query bulksearchtemplate 

[
 "default.json",
 "gtm-origins.json",
 "origins.json",
 "cpcodes.json"
]
 
``` 

default.json bulk search template finds all configuration's and their cpcode values:

``` 
akamai query bulksearchtemplate --get default.json 

{
 "bulkSearchQuery": {
  "syntax": "JSONPATH",
  "match": "$..behaviors[?(@.name == 'cpCode')].options.value.id"
 }
}
 
``` 

origins.json template finds all configuration and their origins:

``` 
akamai query bulksearchtemplate --get origins.json 

{
 "bulkSearchQuery": {
  "syntax": "JSONPATH",
  "match": "$..behaviors[?(@.name == 'origin')].options.hostname"
 }
}
 
``` 

gtm-origins.json template finds all configurations with gtm origins:

``` 
akamai query bulksearchtemplate --get gtm-origins.json 

{
 "bulkSearchQuery": {
  "syntax": "JSONPATH",
  "match": "$..behaviors[?(@.name == 'origin')].options[?(@.hostname =~ /.*akadns.net$/i)].hostname"
 }
}
 
``` 
### Bulk Search Built-In Filters

Filters limit the bulks earch results. The built-in options are listed when running this command:

``` 
akamai query filtertemplate --type bulksearch 

[
 "result.json",
 "arg-filter-configname-result.json",
 "property.json",
 "default.json",
 "arg-filter-configname.json"
]
 
``` 

default.json filter returns each configuration and the value found from the bulk search

``` 
akamai query filtertemplate --type bulksearch --get default.json 

{
 "propertyName": "$.propertyName",
 "results": "$.matchLocationResults[*]"
}

``` 

result.json filter returns only the value found from the bulk search. This is handy to pipe in values into your own custom scripts for further processing

``` 
akamai query filtertemplate --type bulksearch --get result.json 

{
 "results": "$.matchLocationResults[*]"
}

``` 

property.json filter returns only the property names that found the values from the bulk search. This is handy to pipe in property names into your own custom scripts for further processing

``` 
akamai query filtertemplate --type bulksearch --get property.json 

{
 "results": "$.propertyName"
}
 
``` 
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

### More Bulk Searches - Built-In Origin Example:
Get all the configurations and origin values using the default filter.

```
akamai query bulksearch --network Production --searchname origins.json

```

Output:

```
["propertyName", "results"]
["configuration_1", "origin-1.example.com"]
["configuration_2", "origin-2.example.com"]
["configuration_3", "origin-3.example.com"]
["configuration_4", "origin-4.example.com"]

```

Get all origin values in a flattened list:

```
akamai query bulksearch --network Production --searchname origins.json --filtername result.json

```

Output:

```
origin-1.example.com
origin-2.example.com
origin-3.example.com
origin-4.example.com

```


### More Bulk Searches - Built-In GTM Origin Example:

```
akamai query bulksearch --network Production --searchname gtm-origins.json

```

Output:

```
["propertyName", "results"]
["configuration_1", "origin-1.example.com.akadns.net"]
["configuration_2", "origin-2.example.com.akadns.net"]
["configuration_3", "origin-3.example.com.akadns.net"]
["configuration_4", "origin-4.example.com.akadns.net"]

```

### Build Bulk Searches
Using the [developer.akamai.com](developer.akamai.com) API documentation, you can find a few [bulk search examples](https://developer.akamai.com/api/core_features/property_manager/v1.html#samplebulkupdates) to run.


Option 1:
Pipe in bulk search JSON via STDIN

```
akamai query bulksearch --network Production --use-searchstdin << TEXT_BLOCK
{"bulkSearchQuery":{"syntax":"JSONPATH","match":"$..behaviors[?(@.name == 'sureRoute')].options.testObjectUrl" }}
TEXT_BLOCK

```

Option 2:
Save bulk search JSON to file and pass json file as argument  

```
cat > mysearch.json << TEXT_BLOCK
{"bulkSearchQuery":{"syntax":"JSONPATH","match":"$..behaviors[?(@.name == 'sureRoute')].options.testObjectUrl" }}
TEXT_BLOCK

akamai query bulksearch --network Production --searchfile mysearch.json 

```

Both Output:

```
["propertyName", "results"]
["configuration_1", "/Akamai/sureroute-test-object.html"]
["configuration_2", "/Akamai/sureroute-test-object.html"]
["configuration_3", "/Akamai/sureroute-test-object.html,/Akamai/sureroute-test-object.html"]
["configuration_4", "/Akamai/sureroute-test-object.html"]

```

