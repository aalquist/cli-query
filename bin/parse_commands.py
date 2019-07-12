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

from bin.fetch_lds import LdsFetch
from bin.fetch_netstorage import NetStorageFetch
from bin.fetch_cpcodes import CPCODEFetch
from bin.fetch_propertymanager import PropertyManagerFetch

from bin.query_result import QueryResult



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

def create_sub_command( subparsers, name, help, *, optional_arguments=None, required_arguments=None, actions=None):

    actionname = name
    action = subparsers.add_parser(name=name, help=help, add_help=False)

    if required_arguments:
        required = action.add_argument_group("required arguments")
        for arg in required_arguments:
            name = arg["name"]
            del arg["name"]
            required.add_argument("--" + name,
                                  required=True,
                                  **arg)

    optional = action.add_argument_group("optional arguments")

    if optional_arguments:

        for arg in optional_arguments:
            name = arg["name"]
            del arg["name"]

            if name.startswith("use-") or name.startswith("show-") or name.startswith("for-") or ("-use-" in name ):
                
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
        prog += " [command]"

    parser = MyArgumentParser(
            description='Akamai Query CLI',
            add_help=False,
            prog=prog
    )

    parser.add_argument('--version', action='version', version='%(prog)s ' + PACKAGE_VERSION)

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
        print(str(e), file=sys.stderr)
        return 1    

def combineArgs(defaultArgs, AdditionalArgs = None):

    newArgs = copy.deepcopy(defaultArgs)

    if AdditionalArgs is not None or len(AdditionalArgs) > 0:
        for arg in AdditionalArgs:
            newArgs.append(arg)
    
    return newArgs


def setupCommands(subparsers):

    actions = {}

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
        subparsers, "filtertemplate", "prints a filter template",
        optional_arguments=[    {"name": "get", "help": "get template details"}, 
                                {"name": "type", "help": "the templates by filter type"},
                                {"name": "args-use-stdin", "help": "use stdin for large arg lists"},
                                {"name": "arg-list", "help": "additional args to inject into any template condition"}],
        required_arguments=None,
        actions=actions)
    
    create_sub_command(
        subparsers, "bulksearchtemplate", "prints a bulksearch template",
        optional_arguments=[ {"name": "get", "help": "get template by name"}],
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
        subparsers, "groupcpcodelist", "CPCODES assigned to groups",
        optional_arguments=combineArgs(defaultQueryArgs, [{"name": "only-contractIds", "help": "limit the query to specific contracts"} ]),
        required_arguments=None,
        actions=actions)

    create_sub_command(
        subparsers, "bulksearch", "bulk search property manager configurations",
        optional_arguments=combineArgs(bulkSearchQueryArgs, [
                                                            {"name": "contractId", "help": "limit the bulk search scope to a specific contract"},
                                                            {"name": "network", "help": "filter the bulk search result to a specific network (staging or production)"},
                                                            {"name": "use_searchstdin", "help": "get bulksearch json from stdin"}, 
                                                            {"name": "searchfile", "help": "get bulksearch from json file"}, 
                                                            {"name": "searchname", "help": "get bulksearch by name"}, 
                                                             ]),
        required_arguments=None,
        actions=actions)

    

    return actions

def bulksearchtemplate(args):

    return_value = 0    
    searchType = "bulksearch"
    serverside = True

    if args.get is None:

        print( "template name is required. here is a list of options", file=sys.stderr )
        queryType = QueryResult(searchType)
        obj = queryType.listQueryTypes(serverside=serverside)

    else:

        queryType = QueryResult(searchType)
        obj = queryType.loadTemplate(args.get, serverside=serverside)
        

    print( json.dumps(obj,indent=1) )
    return return_value


def filtertemplate(args):

    return_value = 0    

    if args.type is None:
        print( "template type is required. here is a list of options", file=sys.stderr )
        queryType = QueryResult(args.type)
        obj = queryType.listQueryTypes()

    else:

        queryType = QueryResult(args.type)
        obj = queryType.listQueryTypes()

        if args.type in obj:

            templateArgs = args.arg_list

            if templateArgs is None:
                templateArgs = []

            if args.args_use_stdin:

                stdinStr = getArgFromSTDIN()
                output = stdinStr.split("\n")
                templateArgs.extend( output )
                

            obj = queryType.loadTemplate(args.get, templateArgs)
            
        else:
            print( "template type: {} not found. ".format(args.type), file=sys.stderr )
            return_value = 1
        

    print( json.dumps(obj,indent=1) )
    return return_value

