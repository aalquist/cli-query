
template = """{
    "bulkSearchQuery": {
        "syntax": "JSONPATH",
        "match": "$..behaviors[?(@.name == '###')]"
    }
}"""


with open('behaviorNames.txt') as f:
    lines = f.readlines()
    



    for l in lines:
        b_name = l.strip()
        actual = template.replace("###", b_name)
        temp = "test"
        with open("queries/bulksearch/serverside/behavior_{}.json".format(b_name), "w") as wf:
            wf.write(actual)

        print( actual)