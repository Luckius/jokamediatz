from flaskblog import app,db




if __name__ == '__main__':
    app.run(debug=True)

    
from pyfcm import FCMNotification


push_service = FCMNotification(api_key="AAAAQBaoTqo:APA91bFpIqIPKlGTUVzSyuGwYy_cVYnB7d7-3AOTzokVMpbBoIEutMcfvcQBJYSJxLYXAbCzex2eSuBPM1uVaRPEhrKNaYpdrI_jRuT8tucpDy4uRB8HNUIvJhymgiH0EfRIpJpZxanK")


def chat_notification(mytoken):
    registration_id = device_id
    message_title = "Bzypower update"
    message_body = "You have "
    result = push_service.notify_single_device(registration_id=registration_id, message_title=message_title, message_body=message_body)
    return result
