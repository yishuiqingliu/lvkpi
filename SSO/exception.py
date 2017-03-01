# coding=utf-8

class ValidationError(Exception):
    """Base exception class for ticket validation failures."""

class InvalidRequest(ValidationError):
    """Not all of the required request parameters were present."""
    code = 'INVALID_REQUEST'


class InvalidTicket(ValidationError):
    """
    The ticket provided was not valid, or the ticket did not come
    from an initial login and renew was set on validation.
    """
    code = 'INVALID_TICKET'


class InternalError(ValidationError):
    """An internal error occurred during ticket validation."""
    code = 'INTERNAL_ERROR'


class BadPgt(ValidationError):
    """The PGT provided was invalid."""
    code = 'BAD_PGT'