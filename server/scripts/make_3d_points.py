from server import app
import database
import hulop

USER = '1-shrink-0.75'
MAP = 'cole-qolt'

IMAGE_DIR = './examples/'

with app.app_context():
    for s in database.query('select session from answers_label group by session'):
        filename = "{0}{1}.png".format(IMAGE_DIR, s['session'])
        bounding_boxes = []
        answer_ids = []
        for answer in database.query('select * from answers_label where session = ?', [s['session']]):
            if answer['x1']:
                bounding_boxes.append([answer['x1'],answer['y1'],answer['x2'],answer['y2']])
                answer_ids.append(answer['id'])
        with open(filename, 'rb') as image:
            points = hulop.bounding_to_3d(image, USER, MAP, bounding_boxes)
        for i, box in enumerate(points):
            if len(box) < 1:
                x1,y1,x2,y2 =  bounding_boxes[i]
                print "No points found for image '{0}' ({1},{2},{3},{4})".format(filename,x1,y1,x2,y2)
            for p in box:
                print filename, p['x'],p['y'],p['z']
                database.insert(
                    'answer_to_3d_point',
                    ('answer_id','x','y','z'),
                    (answer_ids[i], p['x'],p['y'],p['z'])
                )
