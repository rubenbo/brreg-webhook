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
    orgnr = parameters.get("orgnr")
    orgnrstr = str(int(orgnr))
    r = requests.get('https://data.brreg.no/enhetsregisteret/api/enheter/'+orgnrstr)
    json_object = r.json()
    speech = "The name of "+orgnrstr+" is "+json_object['navn']
    return {
    "fulfillmentText": speech,
    "source": "brreg-webhook-nameof"
    }

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print("Starting app on port %d" % port)
    app.run(debug=False, port=port, host='0.0.0.0')