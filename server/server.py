import sqlite3
import json
from flask import Flask, g, request, send_from_directory
from flask.ext.cors import CORS
import os
import time

import util
import database
import hulop

app = Flask(__name__)
CORS(app)

# example response: {location:{t: [], R: [[],[],[]]}}
@app.route("/localize", methods=['POST'])
def localize():
    image = request.files['image']
    estimate = hulop.localize_image(image, request.form['user'], request.form['map'])
    image.stream.seek(0)
    image.save(os.path.join('./images', image.filename))
    if estimate:
        return json.dumps({'location': estimate})
    else:
        return json.dumps({'error': 'could not localize'}), 400

@app.route("/nearby", methods=['POST'])
def nearby():
    estimate = hulop.localize_image(
        request.files['image'],
        request.form['user'],
        request.form['map']
    )
    if estimate:
        loc = estimate['t']
        results = []
        for h in database.query('select * from hotspots'):
            h_loc = (h['x'],h['y'],h['z'])
            if util.dist(loc[:2], h_loc[:2]) < float(request.form['radius']):
                direction = util.clockwise(estimate['t'], estimate['R'], h_loc)
                results.append({'description': h['category'], 'direction': direction})
        return json.dumps({'location':estimate, 'nearby':results})
    else:
        return json.dumps({'error': 'could not localize'}), 400

@app.route("/hotspotLayout", methods=['POST'])
def hotspot_loyout():
    estimate = hulop.localize_image(
        request.files['image'],
        request.form['user'],
        request.form['map']
    )
    K = np.array(hulop.get_K(request.form['user']))
    P = util.get_P_from_Rt(estimate['R'], estimate['t'])
    buttons = []
    for a in database.query("select * from answer_labels where session_id=?", [session]):
        points_db = database.query("select * from answer_to_3d_point where answer_id=?", [a['id']])
        points = np.array([(p['x'],p['y'],p['z']) for p in points_db])
        points_2d = util.project_3d_to_2d(K, P, points)
        utils.get_bounding(points_2d)
    # calculate bounding boxes of all hotspots
    # see if bounding boxes are in camera screen
    # this means we are going to need the camera matrix K
    # x = K * [R|t] * X

    return send_from_directory('./', 'anhong.json')

@app.route("/hotspots", methods=['GET'])
def hotspots():
    return json.dumps({'hotspots':database.query('select * from hotspots')})

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
