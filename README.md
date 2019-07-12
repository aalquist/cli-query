[![Build Status](https://travis-ci.com/aalquist/cli-query.svg?branch=master)](https://travis-ci.com/aalquist/cli-query)

# cli-query
CLI-Query is a command line interface indended to simplify the interaction of multiple API endpoints available on [developer.akamai.com](https://developer.akamai.com/). 

## Help Text

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
                                             [--args-use-stdin]
                                             [--arg-list ARG_LIST [ARG_LIST ...]]
                                             [--edgerc EDGERC]
                                             [--section SECTION] [--debug]
                                             [--account-key ACCOUNT_KEY]

optional arguments:
  --get GET             get template details
  --type TYPE           the templates by filter type
  --args-use-stdin      use stdin for large arg lists
  --arg-list ARG_LIST [ARG_LIST ...]
                        additional args to inject into any template condition
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
                                         [--use_searchstdin USE_SEARCHSTDIN]
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
  --use_searchstdin USE_SEARCHSTDIN
                        get bulksearch json from stdin
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
