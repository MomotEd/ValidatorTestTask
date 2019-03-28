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
        pass


class BaseFieldValidator(AbstractFieldValidator):

    data_types = {
        "string": str,
        "integer": int,
        # etc
    }

    def __init__(self, field_name: str, config: dict):
        self.field_name = field_name
        self.required = config.get("required")
        self.type_key = config.get("type")
        self.validation_methods = [self.validate_required, self.validate_type]

    def validate(self, value):
        if not self.required and not value:
            return

        for method in self.validation_methods:
            method(value)

    def validate_type(self, value):
        data_type = self.data_types.get(self.type_key)
        if not data_type:
            raise HTTPError(status_code=501, log_message=f"Unsupported data type. Please contact developers!")
        if not isinstance(value, data_type):
            raise HTTPError(status_code=400, log_message=f"{value} is not valid value for {self.field_name}")

    def validate_required(self, value):
        if not value and self.required:
            raise HTTPError(status_code=400, log_message=f"Required fields can not be blank! {self.field_name} required")


class StringValidator(BaseFieldValidator):

    def __init__(self, field_name, config):
        self.max_len = config.get("max", 0)
        self.min_len = config.get("min", 0)
        super().__init__(field_name, config)
        self.validation_methods.extend([self.validate_max_length, self.validate_min_length])

    def validate_min_length(self, value):
        if len(value) < self.min_len:
            raise HTTPError(status_code=400, log_message=f"{value} is shorter then {self.min_len}")

    def validate_max_length(self, value):
        if len(value) > self.max_len:
            raise HTTPError(status_code=400, log_message=f"{value} is longer then {self.max_len}")


class IntegerValidator(BaseFieldValidator):

    def __init__(self, field_name, config):
        self.max_value = config.get("max", 0)
        self.min_value = config.get("min", 0)
        super().__init__(field_name, config)
        self.validation_methods.extend([self.validate_min_value, self.validate_max_value])

    def validate_min_value(self, value):
        if len(value) < self.min_value:
            raise HTTPError(status_code=400, log_message=f"{value} is smaller then {self.min_value}")

    def validate_max_value(self, value):
        if len(value) > self.max_value:
            raise HTTPError(status_code=400, log_message=f"{value} is greater then {self.max_value}")


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
        pass


class FieldValidatorCreator(AbstractValidatorCreator):

    def __init__(self):
        self.field_validators = {
            "string": StringValidator,
            "integer": IntegerValidator,
        }

    def get_field_validator(self, field_name, config):
        field_type = config.get("type")
        field_validator = self.field_validators.get(field_type)
        if field_validator:
            return field_validator(field_name, config)
        raise ValueError(f"Unsupported field type {field_type}. Check config.")
