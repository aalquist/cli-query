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

import sys
import os
import json
from collections import OrderedDict

#seems to be the most reliable jsonpath parser https://github.com/pacifica/python-jsonpath2 
from jsonpath2.path import Path


class QueryResult():

    def __init__(self, name="default"):
        self.name = name

    def getQueryType(self):
       return self.name

    def buildParseExp(self, paths):
        
        try:
            expr = Path.parse_str(paths)
            return expr

        except Exception as identifier:
            raise ValueError("JSON path: {} error: {}".format(paths, identifier))

    
    def parseExp(self, json, expression):
        data = list(map(lambda match_data : match_data.current_value, expression.match( json ) ) )
        return data

    def buildandParseExpression(self, json, paths):
        expr = self.buildParseExp(paths)
        data = self.parseExp(json, expr)
        return data
    
    def loadJson(self, jsonStr):
        #need OrderedDict for some python 3.5 impl 
        data = json.loads(jsonStr, object_pairs_hook=OrderedDict)
        return data
    
    def getJsonQueryFile(self, queryfile):
        with open(queryfile, 'r') as myfile:
            jsonStr = myfile.read()
            data = self.loadJson(jsonStr)
            return data


    def getQuerybyName(self, argname):

        validNames = self.listQuery()

        if argname in validNames:
            obj = self.getNonDefaultQuery(argname)
        else: 
            obj = validNames
        
        return obj

    def listQueryTypes(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        queriesdir = os.path.join(dir_path, "queries" )
        queriesdir = os.listdir(queriesdir)

        returnlist = []

        for f in queriesdir:
            fullname = os.path.join(dir_path, "queries", f)

            if os.path.isdir(fullname):
                returnlist.append(f)
            

        return returnlist

    def listQuery(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        ldsdir = os.path.join(dir_path, "queries", self.getQueryType() )
        listdir = os.listdir(ldsdir)

        returnlist = []

        for f in listdir:
            fullname = os.path.join(dir_path, "queries", self.getQueryType(), f)

            if os.path.isfile(fullname):
                returnlist.append(f)
            

        return returnlist

    def getNonDefaultQuery(self, name):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        queryjson = os.path.join(dir_path, "queries", self.getQueryType(), name )
        return self.getJsonQueryFile(queryjson)

    def getDefaultJsonQuery(self):
        dir_path = os.path.dirname(os.path.realpath(__file__))
        queryjson = os.path.join(dir_path, "queries", self.getQueryType(), "default.json")
        return self.getJsonQueryFile(queryjson)
    
    def parseCommandDefault(self, json, RequireAll = True, JoinValues = True, ReturnHeader=True):
        defaultquery = self.getDefaultJsonQuery()
        return self.parseCommandGeneric(json, defaultquery, RequireAll, JoinValues, ReturnHeader)

    def parseCommandGeneric(self, json , dictObj, RequireAll = True, JoinValues = True, ReturnHeader=True):
        queries = list(dictObj.values() )

        returnList = []

        if ReturnHeader:
            header = list(dictObj.keys())
            returnList.append(header)
            
        result = self.parseElement(json, queries, RequireAll, JoinValues, returnList )

        

        return result

    def parseElement(self, json, paths, RequireAll = True, JoinValues = True, returnList = None):
        
        if returnList is None:
            returnList = []

        jsonExpressions = []
        
        if(isinstance(paths,str) and paths is not None):
            path = self.buildParseExp(paths)
            jsonExpressions.append(path)

        else: 

            for p in paths:

                path = self.buildParseExp(p)
                jsonExpressions.append(path)
                
        #json path on only array elements example
        for obj in json:

            #for each lds config search path
            allMatched = True
            
            matchedArray = []

            for jsonpath_expr in jsonExpressions:
                
                #match = jsonpath_expr.find(obj)
                match = self.parseExp(obj, jsonpath_expr)

                if(len(match) == 0):
                    allMatched = False

                #for each result add to return list
                if JoinValues == True and len(match) > 1:

                    match = list( map( lambda m : str(m), match ) )
                    joinedValue = ",".join(match)
                    matchedArray.append(joinedValue)

                else: 
                    for m in match:
                        matchedArray.append(m)

            if RequireAll == False or allMatched == True:

                if(len(matchedArray) > 0):
                    returnList.append(matchedArray)

        return returnList

