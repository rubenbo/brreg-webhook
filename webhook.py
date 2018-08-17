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
    language = result.get("languageCode")
    if action == "nameof":
        res = nameof(parameters,language)
    elif action == "nrof":
        res = nrof(parameters,language)
    else:
        raise ValueError("unknown action: "+action)
    return res

def nameof(parameters,language):
    orgnr = parameters.get("orgnr")
    orgnrstr = str(int(orgnr))
    r = requests.get('https://data.brreg.no/enhetsregisteret/api/enheter/'+orgnrstr)
    json_object = r.json()
    if 'navn' in json_object:
        if language=="no":
            speech = "Navnet på organisasjon "+orgnrstr+" er "+json_object['navn']
        else:
            speech = "The name of "+orgnrstr+" is "+json_object['navn']
    else:
        if language=="no":
            speech = "Fant ikke noen organisasjon med orgnr "+orgnrstr
        else:
            speech = "No organisation found with orgnr: "+orgnrstr

    return {
    "fulfillmentText": speech,
    "source": "brreg-webhook-nameof"
    }

def nrof(parameters,language):
    name = parameters.get("org-name")
    r = requests.get('https://data.brreg.no/enhetsregisteret/api/enheter?navn='+name)
    json_object = r.json()
    enheter = json_object['_embedded']['enheter']
    if language=="no":
        speech = "Jeg fant følgende resultater: \n\n\n\n"
        for enhet in enheter:
            speech = speech+"Navn: "+enhet['navn']+" Org.Nr: "+enhet['organisasjonsnummer']+"\n\n"
    else:
        speech = "I found the following results: <br/><br/>"
        for enhet in enheter:
            speech = speech+"Name: "+enhet['navn']+" Org.Nr: "+enhet['organisasjonsnummer']+"\n\n"

    return {
    "fulfillmentText": speech,
    "source": "brreg-webhook-nrof"
    }

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % port)
    app.run(debug=False, port=port, host='0.0.0.0')