# garak red-team job (D23, D40)

This job runs [garak](https://github.com/NVIDIA/garak) (≥ 0.17) weekly against LiteLLM, and against each agent before promotion. Reports are kept as ISO 27001 and SOC 2 evidence.

- **Weekly:** the `default-chat` model, through LiteLLM, using `garak-config.yaml`.
- **Pre-promotion:** the agent's model plus its system prompt, run in non-prod.
- **Failure threshold:** any probe family above the agreed hit rate blocks promotion.
