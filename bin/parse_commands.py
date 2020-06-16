# Copyright 2017 Akamai Technologies, Inc. All Rights Reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import sys
import os
import json
import copy 
import traceback

import subprocess

from bin.fetch_lds import LdsFetch
from bin.fetch_netstorage import NetStorageFetch
from bin.fetch_datastream import DataStreamFetch
from bin.fetch_cpcodes import CPCODEFetch
from bin.fetch_propertymanager import PropertyManagerFetch

from bin.query_result import QueryResult

from bin.send_analytics import Analytics 

from bin.resolve_dns import loadDNSfromHostList, checkJsonArrayDNS

import inspect


import json

PACKAGE_VERSION = "0.0.1"

class MyArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        self.print_help(sys.stderr)
        self.exit(0, '%s: error: %s\n' % (self.prog, message))

def get_prog_name():
    prog = os.path.basename(sys.argv[0])
    if os.getenv("AKAMAI_CLI"):
        prog = "akamai query"
    return prog

def create_sub_command( subparsers, name, help, *, optional_arguments=None, required_arguments=None, actions=None, disableAccountSwitch=False):

    actionname = name
    action = subparsers.add_parser(name=name, help=help, add_help=False)

    if required_arguments:
        required = action.add_argument_group("required arguments")
        for arg in required_arguments:
            name = arg["name"]
            del arg["name"]

            if "positional" in arg and arg["positional"] == True:
                positional = arg["positional"]
                del arg["positional"]
                required.add_argument(name, **arg)
            else:
                required.add_argument("--" + name, required=True, **arg)

    optional = action.add_argument_group("optional arguments")

    if optional_arguments:

        for arg in optional_arguments:
            name = arg["name"]
            del arg["name"]

            if name.startswith("require-") or name.startswith("require_") or name.startswith("skip-") or name.startswith("skip_") or name.startswith("use-") or name.startswith("use_") or name.startswith("show-") or name.startswith("show_") or name.startswith("for-") or name.startswith("for_") or name.startswith("is-") or name.startswith("is_") or ("-use-" in name ) or ("_use_" in name ) or ("-is-" in name ) or ("_is_" in name ):
                
                #enable boolean/flags
                optional.add_argument(
                    "--" + name,
                    required=False,
                    **arg,
                    action="store_true")

            elif name.startswith("only-") or name.startswith("arg-list"):
                
                #enable list args
                optional.add_argument("--" + name,
                                      required=False,
                                      nargs='+',
                                      **arg)

            else:

                if "positional" in arg and arg["positional"] == True:
                    positional = arg["positional"]
                    del arg["positional"]
                    optional.add_argument(name, **arg)

                else:
                    optional.add_argument("--" + name,
                                      required=False,
                                      **arg)

    optional.add_argument(
        "--edgerc",
        help="Location of the credentials file [$AKAMAI_EDGERC]",
        default=os.path.join(os.path.expanduser("~"), '.edgerc'))

    optional.add_argument(
        "--section",
        help="Section of the credentials file [$AKAMAI_EDGERC_SECTION]",
        default="default")

    optional.add_argument(
        "--debug",
        help="DEBUG mode to generate additional logs for troubleshooting",
        action="store_true")

    if not disableAccountSwitch:
        optional.add_argument(
            "--account-key",
            help="Account Switch Key",
            default="")

    actions[actionname] = action

def main(mainArgs=None):

    (parser, subparsers) = initmain()

    actions = setupCommands(subparsers)

    return execute(mainArgs, parser, actions)

def initmain():

    prog = get_prog_name()
    if len(sys.argv) == 1:
        prog += " "

    parser = MyArgumentParser(
            description='Akamai Query CLI',
            add_help=False,
            prog=prog
    )

    #parser.add_argument('--version', action='version', version='%(prog)s ' + PACKAGE_VERSION)

    subparsers = parser.add_subparsers(help='commands', dest="command")

    

    subparsers.add_parser(
        name="help",
        help="Show available help",
        add_help=False).add_argument( 'args', metavar="", nargs=argparse.REMAINDER)

    return (parser, subparsers)

