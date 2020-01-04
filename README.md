# Facial and Voice Recognition

Program that authenticates users with facial and voice recognition using Amazon Web Services' on demand cloud computing platform. Made to learn to use Amazon Web Services and its machine learning services, storage services, and serverless code execution.

The program uses the OpenCV and face_recognition libraries for facial recognition on the local machine. The voice recognition work is done using AWS S3, Lambda, and Transcribe.

![Project AWS Usage](https://imgur.com/B0rfqvR)

A voice recording is recorded on the local computer and then uploaded to the S3 bucket in the cloud. This triggers the Lambda function to automatically take the audio file and send it to Amazon Transcribe. Transcribe extracts the speech from the audio and sends the transcription JSON file back to the S3 bucket. The transcription is then pulled from the S3 bucket to the local computer to check whether it is the correct password.

The password is hashed and stored in a binary file in lieu of a database for simplicity sake and because it isn't the main focus of the project. 

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for testing purposes.

### Setup

What things you need to install the software and how to install them.

```
pip install -r requirements.txt
```

Add images to the 'faces' folder as profiles of people you would like the system to be able to recognize. Make sure the file format is either jpg or png.

## Running

Change directory to the project directory and run the following command:

```
python MakeBinaryFile.py
```

This sets up the password for the program. You can go in the code and change it to whatever you want. For the program to actually work you will need your own AWS Access Key ID and Secret Access Key as well as your own S3 buckets. To actually run the program just run the following command:

```
python FacialVoiceLock.py
```

Instructions will pop up in terminal as you go guiding you through the process of "logging in" using facial and voice recognition.


## Built With

* [face_recognition](https://pypi.org/project/face_recognition/) - Recognize faces from Python or from the command line
* [OpenCV](https://pypi.org/project/opencv-python/) - Wrapper package for OpenCV python bindings
* [NumPy](https://numpy.org/) - Useful for higher level mathematical functions
* [Passlib](https://pypi.org/project/passlib/) - Password hashing library
* [Boto3](https://pypi.org/project/boto3/) - Amazon Web Services (AWS) Software Development Kit (SDK) for Python
* [Amazon S3](https://aws.amazon.com/s3/?nc2=h_ql_prod_fs_s3) - Scalable storage in the cloud
* [Amazon Transcribe](https://aws.amazon.com/transcribe/?nc2=h_ql_prod_ml_ts) - Automatic speech recognition
* [Amazon Lambda](https://aws.amazon.com/lambda/?nc2=h_ql_prod_cp_lbd) - Run code based on triggers
