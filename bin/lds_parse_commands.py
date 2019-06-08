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

            if name.startswith("use-") or name.startswith("show-") or name.startswith("for-"):
                optional.add_argument(
                    "--" + name,
                    required=False,
                    **arg,
                    action="store_true")
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
        default="lds")

    optional.add_argument(
        "--debug",
        help="DEBUG mode to generate additional logs for troubleshooting",
        action="store_true")

    optional.add_argument(
        "--account-key",
        help="Account Switch Key",
        default="")

    actions[name] = action

    #return action

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

    

def main(mainArgs=None):

    (parser, subparsers) = initmain()

    actions = {}

    arg = [ 
                            {"name": "show-json", "help": "output json"},
                            {"name": "use-stdin", "help": "use stdin for query"},
                            {"name": "file", "help": "the json file for query"},
                            {"name": "template", "help": "use template name for query"} ]

    create_sub_command(
        subparsers, "ldslist", "List all cpcode based log delivery configurations",
        optional_arguments=copy.deepcopy(arg),
        required_arguments=None,
        actions=actions)

    create_sub_command(
        subparsers, "template", "prints the default yaml query template",
        optional_arguments=[    {"name": "get", "help": "get template by name"}, 
                                {"name": "type", "help": "the template type"}],
        required_arguments=None,
        actions=actions)
    
    create_sub_command(
        subparsers, "netstoragelist", "List storage groups",
        optional_arguments=copy.deepcopy(arg),
        required_arguments=None,
        actions=actions)

    create_sub_command(
        subparsers, "netstorageuser", "List netstorage users",
        optional_arguments=copy.deepcopy(arg),
        required_arguments=None,
        actions=actions)
    
    create_sub_command(
        subparsers, "groupcpcodelist", "CPCODES assigned to groups",
        optional_arguments=copy.deepcopy(arg),
        required_arguments=None,
        actions=actions)

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
                actions[helparg].print_help()
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
        print(e, file=sys.stderr)
        return 1


def template(args):

    return_value = 0    

    if args.type is None:
        print( "template type is required. here is a list of options", file=sys.stderr )
        queryType = QueryResult(args.type)
        obj = queryType.listQueryTypes()

    else:

        queryType = QueryResult(args.type)
        obj = queryType.listQueryTypes()

        if args.type in obj:

            queryType = QueryResult(args.type)

            if args.get is None:
                obj = queryType.listQuery()
            else:

                obj = queryType.getQuerybyName(args.get)
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

def groupcpcodelist(args):

    fetch = CPCODEFetch()
    queryresult = QueryResult("groupcpcodelist")

    (_ , jsonObj) = fetch.fetchGroupCPCODES(edgerc = args.edgerc, section=args.section, account_key=args.account_key, debug=args.debug)  

    return handleresponse(args, jsonObj, queryresult)

def handleresponse(args, jsonObj, queryresult):

    if not args.show_json:

        if args.use_stdin or args.file is not None :
            
            if args.use_stdin:
                inputString = getArgFromSTDIN()
            else: 
                inputString = getArgFromFile(args.file)

            templateJson = queryresult.loadJson(inputString)
            parsed = queryresult.parseCommandGeneric(jsonObj , templateJson)

        elif args.template is not None :

            templateJson = queryresult.getQuerybyName(args.template)
            parsed = queryresult.parseCommandGeneric(jsonObj, templateJson)

        else:
            
            parsed = queryresult.parseCommandDefault(jsonObj)

    
        for line in parsed:
            print( json.dumps(line) )

    else: 
        print( json.dumps( jsonObj, indent=1 ) )


    return 0   


def argFromInput(arg):

    with open(arg, 'r') as myfile:
            jsonStr = myfile.read()
        
    return jsonStr

def getArgFromSTDIN():
    return argFromInput(0)

def getArgFromFile(jsonPath):
    return argFromInput(jsonPath)
