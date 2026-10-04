<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:070b16,55:1d4ed8,100:38bdf8&height=190&section=header&text=s-toufik&fontColor=ffffff&fontSize=56&fontAlignY=36&desc=Building%20a%20homelab%20platform%2C%20one%20clean%20module%20at%20a%20time&descSize=17&descAlignY=58" width="100%" alt="s-toufik" />

<img src="https://readme-typing-svg.demolab.com?font=Fira+Code&weight=500&size=20&duration=2800&pause=900&color=60A5FA&center=true&vCenter=true&width=640&lines=AI+agents+that+plan%2C+act+and+check+their+work;Hexagonal+architecture+in+Python+%26+TypeScript;Self-hosted+LLMs%2C+observability+and+data+on+one+server;Clean+code+over+quick+patches" alt="What I build" />

<p>
  <img src="https://img.shields.io/badge/Paris-France-1d4ed8?style=flat-square&logo=googlemaps&logoColor=white" alt="Paris, France" />
  <img src="https://komarev.com/ghpvc/?username=s-toufik&style=flat-square&color=1d4ed8&label=profile+views" alt="Profile views" />
  <a href="https://github.com/s-toufik?tab=repositories"><img src="https://img.shields.io/badge/repositories-explore-0ea5e9?style=flat-square&logo=github&logoColor=white" alt="Repositories" /></a>
</p>

</div>

## 👋 About me

I build software the way I'd like to maintain it: **clear layers, small swappable parts, and tests that guard the architecture**. My playground is a homelab that grows into a real platform — an AI agent with its own tools, local language models, full observability and data services, all on a single machine.

- 🧠 Designing **AI agents**: planning, tool use over MCP, self-review, routing driven by explicit rules
- 🏗️ Practising **hexagonal architecture** across Python, TypeScript, Rust and C++
- 📈 Running my own **observability stack**: metrics, logs and traces end to end
- 🌱 Always adding the next piece — the repositories below keep growing

## 🛰️ The homelab platform

```text
              ┌──────────────┐  HTTP / SSE  ┌────────────────────┐   MCP   ┌───────────────┐
  you ──────► │  homelab-ui  │ ───────────► │ agent-orchestrator │ ──────► │ agent-toolbox │
              └──────┬───────┘              └─────┬────────┬─────┘         └───────┬───────┘
                     │                            ▼        ▼                       ▼
                     │                           LLMs   MongoDB          SQL · files · Python
                     ▼
        Grafana · Prometheus · Kafka · …  ◄── telemetry from every service

  everything above runs from homelab-infra · shared foundations come from pycraftcore
```

## 🚀 Featured projects

<table>
  <tr>
    <td width="50%">
      <a href="https://github.com/s-toufik/agent-orchestrator"><img src="https://github-readme-stats.vercel.app/api/pin/?username=s-toufik&repo=agent-orchestrator&theme=github_dark&hide_border=true&bg_color=0d1117&title_color=60a5fa&icon_color=60a5fa" alt="agent-orchestrator" /></a>
    </td>
    <td width="50%">
      <a href="https://github.com/s-toufik/agent-toolbox"><img src="https://github-readme-stats.vercel.app/api/pin/?username=s-toufik&repo=agent-toolbox&theme=github_dark&hide_border=true&bg_color=0d1117&title_color=60a5fa&icon_color=60a5fa" alt="agent-toolbox" /></a>
    </td>
  </tr>
  <tr>
    <td width="50%">
      <a href="https://github.com/s-toufik/homelab-ui"><img src="https://github-readme-stats.vercel.app/api/pin/?username=s-toufik&repo=homelab-ui&theme=github_dark&hide_border=true&bg_color=0d1117&title_color=60a5fa&icon_color=60a5fa" alt="homelab-ui" /></a>
    </td>
    <td width="50%">
      <a href="https://github.com/s-toufik/homelab-infra"><img src="https://github-readme-stats.vercel.app/api/pin/?username=s-toufik&repo=homelab-infra&theme=github_dark&hide_border=true&bg_color=0d1117&title_color=60a5fa&icon_color=60a5fa" alt="homelab-infra" /></a>
    </td>
  </tr>
  <tr>
    <td width="50%">
      <a href="https://github.com/s-toufik/pycraftcore"><img src="https://github-readme-stats.vercel.app/api/pin/?username=s-toufik&repo=pycraftcore&theme=github_dark&hide_border=true&bg_color=0d1117&title_color=60a5fa&icon_color=60a5fa" alt="pycraftcore" /></a>
    </td>
    <td width="50%">
      <a href="https://github.com/s-toufik/archetype"><img src="https://github-readme-stats.vercel.app/api/pin/?username=s-toufik&repo=archetype&theme=github_dark&hide_border=true&bg_color=0d1117&title_color=60a5fa&icon_color=60a5fa" alt="archetype" /></a>
    </td>
  </tr>
</table>

Also building the **pricelab** platform: [pricelab-core](https://github.com/s-toufik/pricelab-core) · [pricelab-retriever](https://github.com/s-toufik/pricelab-retriever)

## 🧰 Tech stack

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
<img src="https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white" alt="PostgreSQL" />
<img src="https://img.shields.io/badge/MongoDB-47A248?style=for-the-badge&logo=mongodb&logoColor=white" alt="MongoDB" />
<img src="https://img.shields.io/badge/Kafka-231F20?style=for-the-badge&logo=apachekafka&logoColor=white" alt="Kafka" />
<img src="https://img.shields.io/badge/Grafana-F46800?style=for-the-badge&logo=grafana&logoColor=white" alt="Grafana" />
<img src="https://img.shields.io/badge/Prometheus-E6522C?style=for-the-badge&logo=prometheus&logoColor=white" alt="Prometheus" />
<img src="https://img.shields.io/badge/OpenTelemetry-425CC7?style=for-the-badge&logo=opentelemetry&logoColor=white" alt="OpenTelemetry" />
<img src="https://img.shields.io/badge/Tailscale-242424?style=for-the-badge&logo=tailscale&logoColor=white" alt="Tailscale" />

## 📊 GitHub stats

<div align="center">
  <img height="170" src="https://github-readme-stats.vercel.app/api?username=s-toufik&show_icons=true&include_all_commits=true&count_private=true&theme=github_dark&hide_border=true&bg_color=0d1117&title_color=60a5fa&icon_color=60a5fa&rank_icon=github" alt="GitHub stats" />
  <img height="170" src="https://github-readme-stats.vercel.app/api/top-langs/?username=s-toufik&layout=compact&langs_count=8&theme=github_dark&hide_border=true&bg_color=0d1117&title_color=60a5fa" alt="Top languages" />
  <br />
  <img src="https://streak-stats.demolab.com?user=s-toufik&theme=github-dark-blue&hide_border=true&background=0D1117&ring=60A5FA&fire=38BDF8&currStreakLabel=60A5FA" alt="Contribution streak" />
</div>

## 🏆 Achievements

<div align="center">
  <img src="metrics.achievements.svg" alt="Achievements earned on GitHub" />
</div>

## 📅 A year of contributions

<div align="center">
  <img src="metrics.isocalendar.svg" alt="Contribution calendar" />
  <br /><br />
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/s-toufik/s-toufik/output/github-snake-dark.svg" />
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/s-toufik/s-toufik/output/github-snake.svg" />
    <img src="https://raw.githubusercontent.com/s-toufik/s-toufik/output/github-snake-dark.svg" alt="A snake eating the contribution graph" />
  </picture>
</div>

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:38bdf8,45:1d4ed8,100:070b16&height=110&section=footer" width="100%" alt="" />
