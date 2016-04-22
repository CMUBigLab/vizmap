from server import app
import database
import hulop
import numpy as np

USER = '1-shrink-0.75'
MAP = 'cole-qolt'

with app.app_context():
    for a in database.query('select answer_id from answer_to_3d_point group by answer_id'):
        ans = database.query('select category,label from answers_label where id=?', [a["answer_id"]], one=True)
        points_db = database.query('select * from answer_to_3d_point where answer_id = ?', [a['answer_id']])
        points = np.array([[p['x'], p['y'], p['z']] for p in points_db])
        center = np.average(np.array(points), 0)
        database.insert(
            'hotspots',
            ('x','y','z','category','details'),
            (center[0],center[1],center[2], ans['category'], ans['label'])
        )
