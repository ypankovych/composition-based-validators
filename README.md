# Composition based validators

This is a minimal implementation of infinitely nested validators.

```python
class Sum(BaseValidator):

    def __init__(self, value):
        self.sum = value

    def validate(self, instance, value, field_name):
        return sum(value) == self.sum


class Foo:
    name = List(Int() | List(List(Int(min_value=0)) & Sum(10), min_size=5)) | Int(max_value=10)

    def __init__(self, name):
        self.name = name


foo = Foo(
    [
        [
            [1, 1, 1, 1, 6],
            [0, 0, 0, 0, 10],
            [1, 2, 3, 1, 1, 2],
            [5, 1, 1, 1, 1, 1],
            [2, 3, 4, 1, 0]
        ]
    ]
)

```
