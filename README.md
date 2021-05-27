# Composition based validators

This is a minimal implementation of infinitely nested validators.

```python
class Foo:
    name = List(Int() | List(List(Int(min_value=1)), min_size=5)) | Int(max_value=10)

    def __init__(self, name):
        self.name = name


foo = Foo([[[1, 1, 1, 1], [1, 2, 2, 2], [1, 3], [4], [5]]])
```
