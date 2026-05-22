# {{ title }}

**Authors**: {{ authors | join(", ") }}

**Affiliations**: {{ affiliations | join("; ") }}

**Corresponding Author**: {{ corresponding_author }}

**Email**: {{ corresponding_email }}

---

## Abstract

### Background
{{ abstract_background }}

### Methods
{{ abstract_methods }}

### Results
{{ abstract_results }}

### Conclusions
{{ abstract_conclusions }}

---

## Introduction

{{ introduction }}

---

## Materials and Methods

{{ methods }}

---

## Results

{{ results }}

---

## Discussion

{{ discussion }}

---

## Acknowledgments

{{ acknowledgments }}

---

## Author Contributions

{{ author_contributions }}

---

## Data Availability

{{ data_availability }}

---

## References

{% for ref in references %}
{{ loop.index }}. {{ ref.citation }}
{% endfor %}

---

*Manuscript prepared for submission to PLOS ONE*
