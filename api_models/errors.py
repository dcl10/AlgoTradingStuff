class AccountError(Exception):
    """
    Raised when the API can't locate any accounts for the user
    """
    pass


class OrderError(Exception):
    """
    Raised when there is a problem with orders
    """
    pass
