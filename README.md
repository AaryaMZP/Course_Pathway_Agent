# SkillPilot — Personalized Course Pathways

An agentic AI course-pathway coach powered by **IBM Granite** (watsonx.ai) with a **React** frontend, **Node/Express** backend, and **IBM Cloudant** persistence. Deployed as a native agent on **watsonx Orchestrate**.

Problem Statement No.12 - Agentic AI for Personalized Course Pathways. 
The Challenge - Students often struggle to identify the right learning path that aligns with their interests 
and long-term goals due to the overwhelming number of online courses and a lack of personalized 
guidance. LearnMate aims to solve this by acting as an Agentic AI coach that interacts with students, 
understands their interests (like Frontend Development, Cybersecurity, UI/UX Design, etc.), assesses their 
current skill level, and dynamically builds a personalized course roadmap that adapts over time based on 
progress and preferences. 
Technology – Use of IBM Cloud Lite services / IBM Granite is mandatory.

# SkillPilot

**Agentic AI coach for personalized course pathways.**

SkillPilot helps students cut through the overwhelming number of online courses by acting as an AI coach — it identifies their career goal (or suggests one based on interests), assesses their skill level, and builds an adaptive, personalized learning roadmap.

## Features
- **Goal Discovery Agent** – identifies a career goal or surfaces one from stated interests
- **Skill Assessment Agent** – evaluates current skill level
- **Roadmap Generation Agent** – builds a sequenced plan of skills, tools, and languages
- **Progress Tracking Agent** – adapts the roadmap based on progress and pace
- Visual dashboard with roadmap timeline and per-module progress

## Tech Stack
- IBM Granite Models (`ibm-granite-3-2-8b`)
- IBM watsonx.ai
- IBM Cloud
- Frontend: React + Tailwind
- Backend: Node.js/Express

## Getting Started
```bash
git clone https://github.com/<your-username>/skillpilot.git
cd skillpilot
pip install -r requirements.txt
```

## Team
Built for Problem Statement 12 — Agentic AI for Personalized Course Pathways.
