import sqlite3
import json
from flask import Flask, g, request, send_from_directory
from flask.ext.cors import CORS
import os
import time
import numpy as np

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
        radius = request.form['radius']
        for h in database.query('select * from hotspots'):
            h_loc = (h['x'],h['y'],h['z'])
            if util.dist(loc[:2], h_loc[:2]) < radius:
                direction = util.clockwise(estimate['t'], estimate['R'], h_loc)
                results.append({'description': h['category'], 'direction': direction})
        return json.dumps({'location':estimate, 'nearby':results})
    else:
        return json.dumps({'error': 'could not localize'}), 400

@app.route("/nearbyMessages", methods=['POST'])
def nearby_message():
    estimate = hulop.localize_image(
        request.files['image'],
        request.form['user'],
        request.form['map']
    )
    if estimate:
        loc = estimate['t']
        results = []
        #radius = request.form['radius']
        radius = 5
        for h in database.query('select * from hotspot_messages'):
            h_loc = (h['x'],h['y'],h['z'])
            if util.dist(loc[:2], h_loc[:2]) < radius:
                direction = util.clockwise(estimate['t'], estimate['R'], h_loc)
                results.append({'message': h['message'], 'direction': direction})
        return json.dumps({'location':estimate, 'nearby':results})
    else:
        return json.dumps({'error': 'could not localize'}), 400

@app.route("/createMessage", methods=["POST"])
def create_message():
    estimate = hulop.localize_image(
        request.files['image'],
        request.form['user'],
        request.form['map']
    )
    if estimate:
        loc = estimate['t']
        new_id = database.insert(
            'hotspot_messages',
            ('message','x','y','z'),
            (request.form['message'], loc[0], loc[1], loc[2])
        )
        hotspot = database.query('select * from hotspot_messages where id=?', [new_id], one=True)
        return json.dumps(hotspot), 201
    else:
        return json.dumps({'error': 'could not localize'}), 400

@app.route("/hotspotLayout", methods=['POST', 'GET'])
def hotspot_loyout():
    if request.method == "GET":
        return send_from_directory('buttons', request.args['session'])
    elif request.method == "POST":
        estimate = hulop.localize_image(
            request.files['image'],
            request.form['user'],
            request.form['map']
        )
        K = np.array(hulop.get_K(request.form['user']))
        P = util.get_P_from_Rt(estimate['R'], estimate['t'])
        session = os.path.splitext(request.files['image'].filename)[0]
        print session
        width, height = 2448,1836 # todo, actuall get from image
        buttons = []
        for a in database.query("select * from answers_label where session=?", [session]):
            points_db = database.query("select * from answer_to_3d_point where answer_id=?", [a['id']])
            if not points_db:
                continue
            points = np.array([(p['x'],p['y'],p['z']) for p in points_db])
            points_2d = util.project_3d_to_2d(K, P, points)
            bbox = util.get_bounding(points_2d)
            clipped = util.clip_bbox(bbox, width, height)
            if clipped is not None:
                buttons.append([a['category']] + [str(c) for c in np.nditer(clipped)])
        w_scale, h_scale = util.screen_scale(width, height)
        buttons.insert(0,[str(w_scale*width), str(h_scale*height), str(len(buttons))])
        with open(os.path.join('buttons', session), 'w') as outfile:
            json.dump(buttons, outfile)
        return "",201

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
