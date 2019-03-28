from abc import ABC, abstractmethod
import json
from validators.field_validators import FieldValidatorCreator
from tornado.web import HTTPError


class AbstractViewValidator(ABC):

    @abstractmethod
    def validate(self, request):
        """
        Main validation method. Implement your logic here.
        """
        raise NotImplementedError()

    @abstractmethod
    def check_extra(self, request):
        """
        Provides possibility to check if extra data in request.
        """
        raise NotImplementedError()


class Validator(AbstractViewValidator):

    def __init__(self, fields_conf, allow_extra):
        self.fields_conf = fields_conf
        self.allow_extra = allow_extra
        self.fields = {}
        factory = FieldValidatorCreator()
        for field, config in self.fields_conf.items():
            self.fields[field] = factory.get_field_validator(field, config)

    def validate(self, request):
        request = self.get_json(request)
        if self.check_extra(request) or self.allow_extra:
            for field, f_validator in self.fields.items():
                value = request.get(field)
                f_validator.validate(value)
        else:
            raise HTTPError(status_code=400, log_message="Extra fields are not allowed")

    def check_extra(self, request):
        return all(name in self.fields_conf for name in request)

    @staticmethod
    def get_json(request_body):
        try:
            return json.loads(request_body)
        except TypeError:
            raise HTTPError(status_code=400, log_message="request is not JSON")
