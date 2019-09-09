from dms import state
from dms.ds import Field, Meta
from dms.orm import FNS


class Schema:
    def __init__(self, name: str, meta: Meta):
        self.name: str = name
        self.meta = meta
        self.pk = list(state.items.table(name=self.name).primary_key.columns)[0]
        self._fields = None

    @property
    def fields(self):
        if self._fields is None:
            self._fields = {}
            table = state.items.table(name=self.name)

            for i, c in enumerate(table.columns):
                type_ = c.type.__class__.__name__.lower()
                default = c.default or FNS.get(self.meta.defaults.get(c.name))
                onupdate = c.onupdate or FNS.get(self.meta.updates.get(c.name))
                ld = self.meta.list_display
                pos = ld.index(c.name) if c.name in ld else len(ld) + i

                self._fields[c.name] = Field(
                    name=c.name,
                    pos=pos,
                    label=c._label,
                    type=type_,
                    index=c.index,
                    unique=c.unique,
                    default=default,
                    onupdate=onupdate,
                    choices=getattr(c.type, "choices", None),
                    max_length=getattr(c.type, "length", None),
                    is_nullable=c.nullable,
                    is_primary_key=c.primary_key,
                    is_required=not c.nullable and default is None,
                    is_clean=not hasattr(self.meta, f"_{c.name}"),
                    is_excluded=c.name in self.meta.exclude,
                    is_list_display=bool(set(ld) & {c.name, f"_{c.name}"}),
                    is_readonly=c.name in self.meta.readonly_fields,
                )

        return self._fields

    @property
    def field_names(self):
        return tuple(f.name for f in sorted(self.fields.values(), key=lambda o: o.pos))

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name}>"
