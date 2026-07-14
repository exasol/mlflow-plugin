class VirtualSchemaError(Exception):
    """
    Parent class for errors related to Virtual Schemas.
    """


class PushdownError(VirtualSchemaError):
    """
    Pushdown request specifies unsupported details, e.g. type or
    selectList.
    """


class PropertiesError(VirtualSchemaError):
    """
    CreateVirtualSchema or SetProperties request specifies unsupported
    Adapter Properties.
    """
