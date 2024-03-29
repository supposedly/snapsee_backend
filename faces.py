from tempfile import NamedTemporaryFile

import face_recognition

from database import db, User


def _nmt_from(file_object):
    return 


def _fetch_images():
    return (i.image for i in User.query.all())



def _fetch(query, *attrs):
    start = 0
    while True:
        results = query.slice(start, start + 5).all()
        if results is None:
            break
        for result in results:
            yield [getattr(result, attr) for attr in attrs]
        start += 5


def match(data):
    # data will be a bytestring
    # --
    # load your image
    with NamedTemporaryFile() as f:
        f.write(data)
        to_match = face_recognition.load_image_file(f.name)
    # encoded the loaded image into a feature vector
    to_match_encoded = face_recognition.face_encodings(to_match)[0]

    # iterate over each image
    for image, username in _fetch(User.query, 'image', 'username'):
        with NamedTemporaryFile() as f:
            f.write(image)
            current = face_recognition.load_image_file(f.name)
        # encode the loaded image into a feature vector
        current_encoded = face_recognition.face_encodings(current)[0]
        # match your image with the image and check if it matches
        result = face_recognition.compare_faces(
          [current_encoded], to_match_encoded
        )[0]
        # check if it was a match
        if result:
            return username
    return None
