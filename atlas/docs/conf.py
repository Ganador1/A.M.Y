"""
Configuration file for Sphinx documentation builder.

This file configures Sphinx to generate comprehensive documentation
for the AXIOM ATLAS project, including API documentation, guides,
and examples.
"""

import os
import sys
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.abspath('..'))

# Project information
project = 'AXIOM ATLAS'
copyright = f'2024-{datetime.now().year}, AXIOM ATLAS Team'
author = 'AXIOM ATLAS Team'

# Version information
release = '2.0.0'
version = '2.0'

# General configuration
extensions = [
    'sphinx.ext.autodoc',        # Core Sphinx library for auto html docs
    'sphinx.ext.autosummary',    # Create neat summary tables
    'sphinx.ext.viewcode',       # Add source code links
    'sphinx.ext.napoleon',       # Support for NumPy and Google style docstrings
    'sphinx.ext.intersphinx',    # Link to other projects' documentation
    'sphinx.ext.coverage',       # Check documentation coverage
    'sphinx.ext.doctest',        # Test code snippets in documentation
    'sphinx.ext.githubpages',    # Publish HTML to GitHub Pages
    'sphinx_rtd_theme',          # Read the Docs theme
]

# Autodoc configuration
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
    'member-order': 'bysource',
    'special-members': '__init__, __call__',
}

autodoc_typehints = 'description'
autodoc_type_aliases = {
    'Dict': 'dict',
    'List': 'list',
    'Optional': 'optional',
    'Union': 'union',
    'Tuple': 'tuple',
}

# Autosummary configuration
autosummary_generate = True
autosummary_imported_members = True

# Napoleon configuration (for Google/NumPy style docstrings)
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = False
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_type_aliases = {
    'Dict': 'dict',
    'List': 'list',
    'Optional': 'optional',
    'Union': 'union',
    'Tuple': 'tuple',
}

# Intersphinx configuration
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'sqlalchemy': ('https://docs.sqlalchemy.org/en/20/', None),
    'fastapi': ('https://fastapi.tiangolo.com/', None),
    'pydantic': ('https://docs.pydantic.dev/latest/', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
}

# HTML output configuration
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_css_files = ['custom.css']
html_js_files = ['custom.js']

# Theme options
html_theme_options = {
    'analytics_id': 'G-XXXXXXXXXX',  # Replace with actual Google Analytics ID
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'vcs_pageview_mode': '',
    'style_nav_header_background': '#2980B9',
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}

# Logo and favicon
html_logo = '_static/logo.png'
html_favicon = '_static/favicon.ico'

# Additional static files
html_extra_path = []

# LaTeX configuration (for PDF generation)
latex_elements = {
    'papersize': 'letterpaper',
    'pointsize': '10pt',
    'preamble': '',
    'figure_align': 'htbp',
}

# LaTeX documents
latex_documents = [
    (master_doc, 'AXIOMATLAS.tex', 'AXIOM ATLAS Documentation',
     'AXIOM ATLAS Team', 'manual'),
]

# Manual page output
man_pages = [
    (master_doc, 'axiom-atlas', 'AXIOM ATLAS Documentation',
     [author], 1)
]

# Texinfo file
texinfo_documents = [
    (master_doc, 'AXIOMATLAS', 'AXIOM ATLAS Documentation',
     author, 'AXIOMATLAS', 'AI-driven scientific research platform.',
     'Miscellaneous'),
]

# Coverage configuration
coverage_skip_undoc_in_source = True
coverage_ignore_pyobjects = [
    'test_*',
    '*_test',
    'conftest',
    'setup',
]

# Doctest configuration
doctest_global_setup = '''
import sys
import os
sys.path.insert(0, os.path.abspath('.'))
'''

# GitHub pages configuration
html_baseurl = 'https://your-org.github.io/axiom-atlas/'

# Custom configuration for AXIOM ATLAS
html_context = {
    'github_user': 'your-org',
    'github_repo': 'axiom-atlas',
    'github_version': 'main',
    'doc_path': 'docs/',
    'source_suffix': '.rst',
}

# Path setup
master_doc = 'index'
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '**.tmp']
templates_path = ['_templates']
source_suffix = {
    '.rst': None,
    '.md': None,
}

# Additional configuration for better API documentation
autodoc_inherit_docstrings = True
autodoc_member_order = 'bysource'
autoclass_content = 'both'

# Extensions configuration
viewcode_import = True
viewcode_follow_imported = True

# RTD theme specific configuration
html_theme_path = []
html_style = None
html_theme_options.update({
    'canonical_url': 'https://axiom-atlas.readthedocs.io/',
    'analytics_anonymize_ip': False,
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': True,
    'vcs_pageview_mode': 'blob',
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False,
    'show_sphinx': False,
    'github_url': 'https://github.com/your-org/axiom-atlas',
})

# Custom CSS and JS files
def setup(app):
    app.add_css_file('custom.css')
    app.add_js_file('custom.js')

    # Add custom directives
    app.add_directive('automodule', app.env.get_and_resolve_doctree)

    # Connect to autodoc-skip-member event
    app.connect('autodoc-skip-member', skip_member)
