import sqlite3
import json
from flask import Flask, g, request, send_from_directory
from flask.ext.cors import CORS
import os
import time
import numpy as np
from PIL import Image
from collections import defaultdict


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
        radius = request.form['radius']
        #radius = 5
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
        session = request.args['session']
        #session = str(3846)
        return send_from_directory('buttons', session)
    elif request.method == "POST":
        session = os.path.splitext(request.files['image'].filename)[0]
        im = Image.open(request.files['image'])
        width, height = im.size
        w_scale, h_scale = util.screen_scale(width, height)
        request.files['image'].seek(0)
        buttons = []
        points_db = database.query("select * from answer_to_3d_point")
        answer_ids = [p['answer_id'] for p in points_db]
        points_3d = [[p['x'],p['y'],p['z']] for p in points_db]
        points_2d = hulop.project_3d_to_2d(
            request.files['image'],
            request.form['user'],
            request.form['map'],
            points_3d
        )
        if points_2d == None:
            return json.dumps({'error': 'could not localize'}), 400
        points_by_a = defaultdict(list)
        for i,a in enumerate(answer_ids):
            points_by_a[a].append(points_2d[i])
        for k,v in points_by_a.iteritems():
            if v:
                p = np.array(v)
                bbox = util.get_bounding(p)
                a = database.query("select * from answers_label where id = ?", [k], one=True)
                clipped = util.clip_bbox(bbox, width, height)
                if clipped is not None:
                    clipped += 0.0001
                    buttons.append([a['category']] + [str(c) for c in np.nditer(clipped)])
        buttons.insert(0,[str(w_scale*width), str(h_scale*height), str(len(buttons))])
        with open(os.path.join('buttons', session), 'w') as outfile:
            json.dump(buttons, outfile)
        return "",201

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
