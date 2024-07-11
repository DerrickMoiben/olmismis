import json
import africastalking

# Initialize the africastalking api
africastalking.initialize(
    username="kimtai",
    api_key="a08206a77ad698b9d379a2aebf1df80b7cc98a902fa25c11f56c5829ef6960a7"
)

# Create and instance of the SMS class in africastalking
sms = africastalking.SMS

def read_unsent_messages(file_path):
    """Read unsent messages from a JSON file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    
def write_unsent_messages(file_path, data):
    """Write unsent messages to a JSON file."""
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)
        f.write('\n')
    
def send_sms(message, phone_numbers):
    """The function is used to send sms through the africastalking api and also attempts to send the previously unsent messages"""

    # The json file path and sender name
    file_path = 'apis/messages.json'
    sender = "OLMISMISFCS"

    # Create a message object
    f_message = {"message": message, "phone_numbers": phone_numbers}

    # Read unsent messages
    data = read_unsent_messages(file_path)

    # Append the new message to the list of unsent messages
    data.append(f_message)
    print(data)

    try:
        response = sms.send(message, phone_numbers, sender)
        if response['SMSMessageData']['Recipients'][0]['status'] == 'Success':
            data.remove(f_message)
        elif response['SMSMessageData']['Recipients'][0]['status'] == 'InsufficientBalance':
            write_unsent_messages(file_path, data)
            return "Insufficient balance"

        for msg in data:
            a = msg['message']
            b = msg['phone_numbers']
            try:
                response = sms.send(a, b, sender)

                if response['SMSMessageData']['Recipients'][0]['status'] == 'Success':
                    data.remove(msg)
                else:  
                    print(f'The unsent message was not deleted: {a}')

            except Exception as e:
                pass
                
    except Exception as e:
        pass

    # Write the unsent messages back to the file
    write_unsent_messages(file_path, data)
	