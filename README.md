# AirWatch — Air Quality & Weather Intelligence Dashboard

AirWatch is a full-stack environmental data application that combines air-quality and weather data into a searchable dashboard for exploring local environmental conditions.

The project demonstrates an end-to-end software and data engineering workflow: external API ingestion, backend service design, relational storage, frontend visualization, and Docker-based local development.

## Why I Built This

Air-quality and weather data are often available through separate APIs, which makes it harder to understand local environmental conditions in one place. AirWatch brings these signals together so users can search by location and view environmental context through a single application.

## Features

- Search and view air-quality and weather information by location
- Backend API for health checks, readiness checks, and data access
- PostgreSQL-backed data model for storing environmental records
- Redis-ready infrastructure for caching and background-job workflows
- React + TypeScript frontend for dashboard-style exploration
- Docker Compose setup for local PostgreSQL and Redis services
- Environment-based configuration for API keys, database URLs, and CORS

## Tech Stack

**Frontend:** React, TypeScript, Vite  
**Backend:** Python, FastAPI, Pydantic Settings, SQLAlchemy  
**Database:** PostgreSQL  
**Infrastructure:** Docker, Docker Compose, Redis  
**Data Sources:** OpenAQ, Open-Meteo  
**Tools:** Alembic, Uvicorn, Git, Postman

## Architecture

    User
      ↓
    React + TypeScript Frontend
      ↓
    FastAPI Backend
      ↓
    Service Layer / API Clients
      ↓
    PostgreSQL + Redis
      ↓
    OpenAQ + Open-Meteo APIs

## Repository Structure

    airwatch/
    ├── backend/              # FastAPI application
    ├── web/                  # React + TypeScript frontend
    ├── docker-compose.yml    # Local PostgreSQL and Redis services
    ├── .env.example          # Example environment variables
    └── README.md

## Backend Setup

    cd backend
    python -m venv .venv
    .venv\Scripts\activate   # Windows
    pip install -r requirements.txt
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Useful backend checks:

    GET /healthz
    GET /readyz

## Frontend Setup

    cd web
    npm install
    npm run dev

Create a frontend environment file if needed:

    VITE_API_URL=http://localhost:8000

## Docker Setup

    docker compose up -d

Expected local services:

    PostgreSQL: localhost:5432
    Redis: localhost:6379
    Backend: localhost:8000
    Frontend: localhost:5173

## Environment Variables

Create a `.env` file based on `.env.example`.

    API_HOST=0.0.0.0
    API_PORT=8000

    POSTGRES_HOST=localhost
    POSTGRES_PORT=5432
    POSTGRES_DB=airwatch
    POSTGRES_USER=airwatch
    POSTGRES_PASSWORD=your_password
    DATABASE_URL=postgresql+psycopg://airwatch:your_password@localhost:5432/airwatch

    REDIS_URL=redis://localhost:6379/0

    CORS_ORIGINS=http://localhost:5173

    OPENAQ_API_BASE=https://api.openaq.org
    OPENAQ_API_KEY=your_openaq_key
    OPENMETEO_BASE=https://api.open-meteo.com

## What I Focused On

- Designing a clean full-stack project structure
- Connecting external environmental APIs to a backend service layer
- Managing local development with Dockerized PostgreSQL and Redis
- Building backend health and readiness checks for deployability
- Creating a frontend foundation for a production-style dashboard
- Practicing environment-based configuration across frontend and backend services

## Highlights

- Built a full-stack application using React, TypeScript, FastAPI, PostgreSQL, Redis, and Docker
- Integrated third-party environmental APIs into a backend service layer
- Used health and readiness endpoints to support deployment-style backend validation
- Structured the app with separate frontend, backend, database, and infrastructure concerns
- Designed the project around a real-world data product use case: air quality and weather intelligence

## Future Improvements

- Add scheduled ingestion jobs for historical air-quality records
- Add charts for pollutant trends and weather overlays
- Add geospatial filtering and map-based exploration
- Deploy frontend and backend with production environment variables
- Add automated tests for API routes, services, and frontend components
- Add screenshots and a short demo GIF to the README

## Status

Active portfolio project. Built as a full-stack environmental data platform to demonstrate backend engineering, data ingestion, database design, Docker-based development, and frontend dashboard development.
