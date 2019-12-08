from flaskblog import app,db




if __name__ == '__main__':
    app.run(debug=True)


import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging

cred = credentials.Certificate("C:/Users/user/Downloads/the_website/bzypower-firebase-adminsdk.json")

firebase_admin.initialize_app(cred)

#default_app = firebase_admin.initialize_app()

# This registration token comes from the client FCM SDKs.
#registration_token = "AAAAQBaoTqo:APA91bFpIqIPKlGTUVzSyuGwYy_cVYnB7d7-3AOTzokVMpbBoIEutMcfvcQBJYSJxLYXAbCzex2eSuBPM1uVaRPEhrKNaYpdrI_jRuT8tucpDy4uRB8HNUIvJhymgiH0EfRIpJpZxanK"

registration_token = "cPmY3k0rOI4:APA91bG7KF4q581AoVsFc8UUcTlY5rs1q4iBG890OsFKYqnYU8vusuFonC4pNK8KWL9YDzv1RSLgz142BP4tMr7S5ghbZbOwvnpuqS3cTeb9G4K3pP3BYmXOPSdHptMemFCGbcYDWXNT"

# See documentation on defining a message payload.
message = messaging.Message(
    data={
        'score': '850',
        'time': '2:45',
    },
    token=registration_token,

    notification=messaging.Notification(
        title='$GOOG up the day',
        body='$GOOG gained 11.80 points to close at 835.67, n the day. ',
    ),
    android=messaging.AndroidConfig( priority='high', notification=messaging.AndroidNotification( sound='default' ))
)

# Send a message to the device corresponding to the provided
# registration token.
response = messaging.send(message)
# Response is a message ID string.
print('Successfully sent message:', response)
