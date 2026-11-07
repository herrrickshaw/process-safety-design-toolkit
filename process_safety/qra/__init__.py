"""Quantitative risk assessment (QRA) workflow built on the toolkit's consequence models.

Steps: hazid (1) -> frequency + eta (2) -> effects (3) -> risk (4) -> alarp (5) -> mitigation (6); study.run() chains them.
CLI: python -m process_safety qra {example,validate,run,hazid}. See docs/QRA.md.
"""
