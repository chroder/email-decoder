from flanker.addresslib import address


class Addr:
    """
    Represents an email address.
    """
    def __init__(self, email=None, name=None):
        self.name = name
        """
        The name portion of the email
        :type str | None
        """

        self.email = email
        """
        The email address
        :type str
        """

    @property
    def is_valid(self):
        return validate_email_address(self.email)


def validate_email_address(email_address):
    """
    Validate an email address.

    :param string email_address: The email address to validate
    :return bool
    """
    parsed = address.parse(email_address, addr_spec_only=True)
    if isinstance(parsed, address.EmailAddress):
        return True
    return False
