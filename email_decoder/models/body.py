class Body:
    TYPE_TEXT = "text"
    TYPE_HTML = "html"

    def __init__(self):
        self.content = ""
        """
        The content of the message.
        :type str
        """

        self.type = "text"
        """
        The type of the body
        :type str
        """