def execute(mainArgs, parser, actions):

    args = None
    
    if mainArgs is None: 
        print("no arguments were provided", file=sys.stderr)
        parser.print_help(sys.stderr)
        return 1

    elif isinstance(mainArgs, list) and len(mainArgs) <= 0: 
        print("no arguments were provided and empty", file=sys.stderr)
        parser.print_help(sys.stderr)
        return 1

    else:
        args = parser.parse_args(mainArgs)

    if args.command == "help":

        if len(args.args) > 0:
            helparg = args.args[0]
            
            if helparg in actions and actions[helparg]:
                parser = actions[helparg]
                parser.print_help()
            else:
                parser.print_help(sys.stderr)
                return 1
        else:
            parser.prog = get_prog_name() + " help [command]"
            parser.print_help()
            
        return 0

    try:
        return getattr(sys.modules[__name__], args.command.replace("-", "_"))(args)

    except Exception as e:
        print("Unexpected Exception: {}".format(str(e)), file=sys.stderr)

        if "debug" in vars(args) and args.debug is not None and args.debug == True:
            traceback.print_exc()

        return 1    

def combineArgs(defaultArgs, AdditionalArgs = None):

    newArgs = copy.deepcopy(defaultArgs)

    if AdditionalArgs is not None or len(AdditionalArgs) > 0:
        for arg in AdditionalArgs:
            newArgs.append(arg)
    
    return newArgs


