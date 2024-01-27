import typing as tp


class Celsius:
    def __init__(self, attribute_name: str) -> None:
        self.attribute_name = attribute_name

    def __get__(self, instance: tp.Any, owner: tp.Any) -> int:
        if instance is None:
            raise AttributeError("None instance")

        kelvin_instance = getattr(instance, self.attribute_name)

        if hasattr(instance, self.attribute_name):
            if not self.check_kalvin(instance):
                raise AttributeError(f"{self.attribute_name} does not reference a Kelvin instance")
            return kelvin_instance - 273

        raise AttributeError(f"{self.attribute_name} not found in instance")

    def __set__(self, instance: tp.Any, value: tp.Any) -> None:
        raise AttributeError("Cannot set attribute")

    def __delete__(self, instance: tp.Any) -> None:
        raise ValueError("Cannot delete attribute")

    def check_kalvin(self, instance: tp.Any) -> bool:
        return isinstance(instance.__class__.__dict__[self.attribute_name], Kelvin)


class Kelvin:
    def __init__(self, attribute_name: str) -> None:
        self.attribute_name = attribute_name
        self.is_kelvin = True

    def __get__(self, instance: tp.Any, owner: tp.Any) -> int:
        if instance is None:
            raise AttributeError("None instance")
        if hasattr(instance, self.attribute_name):
            return getattr(instance, self.attribute_name)
        raise AttributeError(f"{self.attribute_name} not found in instance")

    def __set__(self, instance: tp.Any, value: tp.Any) -> None:
        if not hasattr(instance, self.attribute_name):
            raise AttributeError(f"{self.attribute_name} not found in instance")
        if value <= 0:
            raise ValueError("Temperature must be greater than 0")
        setattr(instance, self.attribute_name, value)

    def __delete__(self, instance: tp.Any) -> None:
        raise ValueError("Cannot delete attribute")
