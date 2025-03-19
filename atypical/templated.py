import re
from typing import Any, ClassVar, Dict, ForwardRef, List, Union

from communal.nulls import Omitted
from jinja2 import Environment, StrictUndefined
from jinja2 import Template as JinjaTemplate
from jinja2 import meta as jinja2_meta
from sartorial import JSONSchemaFormatted, Serializable
from sartorial.types import JSON_SCHEMA_DEFAULT_TYPES

JSON_TYPE_DEFAULT_SCHEMAS = {v: k for k, v in JSON_SCHEMA_DEFAULT_TYPES.items()}

Templated = ForwardRef("Templated")


class Templated(str, JSONSchemaFormatted, Serializable):
    __schema_format__ = "jinja2"

    env: ClassVar[Environment] = Environment(undefined=StrictUndefined)
    jinja_check_pattern: ClassVar[re.Pattern] = re.compile(r"\{\{.*?\}\}|\{\%.*?\%\}")

    template: str
    compiled: JinjaTemplate
    variables: List[str]
    params: Dict[str, Any]

    def __new__(cls, template: str, **kwargs):
        return str.__new__(cls, template)

    def __init__(self, template: Union[str, Templated], **kwargs):
        if isinstance(template, Templated):
            self.params = template.params
            self.template = template.template
            self.compiled = template.compiled
            self.variables = template.variables
            self.params = template.params or {}
            self.params.update(kwargs)
        elif not isinstance(template, str):
            raise ValueError("Template must be a string")
        else:
            self.template = template
            nodes = self.env.parse(template)
            self.variables = list(jinja2_meta.find_undeclared_variables(nodes))
            self.compiled = self.env.template_class.from_code(
                environment=self.env,
                code=self.env.compile(nodes),
                globals=self.env.make_globals(None),
                uptodate=None,
            )
            self.params = kwargs

    def render(self, **kwargs):
        if self.params is not Omitted:
            kwargs = dict(self.params, **kwargs)
        value = self.compiled.render(**kwargs)
        return value

    @classmethod
    def is_jinja(cls, value: str):
        parsed = cls.env.parse(value)
        return bool(jinja2_meta.find_undeclared_variables(parsed))

    def __repr__(self) -> str:
        return self.template

    def __str__(self) -> str:
        return self.template
