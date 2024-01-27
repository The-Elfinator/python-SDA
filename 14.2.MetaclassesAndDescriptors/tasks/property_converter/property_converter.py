import typing as tp


class PropertyConverterMeta(type):
    def __new__(cls, clsname, bases, attrs) -> 'PropertyConverterMeta':  # type: ignore
        klazz: PropertyConverterMeta = super(PropertyConverterMeta, cls).__new__(cls, clsname, bases, attrs)
        if bases:
            for k, v in bases[0].__dict__.items():
                if k[:4] == "get_" or k[:4] == "set_":
                    name = k[4:]
                    has_get = f"get_{name}" in bases[0].__dict__
                    has_set = f"set_{name}" in bases[0].__dict__
                    for attr_key, attr_val in attrs.items():
                        if attr_key == name and isinstance(attr_val, property):
                            has_get = False
                            has_set = False
                    if has_get and has_set:
                        setattr(klazz, name, property(
                            fget=lambda self, method_get=f"get_{name}": getattr(self, method_get)(),  # type: ignore
                            fset=lambda self, val, m=f"set_{name}": getattr(self, m)(val)  # type: ignore
                        ))
                    elif has_get:
                        setattr(klazz, name, property(
                            fget=lambda self, method_get=f"get_{name}": getattr(self, method_get)()  # type: ignore
                        ))
                    elif has_set:
                        setattr(klazz, name, property(
                            fset=lambda self, val, m=f"set_{name}": getattr(self, m)(val)  # type: ignore
                        ))
        return klazz


class PropertyConverter(metaclass=PropertyConverterMeta):
    def __getattr__(self, attr: str) -> None:
        return object.__getattribute__(self, attr)

    def __setattr__(self, attr: str, value: tp.Any) -> None:
        object.__setattr__(self, attr, value)