def ldslist(args):

    fetch = LdsFetch()
    queryresult = QueryResult("ldslist")

    (_ , jsonObj) = fetch.fetchCPCodeProducts(edgerc = args.edgerc, section=args.section, account_key=args.account_key, debug=args.debug)  

    return handleresponse(args, jsonObj, queryresult)

def netstoragelist(args):

    fetch = NetStorageFetch()
    queryresult = QueryResult("netstoragelist")
    
    (_ , jsonObj) = fetch.fetchNetStorageGroups(edgerc = args.edgerc, section=args.section, account_key=args.account_key, debug=args.debug)  

    return handleresponse(args, jsonObj, queryresult)

def netstorageuser(args):

    fetch = NetStorageFetch()
    queryresult = QueryResult("netstorageuser")
    
    (_ , jsonObj) = fetch.fetchNetStorageUsers(edgerc = args.edgerc, section=args.section, account_key=args.account_key, debug=args.debug)  

    return handleresponse(args, jsonObj, queryresult)

def bulksearch(args):

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
    
    elif args.searchname is not None :
        postdata = queryresult.loadTemplate(args.searchname, serverside=serverside)

    else:
        postdata = queryresult.loadTemplate("default.json", serverside=serverside)

    (_ , jsonObj) = fetch.bulksearch(edgerc = args.edgerc, section=args.section, account_key=args.account_key, postdata=postdata, contractId=args.contractId, network=args.network ,debug=args.debug)  

    return handleresponse(args, jsonObj, queryresult)

def groupcpcodelist(args):

    fetch = CPCODEFetch()
    queryresult = QueryResult("groupcpcodelist")

    if args.only_contractIds is not None and len(args.only_contractIds) > 0 :
        (_ , jsonObj) = fetch.fetchGroupCPCODES(edgerc = args.edgerc, section=args.section, account_key=args.account_key, onlycontractIds=args.only_contractIds, debug=args.debug, )  
    else:
        (_ , jsonObj) = fetch.fetchGroupCPCODES(edgerc = args.edgerc, section=args.section, account_key=args.account_key, debug=args.debug)  

    return handleresponse(args, jsonObj, queryresult)

def handleresponse(args, jsonObj, queryresult, enableSTDIN = True):

    notJSONOutput = False

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
    
    elif "filtername" in vargs and args.filtername is not None:
        template = args.filtername
        
    else:
        template = None


    if not args.show_json:

        if (enableSTDIN and use_stdin) or (file is not None) :
            
            if (enableSTDIN and use_stdin):
                inputString = getArgFromSTDIN()
            else: 
                inputString = getArgFromFile(file)

            templateJson = queryresult.loadJson(inputString)
            (notJSONOutput, parsed) = flatten(queryresult, jsonObj, templateJson)

        elif template is not None :

            templateJson = queryresult.getQuerybyName(template, throwErrorIfNotFound=True)
            (notJSONOutput, parsed) = flatten(queryresult, jsonObj, templateJson)
            
        else:
            
            parsed = queryresult.parseCommandDefault(jsonObj)

        for line in parsed:

            if notJSONOutput:
                print( line )
            else:
                print( json.dumps(line) )

    else: 
        print( json.dumps( jsonObj, indent=1 ) )


    return 0   

def flatten(queryresult, jsonObj, templateJson):

    notJSONOutput = False
    

    if len(templateJson) == 1 : 
        notJSONOutput = True
        parsed = queryresult.parseCommandGeneric(jsonObj, templateJson, JoinValues=False, ReturnHeader=False)
        
        flattenedParsed = []
        for p in parsed:
            flattenedParsed.extend(p)
        parsed = flattenedParsed

    else:
        parsed = queryresult.parseCommandGeneric(jsonObj, templateJson)

    return (notJSONOutput, parsed)

def argFromInput(arg):

    with open(arg, 'r') as myfile:
            jsonStr = myfile.read()
        
    return jsonStr

def getArgFromSTDIN():
    return argFromInput(0)

def getArgFromFile(jsonPath):
    return argFromInput(jsonPath)
