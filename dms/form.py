import json
from collections import defaultdict
from datetime import date, datetime

from dms import state


class Form:
    def __init__(self, name: str, data: dict):
        self.name = name
        self.schema = state.items.schema(name=self.name)
        self.data = dict(data)
        self.result = {}
        self.errors = defaultdict(list)
        self.is_validated = False

    @property
    def is_valid(self) -> bool:
        if not self.is_validated:
            self.validate()
        return self.errors == {}

    def validate(self) -> "Form":
        data = self.data
        for fn, field in self.schema.fields.items():
            value = data.get(fn)
            type_ = field.type

            # strip strings and convert empty values to None
            if isinstance(value, str):
                value = value.strip() or None

            # convert checkboxes to boolean
            if type_ == "boolean":
                value = bool(int((value if value != "on" else 1) or 0))
                data[fn] = value

            # convert json string to dict
            if type_ in ["json", "jsonb"]:
                value = json.loads(value) if value else {}

            # convert None array value to empty list
            if type_ == "array":
                value = value or []

            # convert date string to date object
            if type_ == "date" and isinstance(value, str):
                value = date.fromisoformat(value)

            # convert datetime string to datetime object
            if type_ in ["datetime", "timestamp"] and isinstance(value, str):
                value = datetime.fromisoformat(value)

            # convert integers
            if type_ in ["integer", "bigint", "smallint"]:
                try:
                    value = int(value) if value is not None else None
                except ValueError:
                    self.errors[fn].append("Invalid value type")

            # convert floats
            if type_ in ["float", "double_precision"]:
                try:
                    value = float(value) if value is not None else None
                except ValueError:
                    self.errors[fn].append("Invalid value type")

            # handle required fields
            if value is None and field.is_required and not field.default:
                self.errors[fn].append("This field is required")

            # handle max length values
            if value and field.max_length and field.max_length < len(value):
                self.errors[fn].append(f"Value is too long")

            self.result[fn] = {**field.to_dict(), **{"value": value}}
            data[fn] = value

        self.errors = dict(self.errors)
        self.is_validated = True
        return self

    def __repr__(self) -> str:
        return self.__str__()

    def __str__(self) -> str:
        return f"<{self.__class__.__name__} name={self.name}>"
