class File:
    def __init__(self):
        self.content_id = None
        """
        The content ID on the file. May be used in a message to reference a resource (e.g. inline images).
        :type str | None
        """

        self.filename = None
        """
        The filename if specified.
        :type str | None
        """

        self.size = 0
        """
        The size of the file in bytes
        :type int
        """

        self.content_type = "application/octet-stream"
        """
        The type of the file (https://en.wikipedia.org/wiki/Internet_media_type)
        :type str
        """

        self.data = None
        """
        The actual file contents, or more commonly, a reference to where to find the file.
        :type str
        """

        self.is_inline = False
        """
        True if the file has inline disposition
        :type bool
        """