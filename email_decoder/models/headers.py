class Headers:
    """
    Collection of headers
    """

    # Well-known headers and their proper names (case matters)
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
        'User-Agent',
        'MIME-Version'
    ]

    NORMAL_TO_KNOWN = dict((h.lower(), h) for h in KNOWN_HEADERS)

    ADDR_HEADERS = [
        'BCC', 'CC', 'Delivered-To', 'From', 'Original-Recipient', 'Reply-To', 'Return-Path', 'Sender', 'To'
    ]

    DATE_HEADERS = [
        'Date', 'Delivery-Date'
    ]

    # Common headers that are usually considered to only have a single value
    SINGLE_HEADERS = [
        'Message-ID', 'In-Reply-To', 'Accept-Language', 'Content-Language', 'MIME-Version', 'Thread-Topic',
        'Thread-Index', 'Subject'
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
                if header.proper_name in Headers.SINGLE_HEADERS:
                    header.is_single = True
                self.add_header(header)
        else:
            header = Header(name, value)
            header.is_single = is_single
            if header.proper_name in Headers.SINGLE_HEADERS:
                header.is_single = True
            self.add_header(header)

    """
    Get ALL header objects for a particular header.
    :param str name: The name of the header you want
    :return list[Header]
    """
    def get_headers(self, name):
        name = name.lower()
        return self.headers[name] if name in self.headers else None

    """
    Get a SINGLE (the first) header object for a particular header.
    :param str name: The name of the header to get
    :return Header
    """
    def get_header(self, name):
        name = name.lower()
        return self.headers[name][0] if name in self.headers else None

    """
    Get ALL values for a particular header.
    :param str name: The name of the header you want
    :return list[str]
    """
    def get_header_values(self, name):
        name = name.lower()
        return [h.value for h in self.headers[name]] if name in self.headers else None

    """
    Get a SINGLE (the first) value for a particular header.
    :param str name: The name of the header to get
    :return str
    """
    def get_header_value(self, name):
        name = name.lower()
        return self.headers[name][0].value if name in self.headers else None

    """
    Check if a header exists in the collection
    :param str name: The name of the header
    :return bool
    """
    def has_header(self, name):
        name = name.lower()
        return True if name in self.headers else False

    @staticmethod
    def get_proper_name(name):
        lower_name = name.lower()
        if lower_name in Headers.NORMAL_TO_KNOWN:
            return Headers.NORMAL_TO_KNOWN[lower_name]
        else:
            return lower_name


class Header(object):
    def __init__(self, name=None, value=None):
        self._raw_name = ""
        """
        The raw header name provided.
        :type str
        """

        self._proper_name = ""
        """
        The "proper" name of the header, including correct case. If this is not a "well known" header
        then this will be the same as the normalised header.
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
        return self._raw_name

    @property
    def name(self):
        return self._normal_name

    @property
    def proper_name(self):
        return self._proper_name;

    @name.setter
    def name(self, name):
        self._raw_name = name
        self._proper_name = Headers.get_proper_name(name)
        self._normal_name = name.lower()
