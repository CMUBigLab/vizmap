import sqlite3
import json
from flask import Flask, g, request

import util
import database
import hulop

app = Flask(__name__)

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# example response: {t: [], R: [[],[],[]]}
@app.route("/localize", methods=['POST'])
def localize():
    estimate = hulop.localize_image(request.files['image'], request.form['user'], request.form['map'])
    if estimate:
        return json.dumps(estimate)
    else:
        return json.dumps({'error': 'could not localize'}), 400


@app.route("/nearby", methods=['POST'])
def nearby():
    estimate = hulop.localize_image(request.files['image'], request.form['user'], request.form['map'])
    if estimate:
        loc = estimate['t']
        results = []
        for h in database.query('select * from hotspots'):
            if util.dist(loc[:2], (h['x'], h['y'])) < float(request.form['radius']):
                results.append(h)
        return json.dumps({'location':estimate, 'nearby':results})
    else:
        return json.dumps({'error': 'could not localize'}), 400

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