def setupCommands(subparsers):

    actions = {}

    basicQueryArgs = [ 
                            {"name": "show-json", "help": "output json"},
                            {"name": "templatefile", "help": "the json file for query"},
                            {"name": "templatename", "help": "use template name for query"} ]

    defaultQueryArgs = [ 
                            {"name": "show-json", "help": "output json"},
                            {"name": "use-filterstdin", "help": "use stdin for query"},
                            {"name": "file", "help": "the json file for query"},
                            {"name": "template", "help": "use template name for query"} ]

    bulkSearchQueryArgs = [ 
                            {"name": "show-json", "help": "output json"},
                            {"name": "use-filterstdin", "help": "get filter json from stdin"}, 
                            {"name": "filterfile", "help": "the json file to filter results from bulksearch"},
                            {"name": "filtername", "help": "template name to filter results from bulksearch"} ]
    
    create_sub_command(
        subparsers, "version", "display the version number",
        optional_arguments=[ {"name": "show-git-version", "help": "display git version"} ],
        required_arguments=None,
        actions=actions)

    create_sub_command(
        subparsers, "ldslist", "List all cpcode based log delivery configurations",
        optional_arguments=combineArgs(defaultQueryArgs, []),
        required_arguments=None,
        actions=actions)
    
    create_sub_command(
        subparsers, "netstoragelist", "List storage groups",
        optional_arguments=combineArgs(defaultQueryArgs, []),
        required_arguments=None,
        actions=actions)

    create_sub_command(
        subparsers, "netstorageuser", "List netstorage users",
        optional_arguments=combineArgs(defaultQueryArgs, []),
        required_arguments=None,
        actions=actions)
    
    create_sub_command(
        subparsers, "datastream_agg", "Get aggregate datastream logs",
        optional_arguments=combineArgs(defaultQueryArgs, [{"name": "streamId", "help": "Stream ID"}, {"name": "timeRange", "help": "Supported format: \d+[smh]. Eg: 2s, 2m, 2h"} ]),
        required_arguments=None,
        disableAccountSwitch=True,
        actions=actions)

    create_sub_command(
        subparsers, "datastream_raw", "Get raw datastream raw logs",
        optional_arguments=combineArgs(defaultQueryArgs, [{"name": "streamId", "help": "Stream ID"}, {"name": "timeRange", "help": "Supported format: \d+[smh]. Eg: 2s, 2m, 2h"} ]),
        required_arguments=None,
        disableAccountSwitch=True,
        actions=actions)

    create_sub_command(
        subparsers, "groupcpcodelist", "CPCODES assigned to groups",
        optional_arguments=combineArgs(defaultQueryArgs, [{"name": "only-contractIds", "help": "limit the query to specific contracts"} ]),
        required_arguments=None,
        actions=actions)

    create_sub_command(
        subparsers, "filtertemplate", "prints a filter template",
        optional_arguments=[    {"name": "get", "help": "get template details"}, 
                                {"name": "type", "help": "the templates by filter type"},
                                {"name": "filterfile", "help": "use your own template from your file system"},
                                {"name": "args-use-stdin", "help": "use your own template from STDIN"},
                                {"name": "arg-list", "help": "additional args for a JSONPath condition: #JSONPATHCRITERIA.somekey#"}],
        required_arguments=None,
        actions=actions)

    create_sub_command(
        subparsers, "bulksearch", "bulk search property manager configurations",
        optional_arguments=combineArgs(bulkSearchQueryArgs, [
                                                            {"name": "contractId", "help": "limit the bulk search scope to a specific contract"},
                                                            {"name": "network", "help": "filter the bulk search result to a specific network (staging or production)"},
                                                            {"name": "use-searchstdin", "help": "get bulksearch json from stdin"}, 
                                                            {"name": "searchfile", "help": "get bulksearch from json file"}, 
                                                            {"name": "searchname", "help": "get bulksearch by name"}, 
                                                            {"name": "use-union-filter", "help": "union filter results"}, 
                                                            {"name": "skip-header", "help": "hide filter header from output"}, 
                                                            {"name": "show-nested-list", "help": "disable JSON Array to String concatenation for JQ @CSV"}
                                                             ]),
        required_arguments=None,
        actions=actions)
    
    create_sub_command(
        subparsers, "bulksearchtemplate", "prints a bulksearch template",
        optional_arguments=[ 
                {"name": "get", "help": "get template by name"},
                {"name": "searchfile", "help": "use your own bulk search template from your file system"},
                {"name": "arg-list", "help": "additional args for a JSONPath condition: #JSONPATHCRITERIA.somekey#"}
                ],
        required_arguments=None,
        actions=actions)

    create_sub_command(
        subparsers, "checkdns", "dns filtering tool",
        
        #requireAnyAkamai=True, requireAllAkamai=False, returnAkamaiHosts

        optional_arguments=combineArgs(basicQueryArgs, [ 
                {"name": "json-dns-index", "help": "zero based index where hostname is located", "default" : 1},
                {"name": "require-AnyAkamai", "help": "requireAnyAkamai", "default" : True},
                {"name": "require-AllAkamai", "help": "requireAllAkamai", "default" : False},
                {"name": "return-AkamaiHosts", "help": "returnAkamaiHosts"},
                {"name": "type", "help": "the DNS record type (A,AAAA,CNAME,NS)"},
                {"name": "domain", "help": "a list of domains", "positional" : True, "nargs" : '*'}]),
        required_arguments=None,
        actions=actions)
    

    return actions

def bulksearchtemplate(args):
    
    path = inspect.getframeinfo(inspect.currentframe()).function
    thread = Analytics().async_send_analytics(path=path, debug=args.debug)

    return_value = 0    
    searchType = "bulksearch"
    serverside = True

    if args.get is None and args.searchfile is None:

        print( "template name is required. here is a list of options", file=sys.stderr )
        queryType = QueryResult(searchType)
        obj = queryType.listQueryTypes(serverside=serverside)

    else:

        queryType = QueryResult(searchType)
        obj = queryType.loadTemplate(args.get, serverside=serverside)

        templateArgs = args.arg_list

        if templateArgs is None:
            templateArgs = []

        if "searchfile" in vars(args) and args.searchfile is not None:
            obj = queryType.loadTemplate(args.get, templateArgs=templateArgs, serverside=serverside, templatefile=args.searchfile)
        else:
            obj = queryType.loadTemplate(args.get, templateArgs=templateArgs, serverside=serverside)    

    print( json.dumps(obj,indent=1) )
    thread.join()
    return return_value

