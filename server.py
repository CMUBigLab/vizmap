import sqlite3
import json
from flask import Flask, g, request, send_from_directory
import os
import time

import util
import database
import hulop

app = Flask(__name__)

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
                results.append({'description': h['description'], 'direction':direction})
        return json.dumps({'location':estimate, 'nearby':results})
    else:
        return json.dumps({'error': 'could not localize'}), 400

@app.route("/hotspotLayout", methods=['GET'])
def hotspot_loyout():
    session = request.args.get('session')
    return send_from_directory('./', 'anhong.json')


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
