<div align="center">

<a href="https://github.com/s-toufik?tab=repositories"><img src="cards/hero.svg" width="100%" alt="Terminal: Toufik Saouchi, software engineer. I build AI agents and the single-server platform they run on. Status of each project." /></a>

<sub>
<a href="https://github.com/s-toufik/agent-runtime">agent-runtime</a> ·
<a href="https://github.com/s-toufik/agent-toolbox">agent-toolbox</a> ·
<a href="https://github.com/s-toufik/homelab-ui">homelab-ui</a> ·
<a href="https://github.com/s-toufik/homelab-infra">homelab-infra</a> ·
<a href="https://github.com/s-toufik/kube-charts">kube-charts</a> ·
<a href="https://github.com/s-toufik/pycraftcore">pycraftcore</a> ·
<a href="https://github.com/s-toufik/archetype">archetype</a> ·
<a href="https://github.com/s-toufik/pricelab-core">pricelab-core</a>
</sub>

</div>

I build software the way I'd like to maintain it: **clear layers, small swappable parts, and tests that guard the architecture**. My playground is a homelab that grows into a real platform: an AI agent with its own MCP tools, local language models, databases, Kafka and full observability, all on one k3s node behind a single sign-in.

## The lab, from the front door to the pods

**[homelab-ui](https://github.com/s-toufik/homelab-ui)** is the front door: every tool rebuilt as a page, a Status page, and the agent beside every page.

<div align="center">
  <img src="assets/homelab-ui.svg" width="100%" alt="Sketch of homelab-ui: sidebar with every tool as a page, the Status page by namespace, and the agent panel" />
</div>

Behind it, **[homelab-infra](https://github.com/s-toufik/homelab-infra)** deploys every release with helmfile and the charts from **[kube-charts](https://github.com/s-toufik/kube-charts)**. The map below is read from that helmfile every day. The numbered pods light up in turn to follow one question, from sign-in to the model, and then its trace lands in Tempo.

<div align="center">
  <img src="cards/cluster.svg" width="100%" alt="Every Helm release on the k3s node, grouped by namespace, with the path of one question through the cluster" />
</div>

## Activity

<div align="center">
  <img src="cards/streak.svg" width="49%" alt="Contributions in the last 12 months and current streak" />
  <img src="cards/languages.svg" width="49%" alt="Most used languages across my repositories" />
  <br /><br />
  <img src="cards/achievements.svg" width="100%" alt="Achievements earned on GitHub" />
  <br /><br />
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/s-toufik/s-toufik/output/github-snake-dark.svg" />
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/s-toufik/s-toufik/output/github-snake.svg" />
    <img src="https://raw.githubusercontent.com/s-toufik/s-toufik/output/github-snake-dark.svg" alt="A snake eating the contribution graph" />
  </picture>
</div>

Also building the **pricelab** platform: [pricelab-core](https://github.com/s-toufik/pricelab-core) · [pricelab-retriever](https://github.com/s-toufik/pricelab-retriever)

## Stack

**Languages**
<br />
<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
<img src="https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white" alt="TypeScript" />
<img src="https://img.shields.io/badge/Rust-000000?style=for-the-badge&logo=rust&logoColor=white" alt="Rust" />
<img src="https://img.shields.io/badge/C%2B%2B-00599C?style=for-the-badge&logo=cplusplus&logoColor=white" alt="C++" />
<img src="https://img.shields.io/badge/Shell-121011?style=for-the-badge&logo=gnubash&logoColor=white" alt="Shell" />

**AI & backend**
<br />
<img src="https://img.shields.io/badge/LangGraph-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white" alt="LangGraph" />
<img src="https://img.shields.io/badge/LangChain-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white" alt="LangChain" />
<img src="https://img.shields.io/badge/MCP-0F172A?style=for-the-badge&logo=modelcontextprotocol&logoColor=white" alt="Model Context Protocol" />
<img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" />
<img src="https://img.shields.io/badge/Pydantic-E92063?style=for-the-badge&logo=pydantic&logoColor=white" alt="Pydantic" />
<img src="https://img.shields.io/badge/llama.cpp-1D4ED8?style=for-the-badge" alt="llama.cpp" />

**Frontend**
<br />
<img src="https://img.shields.io/badge/Angular-DD0031?style=for-the-badge&logo=angular&logoColor=white" alt="Angular" />
<img src="https://img.shields.io/badge/Vitest-6E9F18?style=for-the-badge&logo=vitest&logoColor=white" alt="Vitest" />

**Data & infrastructure**
<br />
<img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker" />
<img src="https://img.shields.io/badge/Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white" alt="Kubernetes" />
<img src="https://img.shields.io/badge/Helm-0F1689?style=for-the-badge&logo=helm&logoColor=white" alt="Helm" />
<img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
<img src="https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white" alt="MongoDB" />
<img src="https://img.shields.io/badge/Kafka-231F20?style=for-the-badge&logo=apachekafka&logoColor=white" alt="Kafka" />
<img src="https://img.shields.io/badge/Grafana-F46800?style=for-the-badge&logo=grafana&logoColor=white" alt="Grafana" />
<img src="https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=prometheus&logoColor=white" alt="Prometheus" />
<img src="https://img.shields.io/badge/OpenTelemetry-425CC7?style=for-the-badge&logo=opentelemetry&logoColor=white" alt="OpenTelemetry" />
<img src="https://img.shields.io/badge/Tailscale-242424?style=for-the-badge&logo=tailscale&logoColor=white" alt="Tailscale" />
<img src="https://img.shields.io/badge/k3s-FFC61C?style=for-the-badge&logo=k3s&logoColor=black" alt="k3s" />
<img src="https://img.shields.io/badge/Caddy-1F88C0?style=for-the-badge&logo=caddy&logoColor=white" alt="Caddy" />
<img src="https://img.shields.io/badge/Keycloak-4D4D4D?style=for-the-badge&logo=keycloak&logoColor=white" alt="Keycloak" />