def checkdns(args):
    path = inspect.getframeinfo(inspect.currentframe()).function
    thread = Analytics().async_send_analytics(path=path, debug=args.debug)

    queryresult = QueryResult("doh")
    
    

    if args.domain is None or len(args.domain) < 1:
        print("... waiting for domain list or json docs from stdin...", file=sys.stderr )
        stdinStr = getArgFromSTDIN()
        print("... got list from user input...", file=sys.stderr )
        stdinStr = str.rstrip(stdinStr)
        lines = stdinStr.split(os.linesep)

    else:
        lines = args.domain

    #check each line if any line has JSON chars (but not including comma or space)
    linesNotDNS = list(filter(lambda dns : len([e for e in ["{", "}", "[", "]", ":" ] if e in dns]) > 0, lines ))

    inputIsJSON = len(linesNotDNS) > 0

    if inputIsJSON == False:
        checkFilterArgs(args, queryresult)

        updatedLines = None
        for dns in lines:
            split = [" ", ","]
            splitCharFound = [e for e in split if e in dns]

            if len(splitCharFound) > 0:
                updatedLines = list()
                for split in splitCharFound:

                    
                    newDns = str.strip(dns)
                    updatedLines.extend( newDns.split(split) ) 

        if updatedLines is not None:
            lines = updatedLines

        jsonObj = loadDNSfromHostList(lines, recoredType=None)
        if "resolution" in jsonObj:
            jsonObj= jsonObj["resolution"]
            thread.join()
            return handleresponse(args, jsonObj, queryresult, enableSTDIN=False, RequireAll=False, Debug=args.debug)
        else:
            print("... something went wrong with response", file=sys.stderr )

    else:
        print("... accepting JSON input and skipping any template output", file=sys.stderr )
        
        try:
            args.json_dns_index = int(args.json_dns_index)

        except ValueError:
            print("... domain index must be an int {}".format(args.json_dns_index), file=sys.stderr )
            return 1
        
        
        returnAkamaiHosts = None if args.return_AkamaiHosts is None else True if "True" == args.return_AkamaiHosts else False
        
        print("... running dns check with requireAnyAkamai={}, requireAllAkamai={}, returnAkamaiHosts={}".format(args.require_AnyAkamai, args.require_AllAkamai, returnAkamaiHosts), file=sys.stderr )

        jsonObj= checkJsonArrayDNS(lines, arrayHostIndex=args.json_dns_index, requireAnyAkamai=args.require_AnyAkamai, requireAllAkamai=args.require_AllAkamai, returnAkamaiHosts=returnAkamaiHosts)
        
        printResponse(jsonObj,JSONOutput=inputIsJSON)
        thread.join()
        return 0   


def filtertemplate(args):

    path = inspect.getframeinfo(inspect.currentframe()).function
    thread = Analytics().async_send_analytics(path=path)

    return_value = 0    

    if args.type is None and args.filterfile is None:
        print( "template type is required. here is a list of options", file=sys.stderr )
        queryType = QueryResult(args.type)
        obj = queryType.listQueryTypes()

    else:

        
        queryType = QueryResult(args.type)
        obj = queryType.listQueryTypes()

        if args.type in obj or args.filterfile is not None:

            templateArgs = args.arg_list

            if templateArgs is None:
                templateArgs = []

            if args.args_use_stdin:

                stdinStr = getArgFromSTDIN()
                output = stdinStr.split("\n")
                templateArgs.extend( output )
                
            if "filterfile" in vars(args) and args.filterfile is not None:
                obj = queryType.loadTemplate(args.get, templateArgs=templateArgs, templatefile=args.filterfile)
            else:
                obj = queryType.loadTemplate(args.get, templateArgs=templateArgs)

        
        
        else:
            print( "template type: {} not found. ".format(args.type), file=sys.stderr )
            return_value = 1
        

    print( json.dumps(obj,indent=1) )

    thread.join()
    return return_value



