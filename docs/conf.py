project = "Frame Studio"
author = "Frame Studio contributors"
copyright = "2026, Frame Studio contributors"
release = "0.1.0"

extensions = [
    "myst_parser",
    "sphinx.ext.autosectionlabel",
    "sphinx.ext.extlinks",
]
autosectionlabel_prefix_document = True
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
html_theme = "furo"
html_title = "Frame Studio documentation"
html_static_path = ["_static"]
html_css_files = ["custom.css"]
html_theme_options = {
    "light_css_variables": {
        "color-brand-primary": "#c96f00",
        "color-brand-content": "#b66100",
    },
    "dark_css_variables": {
        "color-brand-primary": "#ffb11b",
        "color-brand-content": "#ffbd45",
    },
}
