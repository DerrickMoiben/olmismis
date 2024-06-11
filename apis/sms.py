import africastalking
africastalking.initialize(
    username="kimtai",
    api_key="a08206a77ad698b9d379a2aebf1df80b7cc98a902fa25c11f56c5829ef6960a7"
)
sms = africastalking.SMS
def send_sms(message, phone_numbers):
    sender = "SOKO GARDEN"
    try:
        response = sms.send(message, phone_numbers)
        print(response)
    except Exception as error:
        print("Error is ", error)
	