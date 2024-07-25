import africastalking
africastalking.initialize(
    username="kimtai",
    api_key="a08206a77ad698b9d379a2aebf1df80b"
)
sms = africastalking.SMS
def send_sms(message, phone_numbers): 
    sender = "OLMISMISFCS"
    try:
        response = sms.send(message, phone_numbers, sender)
        print(response)
    except Exception as error:
        print("Error is ", error)
	