def version(args):
    
    SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.expanduser(__file__)))
    SCRIPT_DIR = os.path.normpath(os.path.join(SCRIPT_DIR, '..'))

    

    if args.show_git_version:
        cmd = "cd {}; git log -1 --pretty=%H; cd -".format(SCRIPT_DIR)
        returned_value = subprocess.call(cmd, shell=True, stderr=subprocess.DEVNULL)
        return returned_value
    else:

        jsonFilePath = os.path.realpath(os.path.join(SCRIPT_DIR, "cli.json"))
        with open(jsonFilePath, 'r') as myfile:
            jsonStr = myfile.read()
        
        jsonObj = json.loads(jsonStr)
        version = jsonObj["commands"][0]["version"]
        print(version)

    return 0

def ldslist(args):

    path = inspect.getframeinfo(inspect.currentframe()).function
    thread = Analytics().async_send_analytics(path=path, debug=args.debug)

    fetch = LdsFetch()
    queryresult = QueryResult("ldslist")

    checkFilterArgs(args, queryresult)
    (_ , jsonObj) = fetch.fetchCPCodeProducts(edgerc = args.edgerc, section=args.section, account_key=args.account_key, debug=args.debug)  

    thread.join()
    return handleresponse(args, jsonObj, queryresult, Debug=args.debug)

def netstoragelist(args):

    path = inspect.getframeinfo(inspect.currentframe()).function
    thread = Analytics().async_send_analytics(path=path, debug=args.debug)

    fetch = NetStorageFetch()
    queryresult = QueryResult("netstoragelist")
    
    checkFilterArgs(args, queryresult)
    (_ , jsonObj) = fetch.fetchNetStorageGroups(edgerc = args.edgerc, section=args.section, account_key=args.account_key, debug=args.debug)  
    
    thread.join()
    return handleresponse(args, jsonObj, queryresult, Debug=args.debug)

def netstorageuser(args):

    path = inspect.getframeinfo(inspect.currentframe()).function
    thread = Analytics().async_send_analytics(path=path, debug=args.debug)

    fetch = NetStorageFetch()
    queryresult = QueryResult("netstorageuser")
    
    checkFilterArgs(args, queryresult)
    (_ , jsonObj) = fetch.fetchNetStorageUsers(edgerc = args.edgerc, section=args.section, account_key=args.account_key, debug=args.debug)  
    
    thread.join()
    return handleresponse(args, jsonObj, queryresult, Debug=args.debug)

def datastream_agg(args):

    path = inspect.getframeinfo(inspect.currentframe()).function
    thread = Analytics().async_send_analytics(path=path, debug=args.debug)

    fetch = DataStreamFetch()
    queryresult = QueryResult("datastream_aggregate")

    logType="aggregate"

    checkFilterArgs(args, queryresult)
    (_ , jsonObj) = fetch.fetchLogs(edgerc = args.edgerc, section=args.section, streamId=args.streamId, timeRange=args.timeRange, logType=logType, debug=args.debug)  

    thread.join()
    return handleresponse(args, jsonObj, queryresult, RequireAll=False, HideHeader=True, Debug=args.debug)

def datastream_raw(args):

    path = inspect.getframeinfo(inspect.currentframe()).function
    thread = Analytics().async_send_analytics(path=path, debug=args.debug)

    fetch = DataStreamFetch()
    queryresult = QueryResult("datastream_raw")

    logType="raw"

    checkFilterArgs(args, queryresult)
    (_ , jsonObj) = fetch.fetchLogs(edgerc = args.edgerc, section=args.section, streamId=args.streamId, timeRange=args.timeRange, logType=logType, debug=args.debug)  

    thread.join()
    return handleresponse(args, jsonObj, queryresult, RequireAll=False, HideHeader=True,  Debug=args.debug)

