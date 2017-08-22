class Message:
    """
    Represents an email message parsed into useful values.
    """
    def __init__(self):
        self.subject = ""
        """
        Subject of the email
        :type str
        """

        self.message_id = ""
        """
        The message ID
        :type str
        """

        self.from_addr = None
        """
        From address of the email. Note that technically there can be multiple froms. If your
        code anticipates that, you can read the value from headers instead.
        :type str | None
        """

        self.to_addrs = None
        """
        To addresses the email was sent to.
        :type list[addr] | None
        """

        self.cc_addrs = None
        """
        CC addresses the email was sent to.
        :type list[addr] | None
        """

        self.bcc_addrs = None
        """
        BCC'd addresses the email was sent to. Note that incoming email won't have any record of these (hence being blind).
        :type list[addr] | None
        """

        self.reply_to_addr = None
        """
        Reply-to address the email has specified.
        :type str | None
        """

        self.date = None
        """
        The date the email was read. Note that this is not necessarily the date the email was actually sent.
        :type datetime.datetime
        """

        self.message_date = None
        """
        The date on the email itself (may be spoofed).
        :type datetime.datetime
        """

        self.references = []
        """
        List of message-ids this message references
        :type list[string]
        """

        self.body_text = None
        """
        Text body, if available.
        :type str | None
        """

        self.body_html = None
        """
        HTML body, if available.
        :type str | None
        """

        self.files = []
        """
        File attachments in the email.
        :type list[file]
        """

        self.headers = None
        """
        Headers on the message 
        """

        self.raw_headers = None
        """
        Headers on the message with their raw string values. Note this differs
        from message.headers in that these are raw string values, whereas headers will be
        parsed into useful values where it makes sense (e.g. email addresses will be Addr lists). 
        """