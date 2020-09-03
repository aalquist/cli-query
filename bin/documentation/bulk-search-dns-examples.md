### Pairing Bulk Search and DNS Validation
Here are a few examples how you can pair bulk search and dns


Pipe bulk search results with their hostnames to checkjsondns which will filter search results with a modified set of hosts that are CNAMEd to Akamai

```
akamai query bulksearch --filtername property-hostnames.json | akamai query checkjsondns hostsCNAMED 

```

Output of configurations and their CNAMED hosts:

```
["configuration_1", "hostname1-cnamed.akamai.com,hostname2-cnamed.akamai.com"]
["configuration_2", "hostname3-cnamed.akamai.com"]


```


Pipe bulk search results with their hostnames to checkjsondns which will filter search results with a modified set of configurations that have at least one host CNAMED to Akamai

```
akamai query bulksearch --filtername property-hostnames.json | akamai query checkjsondns configsWithCNAME 

```


Output of configurations with at least one host CNAMEd to Akamai

```
["configuration_1", "hostname1-cnamed.akamai.com,hostname2-cnamed.akamai.com"]
["configuration_2", "hostname3-cnamed.akamai.com, hostname4-notcnamed.akamai.com"]


```


