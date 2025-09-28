from api.services.payments_service import create_cash_payment, create_payment_and_intent

def process_payment(payment_mode, donation, amount):
    """
    Processes payment based on the mode (Card or Cash).
    """
    if payment_mode == "Card":
        return create_payment_and_intent(donation, amount)
    elif payment_mode == "Cash":
        return create_cash_payment(donation, amount)
    else:
        raise ValueError("Unsupported payment mode. Supported modes are: Card, Cash.")