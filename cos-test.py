import json
import os
import io
import ibm_boto3

from flask import Flask, Response, render_template #, jsonify, request, send_file
from ibm_botocore.client import Config

PORT = os.getenv('PORT', '5000')
app = Flask(__name__)

thehost = "http://0.0.0.0:5000"
if 'VCAP_APPLICATION' in os.environ:
    appinfo = json.loads(os.environ['VCAP_APPLICATION'])
    thehost = "https://" + appinfo['application_uris'][0]

cos_credentials={
  "apikey": "owOXY_6U6vFRl7sKIFPjA-4zccGwzSfOjxN46qAHiR3C",
  "endpoints": "https://cos-service.bluemix.net/endpoints",
  "iam_apikey_description": "Auto generated apikey during resource-key operation for Instance - crn:v1:bluemix:public:cloud-object-storage:global:a/097c683a217b44dc98831680a2a442a6:6e53fcba-8bc8-4940-9fc0-0bd2836aef60::",
  "iam_apikey_name": "auto-generated-apikey-b1382273-10e9-4755-8a53-b9df84188957",
  "iam_role_crn": "crn:v1:bluemix:public:iam::::serviceRole:Writer",
  "iam_serviceid_crn": "crn:v1:bluemix:public:iam-identity::a/097c683a217b44dc98831680a2a442a6::serviceid:ServiceId-731701f4-f3c8-4d41-9298-d9c99a916cf0",
  "resource_instance_id": "crn:v1:bluemix:public:cloud-object-storage:global:a/097c683a217b44dc98831680a2a442a6:6e53fcba-8bc8-4940-9fc0-0bd2836aef60::"
}

auth_endpoint = 'https://iam.bluemix.net/oidc/token'
service_endpoint = 'https://s3.eu-geo.objectstorage.softlayer.net'

@app.route('/', methods=['GET'])
def GetObjStoreInfo():
    cos = ibm_boto3.client('s3',ibm_api_key_id=cos_credentials['apikey'],ibm_service_instance_id=cos_credentials['resource_instance_id'],ibm_auth_endpoint=auth_endpoint,config=Config(signature_version='oauth'),endpoint_url=service_endpoint)
    bucs = []
    for bucket in cos.list_buckets()['Buckets']:
        bucket['accessURL'] = thehost + "/" + bucket['Name']
        bucs.append(bucket)
    return render_template('main.html', cons = bucs)

@app.route('/<container>', methods=['GET'])
def GetObjStoContainerInfo(container):
    cos = ibm_boto3.client('s3',ibm_api_key_id=cos_credentials['apikey'],ibm_service_instance_id=cos_credentials['resource_instance_id'],ibm_auth_endpoint=auth_endpoint,config=Config(signature_version='oauth'),endpoint_url=service_endpoint)
    bucs = []
    for data in cos.list_objects(Bucket = "testbucketyu")['Contents']:
        data['downloadURL'] = thehost + "/" + container + "/" + data['Key']
        bucs.append(data)
    return render_template('table.html', objs = bucs, container = container)

@app.route('/<container>/<filename>', methods=['GET'])
def GetObjectStorage(container, filename):
    cos = ibm_boto3.client('s3',ibm_api_key_id=cos_credentials['apikey'],ibm_service_instance_id=cos_credentials['resource_instance_id'],ibm_auth_endpoint=auth_endpoint,config=Config(signature_version='oauth'),endpoint_url=service_endpoint)
    obj = cos.get_object(Bucket = container, Key = filename)['Body']
    return Response(obj.read(), mimetype='text/plain', status=200)

def MakeJSONMsgResponse(themsg, statuscode):
    return Response(json.dumps(themsg), mimetype='application/json', status=statuscode)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(PORT), threaded=True, debug=True)
