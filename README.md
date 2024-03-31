# atypical
Custom types for things like phone numbers, emails, etc. with normalization, Pydantic handling and JSON Schema serialization

## Examples

```python
from atypical.email import Email
from atypical.money import Money
from atypical.phone import PhoneNumber
from atypical.url import NormalizedURL
from sartorial.schema import Schema


class MyModel(Schema):
    email: Email
    phone_number: PhoneNumber
    amount: Money
    website: NormalizedURL

import json
print(MyModel.model_json_schema())  # or MyModel.to_schema_dict()

# Output
'''
{
    "additionalProperties": true,
    "properties": {
        "email": {
            "format": "email",
            "type": "string"
        },
        "phone_number": {
            "format": "phone",
            "type": "string"
        },
        "amount": {
            "format": "money",
            "type": "string"
        },
        "website": {
            "format": "normalized-url",
            "type": "string"
        }
    },
    "required": [
        "email",
        "phone_number",
        "amount",
        "website"
    ],
    "title": "MyModel",
    "type": "object"
}
 '''

m = MyModel(email="foo.bar+baz@gmail",
            phone_number="1 (212) 555-6789",
            amount="$100",
            website="example.com")

print(m.model_dump_json(indent=4))  # or m.to_json()

# Output
'''
{
    "email": "foobar@gmail.com",
    "phone_number": "+12125556789",
    "amount": "$100.00",
    "website": "https://example.com/"
}
'''
```
