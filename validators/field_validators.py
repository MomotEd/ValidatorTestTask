from tornado.web import HTTPError
from abc import ABC, abstractmethod


class AbstractFieldValidator(ABC):
    """
    The AbstractFieldValidator class declares base methods to validate
    file.
    """

    @abstractmethod
    def validate(self, value):
        """
        Main validation method. Implement your logic here.
        """
        raise NotImplementedError()


class BaseFieldValidator(AbstractFieldValidator):

    data_types = {
        "string": str,
        "integer": int,
        # etc
    }

    def __init__(self, field_name: str, config: dict):
        self._field_name = field_name
        self._required = config.get("required")
        self._type_key = config.get("type")
        additional_methods = [getattr(self, method) for method in dir(self) if
                              method.startswith("validate_") and callable(getattr(self, method))]
        self.validation_methods = [self.base_validate_type, self.base_validate_required, *additional_methods]

    def validate(self, value):
        if not self._required and not value:
            return

        for method in self.validation_methods:
            method(value)

    def base_validate_type(self, value):
        data_type = self.data_types.get(self._type_key)
        if not data_type:
            raise HTTPError(status_code=501, log_message=f"Unsupported data type. Please contact developers!")
        if not isinstance(value, data_type):
            raise HTTPError(status_code=400, log_message=f"{value} is not valid value for {self._field_name}")

    def base_validate_required(self, value):
        if not value and self._required:
            raise HTTPError(status_code=400, log_message=f"Required fields can not be blank! {self._field_name} required")


class StringValidator(BaseFieldValidator):

    def __init__(self, field_name, config):
        self._max_len = config.get("max", 0)
        self._min_len = config.get("min", 0)
        super().__init__(field_name, config)

    def validate_min_length(self, value):
        if len(value) < self._min_len:
            raise HTTPError(status_code=400, log_message=f"{value} is shorter then {self._min_len}")

    def validate_max_length(self, value):
        if len(value) > self._max_len:
            raise HTTPError(status_code=400, log_message=f"{value} is longer then {self._max_len}")


class IntegerValidator(BaseFieldValidator):

    def __init__(self, field_name, config):
        self._max_value = config.get("max", 0)
        self._min_value = config.get("min", 0)
        super().__init__(field_name, config)

    def validate_min_value(self, value):
        if value < self._min_value:
            raise HTTPError(status_code=400, log_message=f"{value} is smaller then {self._min_value}")

    def validate_max_value(self, value):
        if value > self._max_value:
            raise HTTPError(status_code=400, log_message=f"{value} is greater then {self._max_value}")


class AbstractValidatorCreator(ABC):
    """
    The AbstractValidatorCreator class declares the factory method that should rotate the object
    Class FieldValidator.
    """

    @abstractmethod
    def get_field_validator(self, field_name, config):
        """
        AbstractValidatorCreator also provide implementation
        factory default method.
        """
        raise NotImplementedError()


class FieldValidatorCreator(AbstractValidatorCreator):

    def __init__(self):
        self._field_validators = {
            "string": StringValidator,
            "integer": IntegerValidator,
        }

    def get_field_validator(self, field_name, config):
        field_type = config.get("type")
        field_validator = self._field_validators.get(field_type)
        if field_validator:
            return field_validator(field_name, config)
        raise ValueError(f"Unsupported field type {field_type}. Check config.")
