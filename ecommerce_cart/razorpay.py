"""
Razorpay API Implementation
"""
import razorpay

RAZORPAY_KEY = "rzp_test_jvh5Se3lUnOjjE"  # TEST KEY
RAZORPAY_CLIENT = razorpay.Client(auth=(RAZORPAY_KEY, "AUYJio0bqCs9PbVwfkyrOKeH"))  # "<YOUR_API_KEY>", "<YOUR_API_SECRET>"
RAZORPAY_CLIENT.set_app_details({"title": "django", "version": "2.0.6"})


def new_razorpay_order(order_amount, order_receipt, note_dict):
    """
    Creates a new Razorpay Order and returns the dict return by razorpay
    """
    data = {
        "amount": order_amount,  # in paise
        "currency": "INR",
        "receipt": order_receipt,  # Maximum length 40 chars
        "notes": note_dict,  # OPTIONAL (add up to 15 key-value pairs with each value of the key not exceeding 256 characters)
        "payment_capture": '1'
    }

    razorpay_order_info = RAZORPAY_CLIENT.order.create(data=data)

    return razorpay_order_info


def fetch_razorpay_order_info(razorpay_order_id):
    """
    Fetch order details form razorpay
    """
    razorpay_order_info = RAZORPAY_CLIENT.order.fetch(razorpay_order_id)

    return razorpay_order_info


def verify_razorpay_signature(razorpay_order_id, razorpay_payment_id, razorpay_signature):
    """
    Verify razorpay payment success by signature verification; raise SignatureVerificationError error if fails
    """
    params_dict = {
        'razorpay_order_id': razorpay_order_id,
        'razorpay_payment_id': razorpay_payment_id,
        'razorpay_signature': razorpay_signature
    }

    RAZORPAY_CLIENT.utility.verify_payment_signature(params_dict)


def fetch_razorpay_payment_by_order(razorpay_order_id):
    """
    Fetch payment details form razorpay
    """
    fetch_data = RAZORPAY_CLIENT.order.payments(razorpay_order_id)

    return fetch_data


def capture_razorpay_payment(razorpay_payment_id, razorpay_order_amount):
    """
    Capture payment details form razorpay
    """
    captured_data = RAZORPAY_CLIENT.payment.capture(razorpay_payment_id, razorpay_order_amount)

    return captured_data