def bulksearch(args):

    path = inspect.getframeinfo(inspect.currentframe()).function
    thread = Analytics().async_send_analytics(path=path, debug=args.debug)

    fetch = PropertyManagerFetch()
    queryresult = QueryResult("bulksearch")
    serverside = True

    if args.use_searchstdin and args.use_filterstdin:
        raise ValueError("Both args.use_searchstdin and args.use_filterstdin maynot be True")
    
    if args.use_searchstdin or args.searchfile is not None :
        if (args.use_searchstdin):
            inputString = getArgFromSTDIN()
        else: 
            inputString = getArgFromFile(args.searchfile)

        postdata = queryresult.loadJson(inputString)

        if not queryresult.isJsonServerSide(postdata):
            postdataStr = json.dumps(postdata)
            print("Search JSON Format Error:\n{}".format(postdataStr), file=sys.stderr )
            raise ValueError("bulksearch JSON is not correct format")
    
    elif args.searchname is not None :
        postdata = queryresult.loadTemplate(args.searchname, serverside=serverside)

        if isinstance(postdata, list):
            print("Error: choose from one of these:", file=sys.stderr)
            printJsonStr = json.dumps(postdata, indent=1)
            print(printJsonStr, file=sys.stderr)
            raise ValueError("{} not found".format(args.searchname))
        
    else:
        postdata = queryresult.loadTemplate("default.json", serverside=serverside)

    checkFilterArgs(args, queryresult)

    (_ , jsonObj) = fetch.bulksearch(edgerc = args.edgerc, section=args.section, account_key=args.account_key, postdata=postdata, contractId=args.contractId, network=args.network, debug=args.debug)  

    thread.join()
    RequireAll = not args.use_union_filter
    HideHeader = args.skip_header
    SkipConcat = not args.show_nested_list

    return handleresponse(args, jsonObj, queryresult, RequireAll=RequireAll, HideHeader=HideHeader, concatForJQCSV=SkipConcat, Debug=args.debug)

def groupcpcodelist(args):

    path = inspect.getframeinfo(inspect.currentframe()).function
    thread = Analytics().async_send_analytics(path=path, debug=args.debug)

    fetch = CPCODEFetch()
    queryresult = QueryResult("groupcpcodelist")

    checkFilterArgs(args, queryresult)

    if args.only_contractIds is not None and len(args.only_contractIds) > 0 :
        (_ , jsonObj) = fetch.fetchGroupCPCODES(edgerc = args.edgerc, section=args.section, account_key=args.account_key, onlycontractIds=args.only_contractIds, debug=args.debug, )  
    else:
        (_ , jsonObj) = fetch.fetchGroupCPCODES(edgerc = args.edgerc, section=args.section, account_key=args.account_key, debug=args.debug)  

    thread.join()
    return handleresponse(args, jsonObj, queryresult, Debug=args.debug)

def checkFilterArgs(args, queryresult, skipErrorMsg=False):

    (isFilterJSON, _, filterJsonTemplate, _, _) = verifyInputTemplateFilter(args, queryresult)

    if isFilterJSON == False and filterJsonTemplate is not None:
        if not skipErrorMsg:
            printJsonStr = json.dumps(filterJsonTemplate)
            print("Error:\n{}".format(printJsonStr), file=sys.stderr )
        raise ValueError("filter json is not in correct format")

def checkTemplateNotFoundError(queryresult, template):
        try:
            templatefound = queryresult.getQuerybyName(template, throwErrorIfNotFound=True)

        except Exception as ex:

            if len(ex.args) > 1:
                availableargs = ex.args[1]
                print("Error: choose from one of these:", file=sys.stderr)
                printJsonStr = json.dumps(availableargs, indent=1)
                print(printJsonStr, file=sys.stderr)
            
            raise ValueError("{} not found".format(template))
        
