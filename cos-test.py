# Import packages you need here,
# and remember to also declare them in the requirements.txt file.
import json
import os
import io
import ibm_boto3
import pandas as pd
import numpy as np
import bokeh
from bokeh.embed import components
from bokeh.plotting import figure, output_file, show
from bokeh.layouts import gridplot
from bokeh.models import HoverTool
from flask import Flask, Response, render_template
from ibm_botocore.client import Config

#network setup
PORT = os.getenv('PORT', '5000')
app = Flask(__name__)

thehost = "http://0.0.0.0:5000"
if 'VCAP_APPLICATION' in os.environ:
    appinfo = json.loads(os.environ['VCAP_APPLICATION'])
    thehost = "https://" + appinfo['application_uris'][0]

#insert your object storage service credential here
cos_credentials={
 
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
    for data in cos.list_objects(Bucket = container)['Contents']:
        data['downloadURL'] = thehost + "/" + container + "/" + data['Key']
        bucs.append(data)
    return render_template('table.html', objs = bucs, container = container)

@app.route('/<container>/<filename>', methods=['GET'])
def GetObjectStorage(container, filename):
    cos = ibm_boto3.client('s3',ibm_api_key_id=cos_credentials['apikey'],ibm_service_instance_id=cos_credentials['resource_instance_id'],ibm_auth_endpoint=auth_endpoint,config=Config(signature_version='oauth'),endpoint_url=service_endpoint)
    obj = cos.get_object(Bucket = container, Key = filename)['Body']
    return Response(obj.read(), mimetype='text/plain', status=200)

@app.route('/<container>/<filename>/plot', methods=['GET'])
def test2(container, filename):
    cos = ibm_boto3.client('s3',ibm_api_key_id=cos_credentials['apikey'],ibm_service_instance_id=cos_credentials['resource_instance_id'],ibm_auth_endpoint=auth_endpoint,config=Config(signature_version='oauth'),endpoint_url=service_endpoint)
    obj = cos.get_object(Bucket = container, Key = filename)['Body']
    b = io.BytesIO(obj.read())
    df = pd.read_csv(b)

    x = df.iloc[:,0].values/1000
    y = df.iloc[:,1].values
    z = np.diff(y)
    z1 = np.divide(z,np.diff(x))
    z = np.insert(z1, 0, 0, axis=0)

    tools_to_show = "wheel_zoom,pan,box_zoom,reset,save"
    plot1 = figure(title="Total Capacitance (Ch1)", x_axis_label='Time [s]', y_axis_label='Capacitance [pF]', tools= tools_to_show)
    plot1.line(x,y,line_width=1.5)
    plot1.add_tools(HoverTool(tooltips=[("Time", "$x"),("Capcitance", "$y"),]))
    plot2 = figure(title="Capacitance Change (Ch1)", x_axis_label='Time [s]', y_axis_label='Cap. Change [pF/s]', tools= tools_to_show)
    plot2.line(x,z1,line_width=1)
    plot2.add_tools(HoverTool(tooltips=[("Time", "$x"),("Capcitance", "$y"),]))
    if len(df.columns) == 2:
        p = gridplot([[plot1,plot2]], plot_width=800, plot_height=400, sizing_mode = "scale_width")
    else:
        y2 = df.iloc[:,2].values
        z2 = np.diff(y2)
        z3 = np.divide(z2,np.diff(x))
        z2 = np.insert(z3, 0, 0, axis=0)
        plot3 = figure(title="Total Capacitance (Ch2)", x_axis_label='Time [s]', y_axis_label='Capacitance [pF]', tools= tools_to_show)
        plot3.line(x,y2,line_width=1.5)
        plot3.add_tools(HoverTool(tooltips=[("Time", "$x"),("Capcitance", "$y"),]))
        plot4 = figure(title="Capacitance Change (Ch2)", x_axis_label='Time [s]', y_axis_label='Cap. Change [pF/s]', tools= tools_to_show)
        plot4.line(x,z2,line_width=1)
        plot4.add_tools(HoverTool(tooltips=[("Time", "$x"),("Capcitance", "$y"),]))
        p = gridplot([[plot1, plot2], [plot3, plot4]], plot_width=800, plot_height=400, sizing_mode = "scale_width")
    script, div = components(p)
    return render_template('plot.html', script = script, div = div)

#debug is turned on here so that you can see the track of the error (500 Internal error when debug=False)
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(PORT), threaded=True, debug=True)
