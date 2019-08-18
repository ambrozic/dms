import typing
from dataclasses import asdict, dataclass


@dataclass
class DS:
    def to_dict(self):
        return asdict(self)


@dataclass
class Config(DS):
    settings: typing.Dict[str, typing.Any]
    models: typing.Dict[str, "Meta"]

    def __init__(self, settings: dict = None, models: dict = None):
        self.settings = settings or {}
        self.models = {
            k: Meta(**{"name": k, "table": k, **v}) for k, v in (models or {}).items()
        }


@dataclass
class Meta(DS):
    # model display name
    name: str

    # table name
    table: str = None

    # model icon
    icon: str = "circle"

    # fields show in list view
    list_display: typing.Tuple = None

    # show list of filter on right side menu #todo implement
    list_filter: typing.Tuple = None

    # fields used in model search
    search_fields: typing.Tuple = None

    # readonly but shown as disabled in form view
    readonly_fields: typing.Tuple = None

    # excluded from showing in form view
    exclude: typing.Tuple = None

    # order in list view
    ordering: typing.Tuple = None

    # generated field value on create
    defaults: typing.Dict = None

    # generated field value on update
    updates: typing.Dict = None

    def __post_init__(self):
        for fn, th in typing.get_type_hints(self.__class__).items():
            v = getattr(self, fn)
            if v is None:
                continue
            setattr(self, fn, th(v) if type(th) == type else th.__origin__(v))

        self.list_display = self.list_display or ()
        self.list_filter = self.list_filter or ()
        self.search_fields = self.search_fields or ()
        self.readonly_fields = self.readonly_fields or ()
        self.ordering = self.ordering or ()
        self.exclude = self.exclude or ()
        self.defaults = self.defaults or {}
        self.updates = self.updates or {}


@dataclass
class Field(DS):
    name: str
    pos: int
    label: str
    type: str
    index: int
    unique: bool
    default: bool
    onupdate: str
    choices: typing.Tuple
    max_length: int
    is_nullable: bool
    is_primary_key: bool
    is_required: bool
    is_clean: bool
    is_excluded: bool
    is_list_display: bool
    is_readonly: bool
