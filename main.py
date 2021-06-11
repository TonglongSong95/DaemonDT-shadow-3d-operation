from flask import Flask, request, jsonify
import mymeshIO as m
import shadow_calc
import json
from waitress import serve

app = Flask(__name__)


@app.route('/shadow-3d-operation/version')
def appversion():
    return {
        'version': '1.0.0.0',
        'last update': '11/6/2021'
    }


@app.route('/shadow-3d-operation/bec/devplan/<uuid>/envelope/<env_uuid>/shadowunion', methods=['POST'])
def return_true_shadow(uuid, env_uuid):
    if request.method == 'POST':
        try:
            data = request.form['json']
            data = json.loads(data)
            true_shadow = shadow_calc.true_shadow_geom(data['data'])
            output = {
                'code': 200,
                'data': {
                    "envTrueSV": m.write_mesh(true_shadow),
                    "envTrueSVVolume": m.transform_mesh_to_pcs(true_shadow).volume
                },
                'status': 'success'
            }
            output = jsonify(output)
            output.headers['token'] = data['data']['token']
            return output
        except Exception:
            return {
                'code': 400,
                'status': f"error: invalid data"
            }

    else:
        return {
            'code': 400,
            'status': 'Non post request received'
        }


if __name__ == '__main__':
    app.run()
    serve(app, port=9000, url_scheme='https')