def verifyInputTemplateFilter(args, queryresult, enableSTDIN = True):

    #normalize args
    vargs = vars(args)

    if "use_filterstdin" in vargs and args.use_filterstdin:
        use_stdin = True

    else:
        use_stdin = False

    if ("file" in vargs and args.file is not None):
        file = args.file

    elif ("filterfile" in vargs and args.filterfile is not None):
        file = args.filterfile

    else:
        file = None

    if "template" in vargs and args.template is not None:
        template = args.template
        checkTemplateNotFoundError(queryresult, template)

    elif "filtername" in vargs and args.filtername is not None:
        template = args.filtername
        checkTemplateNotFoundError(queryresult, template)
        
    else:
        template = None

    passedFilterCheck = True
    templateJson = None

    if not args.show_json:

        if (enableSTDIN and use_stdin) or (file is not None) :
            
            if (enableSTDIN and use_stdin):
                inputString = getArgFromSTDIN()
            else: 
                inputString = getArgFromFile(file)

            templateJson = queryresult.loadJson(inputString)
            passedFilterCheck = not queryresult.isJsonServerSide(templateJson)
    
    return (passedFilterCheck, template, templateJson, file, use_stdin)

def handleresponse(args, jsonObj, queryresult, enableSTDIN = True, RequireAll = True, HideHeader = False, concatForJQCSV = True, Debug=False):

    notJSONOutput = False
    ReturnHeader = not HideHeader

    (_, template, templateJson, file, use_stdin) = verifyInputTemplateFilter(args, queryresult, enableSTDIN=enableSTDIN)


    if not args.show_json:

        if (enableSTDIN and use_stdin) or (file is not None) :
            
            if (enableSTDIN and use_stdin):
                inputString = getArgFromSTDIN()
            else: 
                inputString = getArgFromFile(file)

            templateJson = queryresult.loadJson(inputString)
            
            (notJSONOutput, parsed) = flatten(queryresult, jsonObj, templateJson, ReturnHeader=ReturnHeader, concatForJQCSV=concatForJQCSV, Debug=Debug)

        elif template is not None :

            templateJson = queryresult.getQuerybyName(template, throwErrorIfNotFound=True)
            
            (notJSONOutput, parsed) = flatten(queryresult, jsonObj, templateJson, ReturnHeader=ReturnHeader, concatForJQCSV=concatForJQCSV, Debug=Debug)
            
        else:
            
            parsed = queryresult.parseCommandDefault(jsonObj,RequireAll=RequireAll, ReturnHeader=ReturnHeader, concatForJQCSV=concatForJQCSV, Debug=Debug)

        printResponse(parsed, JSONOutput=(not notJSONOutput))

    else: 
        print( json.dumps( jsonObj, indent=1 ) )


    return 0   

def printResponse(parsed, JSONOutput=False):
    
    for line in parsed:

        if not JSONOutput:
            print( line )
        else:
            print( json.dumps(line) )

def flatten(queryresult, jsonObj, templateJson, ReturnHeader=True, concatForJQCSV=True, Debug=False):

    notJSONOutput = False
    
    allValuesAreNotJsonInstances = True

    if len(templateJson) == 1 : 
        notJSONOutput = True
        parsed = queryresult.parseCommandGeneric(jsonObj, templateJson, JoinValues=False, ReturnHeader=False, concatForJQCSV=True, Debug=Debug)
        
        flattenedParsed = []
        for p in parsed:

            if allValuesAreNotJsonInstances and len(p) == 1 and isinstance(p[0], dict):
                allValuesAreNotJsonInstances = False

            flattenedParsed.extend(p)
        parsed = flattenedParsed

    else:
        parsed = queryresult.parseCommandGeneric(jsonObj, templateJson, ReturnHeader=ReturnHeader, concatForJQCSV=concatForJQCSV, Debug=Debug)

    return (notJSONOutput and allValuesAreNotJsonInstances, parsed)

def argFromInput(arg):

    with open(arg, 'r') as myfile:
            jsonStr = myfile.read()
        
    return jsonStr

def getArgFromSTDIN():
    return argFromInput(0)

def getArgFromFile(jsonPath):
    return argFromInput(jsonPath)
