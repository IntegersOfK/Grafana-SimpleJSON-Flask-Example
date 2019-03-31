# python 3.7.2
import datetime
import random
from flask import Flask, make_response, jsonify, request
app = Flask(__name__)

def generate_fake_timeseries(fr, to, interval=60000, create=4):
  """Makes some fake timeseries (value, clock) to send back for rendering a chart in our examples below."""
  fr_timestamp = int(datetime.datetime.strptime(fr[:-5]+'+0000', "%Y-%m-%dT%H:%M:%S%z").timestamp()*1000)
  to_timestamp = int(datetime.datetime.strptime(to[:-5]+'+0000', "%Y-%m-%dT%H:%M:%S%z").timestamp()*1000)
  return_series = []
  for r in range(0,create):
    val = random.random()*100
    series_obj = {'target':'series'+str(r+1), 'datapoints':[]}
    series_obj['datapoints'] = [[val, fr_timestamp]]
    a = fr_timestamp
    while a < to_timestamp:
      a += interval
      val += random.randint(-1,1)
      series_obj['datapoints'].append([val, a])
    return_series.append(series_obj)
  return return_series
  
@app.after_request
def after_request(response):
    """Grafana makes POST requests for queries, which aren't on the same domain/port
    from which you're serving the Grafana instance. Therefore we must add the headers
    so the browser will approve the cross domain request. Flask automatically deals
    with OPTIONS requests, which uses the same headers here."""
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
    return response

@app.route('/')
def test_request():
    """When a new datasource is added to Grafana, it does a test to validate that 
    the given datasource server exists."""
    return make_response("ok")

@app.route('/search', methods=['GET', 'POST'])
def search_request():
    """simple-json datasource dropdowns are populated by a post to /search """
    my_dropdown_items = [] # create the dropdowns list
    query_data = request.get_json() # get the query data, which simple-json puts in "target"

    # example 1: in this case, Grafana template variable had "server_list" as the query
    if query_data.get('target') == "server_list":
        my_dropdown_items += ['here', 'are', 'some', 'things', 'for', 'the', 'dropdowns']
    
    # example 2: the query in Grafana template var is "server_values"
    elif query_data.get('target') == "server_values":
        """For this example, we are using the text/values. The difference is that when a user selects one of the dropdowns
        on Grafana, the value will be sent in any queries using that template var instead of the name like the first example
        above. This is useful if you want to provide an id in queries, rather than parsing the human-readable name."""
        my_dropdown_items += [{'text':'here', 'value':'key1'}, {'text':'another', 'value':'key2'}]

    return make_response(jsonify(my_dropdown_items))

@app.route('/query', methods=['GET', 'POST', 'OPTIONS'])
def query_request():
    """simple-json datasource charts are populated by a post to /query """
    query_data = request.get_json()
    print(query_data)
    example_response = []
    
    # First we need to check if the request is for table or time series data
    if query_data and query_data == 'table':
        # send back columns and rows
        pass
    elif query_data:
        # send back value/clock pairs for timeseries charts
      example_response = generate_fake_timeseries(query_data.get('range', {}).get('from'),
                                                  query_data.get('range', {}).get('to'),
                                                  interval=query_data.get('intervalMs', 60000),
                                                  create=4)
    return make_response(jsonify(example_response))

@app.route('/annotations')
def annotation_request():
    """simple-json datasource annotations are populated by a post to /annotations """
    resp = make_response([])
    return jsonify(resp)
    
if __name__ == "__main__":
    app.run(debug=True, port=5000, threaded=True)