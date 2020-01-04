import face_recognition as fr
import os
import cv2
import face_recognition
import numpy as np
from passlib.context import CryptContext
import sounddevice as sd
from scipy.io.wavfile import write
import boto3
import json
import time
import pickle

# Hashing configuration parameters
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"],
    default="pbkdf2_sha256",
    pbkdf2_sha256__default_rounds=30000
)


def check_encrypted_password(password, hashed):
    """
    Checks whether raw input password and hashed password
    are equivalent and returns true or false
    :param password: raw input of password
    :param hashed: hashed password to be checked against
    :return: true if equivalent or false if not
    """
    return pwd_context.verify(password, hashed)


def get_transcription():
    """
    Gets the transcription from the AWS bucket that contains
    the transcription from the audio.
    :return: the transcription from the AWS bucket
    """
    s3 = boto3.resource('s3')
    get_last_modified = lambda obj: int(obj.last_modified.strftime('%s'))

    bucket = s3.Bucket("pwd-analysis")
    # List of objects in bucket
    objects = [obj for obj in bucket.objects.all()]

    # Sorts the list of objects to get the most recent transcription first
    objects = [obj for obj in sorted(objects, key=get_last_modified)]
    last_added = objects[-1].key
    # Turn most recent file into object
    content_object = s3.Object('pwd-analysis', last_added)
    file_content = content_object.get()['Body'].read().decode('utf-8')
    json_content = json.loads(file_content)
    transcript = json_content['results']['transcripts'][0]
    blah = str(transcript)
    output = blah[18:-3]
    return output.lower()


def get_encoded_faces():
    """
    Looks through the faces folder and encodes all
    the faces

    :return: dict of (name, image encoded)
    """
    encoded = {}

    for dirpath, dnames, fnames in os.walk("./faces"):
        for f in fnames:
            if f.endswith(".jpg") or f.endswith(".png"):
                face = fr.load_image_file("faces/" + f)
                encoding = fr.face_encodings(face)[0]
                encoded[f.split(".")[0]] = encoding

    return encoded


def unknown_image_encoded(img):
    """
    Encode a face given the file name
    """
    face = fr.load_image_file("faces/" + img)
    encoding = fr.face_encodings(face)[0]

    return encoding


def validate(im):
    """
    Validates user by checking face and then password via voice command
    :param im: the image to check the face in
    :return: simple return when the function terminates
    """
    faces = get_encoded_faces()
    faces_encoded = list(faces.values())
    known_face_names = list(faces.keys())

    img = cv2.imread(im, 1)

    face_locations = face_recognition.face_locations(img)
    unknown_face_encodings = face_recognition.face_encodings(img, face_locations)

    face_names = []
    for face_encoding in unknown_face_encodings:
        # See if the face is a match for the known face(s)
        matches = face_recognition.compare_faces(faces_encoded, face_encoding)
        name = "Unknown"

        # use the known face with the smallest distance to the new face
        face_distances = face_recognition.face_distance(faces_encoded, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]

        face_names.append(name)

    if len(face_names) != 1:
        print("Too little/many faces in frame. Take a picture with only one face in the camera.")
        return
    elif face_names[0] not in ['Akshat']:
        print("Not a valid face. Contact Akshat Dixit for assistance.")
        return
    else:
        k = cv2.waitKey(1)
        print("Hello {}. You will need to say the password. You will have 5 seconds to record your voice. The program "
              "will tell you when it is ready to receive input.\n"
              .format(face_names[0]))

        time.sleep(15)
        print("You have 5 seconds before the program begins recording. Speak when the program says to speak.\n")
        time.sleep(5)
        print("Speak!\n")
        print("Recording...\n")

        fs = 44100  # Sample rate
        seconds = 5  # Duration of recording

        recording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
        sd.wait()  # Wait until recording is finished
        write('output.wav', fs, recording)  # Save as WAV file

        data = open('output.wav', 'rb')  # Create data to upload with audio file

        # Upload to AWS bucket
        s3 = boto3.resource('s3')
        print("Checking voice password...\n")
        s3.Bucket('pwd-analysis').put_object(Key='audioFile/output.wav', Body=data, ACL='public-read')

        # Wait to upload and transcribe in the cloud
        time.sleep(120)

        # Check if audio is equal to password (hashed)
        transcription = get_transcription()
        input_file = open("passFile.bin", "rb")
        hashedPass = pickle.load(input_file)
        input_file.close()

        if check_encrypted_password(transcription, hashedPass):
            print("Access granted")
            return
        else:
            print("Incorrect password. Retry or contact Akshat Dixit for assistance.")
            return


def main():
    """
    Takes an image from the web cam and performs
    image recognition on the captured image
    :return: exit status
    """
    print("Welcome. Press space to capture your face and then press ESC when you are satisfied.\n")
    camera = cv2.VideoCapture(0)

    cv2.namedWindow("Image")

    # Keep taking images until satisfied
    while True:
        ret, frame = camera.read()
        cv2.imshow("Image", frame)
        if not ret:
            break
        k = cv2.waitKey(1)

        if k % 256 == 27:
            # ESC pressed
            print("Done taking image, closing.\n")
            break
        elif k % 256 == 32:
            # SPACE pressed
            img_name = "image.jpg"
            cv2.imwrite(img_name, frame)
            print("Image saved!\n")

    camera.release()
    cv2.destroyAllWindows()

    # Recognizes face and voice password
    validate("image.jpg")


if __name__ == "__main__":
    main()
