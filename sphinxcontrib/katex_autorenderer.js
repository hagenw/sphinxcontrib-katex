latex_options = { macros: {
  "\\i": "\\mathrm{i}",
  "\\e": "\\mathrm{e}^{#1}",
  "\\w": "\\omega",
  "\\wc": "\\frac{\\omega}{c}",
  "\\vec": "\\mathbf{#1}",
  "\\x": "\\vec{x}",
  "\\xs": "\\x_\\text{s}",
  "\\xref": "\\x_\\text{ref}",
  "\\k": "\\vec{k}",
  "\\n": "\\vec{n}",
  "\\d": "\\operatorname{d}\\!{}",
  "\\dirac": "\\operatorname{\\delta}\\left(#1\\right)",
  "\\scalarprod":   "\\left\\langle#1,#2\\right\\rangle",
  "\\Hankel": "\\mathop{{}H_{#2}^{(#1)}}\\!\\left(#3\\right)",
  "\\hankel": "\\mathop{{}h_{#2}^{(#1)}}\\!\\left(#3\\right)"
}}
renderMathInElement(document.body, latex_options);
