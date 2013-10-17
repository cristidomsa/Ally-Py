{% extends '_request.rst' -%}
{% block description -%}
{% set flags = request['flags'] -%}
{% if 'isCollection' in flags -%}
  {% if 'isModel' in flags %}
 * The request will GET a collection of models ``{{ request['target'] }}``
  {%- else -%}
    {% if 'isModelRef' in flags %}
 * The request will GET a collection of references to models ``{{ request['target'] }}``
    {%- else %}
 * The request will GET a collection of ``{{ request['property'] }}`` properties of models ``{{ request['target'] }}``
    {%- endif -%}
  {%- endif -%}
{%- else %}
  {% if 'isModel' in flags %}
 * The request will GET a model ``{{ request['target'] }}``
  {%- else -%}
    {% if 'isModelRef' in flags %}
 * The request will GET a reference to model ``{{ request['target'] }}``
    {%- else %}
 * The request will GET a ``{{ request['property'] }}`` property o model ``{{ request['target'] }}``
    {%- endif -%}
  {%- endif -%}
{% endif -%}
{%- endblock -%}