# {{ title }}

**Authors**: {{ authors | join(", ") }}

**Affiliations**: {{ affiliations | join("; ") }}

**Corresponding Author**: {{ corresponding_author }}

**Email**: {{ corresponding_email }}

---

## Summary

{{ abstract }}

**Keywords**: {{ keywords | join(", ") }}

---

## Introduction

{{ introduction }}

---

## Results

{{ results }}

---

## Discussion

{{ discussion }}

---

## STAR Methods

{{ methods }}

---

## Acknowledgments

{{ acknowledgments }}

---

## Author Contributions

{{ author_contributions }}

---

## Data and Code Availability

{{ data_availability }}

---

## References

{% for ref in references %}
{{ loop.index }}. {{ ref.citation }}
{% endfor %}

---

*Manuscript prepared for submission to Cell*
