# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'uplogic'
copyright = '2024, Leopold Auersperg-Castell'
author = 'Leopold Auersperg-Castell'
release = '2.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx_rtd_theme'
]

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_logo = '_static/upbge_logo.png'
html_title = 'UPLOGIC Manual'
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_theme_options = {
   "navigation_with_keys": True,
   # included in the title
   "display_version": False,
   "collapse_navigation": True, # slows build down; useful
   "navigation_depth": 3,
}
