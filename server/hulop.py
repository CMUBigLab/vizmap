import requests

HULOP_API = 'http://localhost:3000/'

def localize_image(image, user, map_name):
    data = {'user': user, 'map': map_name}
    r = requests.post(HULOP_API + 'localize', files={'image':image}, data=data)
    if r.status_code != 200:
        print r.text
        return None
    else:
        estimate = r.json()['estimate']
        if len(estimate['t']) < 3 or len(estimate['R']) < 3:
            return None
        else:
            return estimate

def bounding_to_3d(image, user, map_name, bounding):
    data = {'user': user, 'map': map_name, 'bounding': bounding}
    r = requests.post(HULOP_API + 'bounding', files={'image':image}, data=data)
    if r.status_code != 200:
        print r.text
        return None
    else:
        results = r.json()['boundingBoxResults']
        return results

def get_K(user):
    r = requests.get(HULOP_API + 'user', data={'user': user})
    if r.status_code != 200:
        print r.text
        return None
    else:
        return r.json()['K']
