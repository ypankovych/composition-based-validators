class ValidationError(ValueError):
    pass


class Union:

    def __init__(self, *args):
        self.validators = list(args)

    def __set_name__(self, owner, name):
        self.field_name = name

    def __set__(self, instance, value):
        self.validate(instance, value, self.field_name)
        vars(instance)[self.field_name] = value

    def validate(self, instance, value, field_name):
        pass


class UnionAnd(Union):

    def __and__(self, other):
        self.validators.append(other)
        return self

    def __or__(self, other):
        return UnionOr(self, other)

    def validate(self, instance, value, field_name):
        error = False
        for validator in self.validators:
            try:
                valid = validator.validate(instance, value, field_name)
            except ValidationError:
                error = True
            except Exception:
                if not error:
                    raise
                break
            else:
                if not valid:
                    error = True
        if error:
            raise ValidationError
        return True


class UnionOr(Union):

    def __or__(self, other):
        self.validators.append(other)
        return self

    def __and__(self, other):
        return UnionAnd(self, other)

    def validate(self, instance, value, field_name):
        error = False
        for validator in self.validators:
            try:
                valid = validator.validate(instance, value, field_name)
                if valid:
                    return True
            except ValidationError:
                error = True
            except Exception:
                if not error:
                    raise
                break
        raise ValidationError


class BaseValidator:

    def __set_name__(self, owner, name):
        self.field_name = name

    def __and__(self, other):
        return UnionAnd(self, other)

    def __or__(self, other):
        return UnionOr(self, other)

    def __set__(self, instance, value):
        valid = self.validate(instance, value, self.field_name)
        if not valid:
            raise ValidationError
        vars(instance)[self.field_name] = value

    def __get__(self, instance, owner):
        if not instance:
            return self
        value = vars(instance)[self.field_name]
        mutated = self.mutate(instance, value)
        if mutated is not NotImplemented:
            value = mutated
        return value

    def validate(self, instance, value, field_name):
        pass

    def mutate(self, instance, value):
        return NotImplemented


class ContainerValidator(BaseValidator):

    def __init__(self, predicate):
        self.predicate = predicate

    def validate(self, instance, value, field_name):
        valid = True
        if not self.predicate:
            return valid

        for item in value:
            valid = self.predicate.validate(instance, item, field_name)
            if not valid:
                raise ValidationError
        return valid


class List(ContainerValidator):

    def __init__(self, predicate=None, min_size=None, max_size=None):
        super(List, self).__init__(predicate)
        self.max_size = max_size
        self.min_size = min_size

    def validate(self, instance, value, field_name):
        valid = isinstance(value, list)
        if self.min_size:
            valid = valid and len(value) >= self.min_size
        if self.max_size:
            valid = valid and len(value) <= self.max_size
        if not valid:
            return False
        return super(List, self).validate(instance, value, field_name)


class Int(BaseValidator):
    error_message = "`{field_name}` should be an int"

    def __init__(self, min_value=None, max_value=None):
        self.min_value = min_value
        self.max_value = max_value

    def validate(self, instance, value, field_name):
        valid = isinstance(value, int)
        if self.min_value:
            valid = valid and value >= self.min_value
        if self.max_value:
            valid = value <= self.max_value
        return valid
