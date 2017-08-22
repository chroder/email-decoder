class Headers:
    """
    Collection of headers
    """

    KNOWN_HEADERS = [
        'Autoforwarded',
        'BCC',
        'CC',
        'Content-Disposition',
        'Content-ID',
        'Content-Language',
        'Content-Length',
        'Content-Transfer-Encoding',
        'Content-Type',
        'Date',
        'Delivered-To',
        'Delivery-Date',
        'Distribution',
        'Encoding',
        'Envelope-ID',
        'From',
        'Importance',
        'In-Reply-To',
        'Language',
        'List-ID',
        'Mailer',
        'Mailing-List',
        'Message-ID',
        'Original-Recipient',
        'Path',
        'Priority',
        'Received',
        'References',
        'Reply-To',
        'Return-Path',
        'Sender',
        'Subject',
        'To',
        'User-Agent'
    ]

    NORMAL_TO_KNOWN = dict((h.lower(), h) for h in KNOWN_HEADERS)

    ADDR_HEADERS = [
        'BCC', 'CC', 'Delivered-To', 'From', 'Original-Recipient', 'Reply-To', 'Return-Path', 'Sender', 'To'
    ]

    DATE_HEADERS = [
        'Date', 'Delivery-Date'
    ]

    """
    Collection of headers
    """
    def __init__(self):
        self.headers = {}
        """
        Headers and their values.
        :type dict[str, list[Header]]
        """

    """
    Adds a header to the collection
    :param Header header: The header to add
    """
    def add_header(self, header):
        if header.name not in self.headers:
            self.headers[header.name] = []

        self.headers[header.name].append(header)

    """
    Create a new Header and then add it to the collection
    :param str name: The name of the header
    :param str value: The value of the header
    :param bool is_multiple: The value is a list of values, so we'll add multiple header values
    :param bool is_single: If the header should be marked as is_single
    """
    def add_header_value(self, name, value, is_multiple=False, is_single=False):
        if is_multiple:
            for v in value:
                header = Header(name, v)
                header.is_single = is_single
                self.add_header(header)
        else:
            header = Header(name, value)
            header.is_single = is_single
            self.add_header(header)

    """
    Get ALL header objects for a particular header.
    :param str name: The name of the header you want
    :return list[Header]
    """
    def get_headers(self, name):
        name = Headers.get_normalized_name(name)
        return self.headers[name] if name in self.headers else None

    """
    Get a SINGLE (the first) header object for a particular header.
    :param str name: The name of the header to get
    :return Header
    """
    def get_header(self, name):
        name = Headers.get_normalized_name(name)
        return self.headers[name].value if name in self.headers else None

    """
    Get ALL values for a particular header.
    :param str name: The name of the header you want
    :return list[str]
    """
    def get_header_values(self, name):
        name = Headers.get_normalized_name(name)
        return [h.value for h in self.headers[name]] if name in self.headers else None

    """
    Get a SINGLE (the first) value for a particular header.
    :param str name: The name of the header to get
    :return str
    """
    def get_header_value(self, name):
        name = Headers.get_normalized_name(name)
        return self.headers[name][0].value if name in self.headers else None

    """
    Check if a header exists in the collection
    :param str name: The name of the header
    :return bool
    """
    def has_header(self, name):
        name = Headers.get_normalized_name(name)
        return True if name in self.headers else False

    @staticmethod
    def get_normalized_name(name):
        name = name.lower()
        if name in Headers.NORMAL_TO_KNOWN:
            return Headers.NORMAL_TO_KNOWN[name]
        else:
            return name


class Header:
    def __init__(self, name=None, value=None):
        self._name = ""
        """
        The raw header name provided.
        :type str
        """

        self._normal_name = ""
        """
        The normalised version of the header. This will be a lowercased version
        of the input unless its a common/known header, in which case we'll use the
        spec version.
        :type str
        """

        self.value = ""
        """
        Value of the header.
        """

        self.is_single = False
        """
        Is this header a single value? These headers are expected to always have only one
        value. This changes how the header behaves when it is encoded for output.
        """

        if name:
            self.name = name
        if value:
            self.value = value

    """
    Gets the raw header value provided instead of the normalised one.
    """
    @property
    def raw_name(self):
        return self._name

    @property
    def name(self):
        return self._normal_name

    @name.setter
    def name(self, name):
        self._name = name
        self._normal_name = Headers.get_normalized_name(name)
