from flask import Flask, request, jsonify
import mymeshIO as m
import shadow_calc
from waitress import serve
import json

app = Flask(__name__)


@app.route('/shadow-3d-operation/version')
def appversion():
    return {
        'version': '1.0.0.1',
        'last update': '14/6/2021'
    }


@app.route('/shadow-3d-operation/bec/devplan/<uuid>/envelope/<env_uuid>/shadowunion', methods=['POST'])
def return_true_shadow(uuid, env_uuid):
    try:
        if request.method == 'POST':
            try:
                data = request.get_json(force=True)
                true_shadow = shadow_calc.true_shadow_geom(data)
                output = {
                    'code': 200,
                    'data': {
                        "envTrueSV": m.write_mesh(true_shadow),
                        "envTrueSVVolume": m.transform_mesh_to_pcs(true_shadow).volume
                    },
                    'status': 'success'
                }
                output = jsonify(output)
                output.headers['token'] = data['token']
                return output
            except Exception as e:
                return {
                    'code': 500,
                    'status': f"error: {e}"
                }

        else:
            return {
                'code': 500,
                'status': 'Non POST request received'
            }
    except Exception as e:
        return {
            'code': 400,
            'status': f"error: {e}"
        }



if __name__ == '__main__':
    app.run()
    serve(app, port=9000, url_scheme='https')
