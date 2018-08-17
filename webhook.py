import json
import os
import requests

from flask import Flask
from flask import request
from flask import make_response

# Flask app should start in global layout
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    print(json.dumps(req, indent=4))
    
    res = makeResponse(req)
    
    res = json.dumps(res, indent=4)
    # print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r

def makeResponse(req):
    result = req.get("queryResult")
    parameters = result.get("parameters")
    action = result.get("action")
    if action == "nameof":
        res = nameof(parameters)
    elif action == "nrof":
        res = nrof(paramters)
    else:
        raise ValueError("unknown action: "+action)
    return res

def nameof(parameters):
    orgnr = parameters.get("orgnr")
    orgnrstr = str(int(orgnr))
    r = requests.get('https://data.brreg.no/enhetsregisteret/api/enheter/'+orgnrstr)
    json_object = r.json()
    if 'navn' in json_object:
        speech = "The name of "+orgnrstr+" is "+json_object['navn']
    else:
        speech = "No organisation found with orgnr: "+orgnrstr

    return {
    "fulfillmentText": speech,
    "source": "brreg-webhook-nameof"
    }

def nrof(parameters):
    name = parameters.get("org-name")
    r = requests.get('https://data.brreg.no/enhetsregisteret/api/enheter?navn='+name)
    json_object = r.json()
    enheter = json_object['_embedded']['enheter']
    speech = "I found the following results: "
    for enhet in enheter:
        speech = speech+"Name: "+enhet['navn']+" Org.Nr: "+enhet['organisasjonsnummer']+"\n"

    return {
    "fulfillmentText": speech,
    "source": "brreg-webhook-nrof"
    }

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % port)
    app.run(debug=False, port=port, host='0.0.0.0')