# {{ title }}

**Authors**: {{ authors | join(", ") }}

**Affiliations**: {{ affiliations | join("; ") }}

**Corresponding Author**: {{ corresponding_author }}

**Email**: {{ corresponding_email }}

---

## Abstract

{{ abstract }}

**Keywords**: {{ keywords | join(", ") }}

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

## Data and Materials Availability

{{ data_availability }}

---

## References

{% for ref in references %}
{{ loop.index }}. {{ ref.citation }}
{% endfor %}

---

*Manuscript prepared for submission to Science*
