class BankError(Exception):
    pass 

class InsufficientFundsError(BankError):
    """Raised when group does not have enough balance to buy a question."""
    pass

class InsufficientQuestionsError(BankError):
    """Raised when bank does not have enough questions of a specific level."""
    pass

class QuestionDoesNotExist(BankError):
    """Raised when the question doesn't to the group or doesn't exist."""
    pass

class ItemDoesNotExist(BankError):
    """Raised when the item was sold or does not exist."""
    pass

class GroupDoesNotExist(BankError):
    """Raised when the group to make changes to does not exist."""
    pass

class NoLeaderFound(BankError):
    """Raised when the group does not have any leader."""

class FormDoesNotExist(BankError):
    """Raised when the trade form does not exist."""
    pass
    
class InvalidOTP(BankError):
    """Raised when the entered otp is not equal to the saved one."""
    pass

class NotExpiredOTP(BankError):
    """Raised when the otp code has expired."""
    pass