<div align="center">

<img src="cards/hero.svg" width="100%" alt="Terminal: Toufik Saouchi, software engineer. About me, then the status of each project." />

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

## The homelab

**[homelab-infra](https://github.com/s-toufik/homelab-infra)** runs the whole platform on one k3s node, deploying every release with helmfile and the charts from **[kube-charts](https://github.com/s-toufik/kube-charts)**. The map below is read from that helmfile every day. The numbered pods light up in turn to follow one question, from sign-in to the model, and then its trace lands in Tempo.

<div align="center">
  <a href="https://github.com/s-toufik/homelab-infra"><img src="cards/cluster.svg" width="100%" alt="Every Helm release on the homelab-infra k3s node, grouped by namespace, with the path of one question through the cluster" /></a>
</div>

## Nexus, my knowledge hub

**[nexus](https://github.com/s-toufik/nexus)** is where I write down everything I build, why it's built that way, and the ideas behind it, so it can be learned from. It's an Obsidian vault: one note per idea, linked rather than repeated, with decisions that keep their reasons. The graph below is drawn from the vault every day: one dot per note, linked the way the notes link each other.

<div align="center">
  <a href="https://github.com/s-toufik/nexus"><img src="cards/nexus.svg" width="100%" alt="Nexus: the folders of my knowledge hub with their note counts, and a graph of every note and its links" /></a>
</div>

## Repositories

**Agents**
- [agent-runtime](https://github.com/s-toufik/agent-runtime): planning, execution, reflection and decision-making workflows that produce reliable answers
- [agent-toolbox](https://github.com/s-toufik/agent-toolbox): the MCP tool server the agent calls

**Homelab**
- [homelab-ui](https://github.com/s-toufik/homelab-ui): the front door, with every tool as a page and the agent beside it
- [homelab-infra](https://github.com/s-toufik/homelab-infra): the whole platform on one k3s node, deployed with helmfile
- [kube-charts](https://github.com/s-toufik/kube-charts): the Helm charts the homelab runs on

**Knowledge**
- [nexus](https://github.com/s-toufik/nexus): my knowledge hub, an Obsidian vault of projects, ideas, learning paths and sources

**Libraries and templates**
- [pycraftcore](https://github.com/s-toufik/pycraftcore): reusable infrastructure and adapters for Python applications
- [archetype](https://github.com/s-toufik/archetype): a pragmatic hexagonal architecture template for Python, Rust and C++

**pricelab**
- [pricelab-core](https://github.com/s-toufik/pricelab-core): core library of the pricing platform
- [pricelab-retriever](https://github.com/s-toufik/pricelab-retriever): retrieves data from various sources
- [pricelabcpp-core](https://github.com/s-toufik/pricelabcpp-core): the pricelab core in C++
- [pricelabr-core](https://github.com/s-toufik/pricelabr-core): the shared core of the pricelab microservices in Rust (experimental)

**Experiments**
- [web_framework_benchmark](https://github.com/s-toufik/web_framework_benchmark): every web framework under the same load, compared
- [blender](https://github.com/s-toufik/blender): Blender experiments

**Retired**
- [Orion](https://github.com/s-toufik/Orion): a Python API for post-processing large-scale data, now decommissioned

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
