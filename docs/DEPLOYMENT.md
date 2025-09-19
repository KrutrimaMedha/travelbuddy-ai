# Cloud Run Deployment Guide

This repo contains both a backend (FastAPI) and a frontend (Vite + Nginx). You can deploy them to Cloud Run via:
- GitHub Actions (recommended; keyless via Workload Identity Federation)
- Local script (`deploy-script.sh`)
- Google Cloud Build trigger (`cloudbuild.yaml`)

## One‑Time GCP Setup

1) Enable required APIs

```bash
gcloud services enable \
  run.googleapis.com \
  artifactregistry.googleapis.com \
  iam.googleapis.com \
  iamcredentials.googleapis.com
```

2) Create an Artifact Registry repo (Docker)

```bash
# Pick your location and repo name (examples below)
AR_LOCATION=us-central1
AR_REPOSITORY=travelbuddy

gcloud artifacts repositories create "$AR_REPOSITORY" \
  --repository-format=docker \
  --location="$AR_LOCATION" \
  --description="Docker repo for TravelBuddy"
```

3) Create a deployer Service Account

```bash
PROJECT_ID=primal-carport-462506-a0
SA=gh-deployer

gcloud iam service-accounts create "$SA" \
  --display-name="GitHub Deployer"

# Minimum roles for CI deploys
gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SA@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding "$PROJECT_ID" \
  --member="serviceAccount:$SA@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/artifactregistry.writer"
```

4) Set up Workload Identity Federation (keyless GitHub OIDC)

```bash
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)')

# Create a pool and provider for GitHub
gcloud iam workload-identity-pools create github-pool \
  --location=global \
  --display-name="GitHub Actions Pool"

gcloud iam workload-identity-pools providers create-oidc github \
  --location=global \
  --workload-identity-pool=github-pool \
  --display-name="GitHub OIDC" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="google.subject=assertion.sub,attribute.actor=assertion.actor,attribute.repository=assertion.repository,attribute.ref=assertion.ref" \
  --attribute-condition="assertion.repository=='KrutrimaMedha/travelbuddy-ai' && assertion.ref=='refs/heads/main'"

# Permit the GitHub principal to impersonate the SA
gcloud iam service-accounts add-iam-policy-binding \
  "$SA@$PROJECT_ID.iam.gserviceaccount.com" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/attribute.repository/KrutrimaMedha/travelbuddy-ai"
```

Provider resource value to use in GitHub secrets:

```
projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/providers/github
```

## GitHub Actions (CI/CD)

Workflows:
- `.github/workflows/deploy-backend.yml` — builds/pushes backend image to Artifact Registry, deploys to Cloud Run.
- `.github/workflows/deploy-frontend.yml` — fetches backend URL, writes `travel_planner_ui/.env.production`, builds/pushes frontend image, deploys.

Required repository secrets (Settings → Secrets and variables → Actions):
- `GCP_PROJECT_ID` = `primal-carport-462506-a0`
- `GCP_REGION` = `us-central1`
- `GCP_AR_LOCATION` = `us-central1`
- `GCP_AR_REPOSITORY` = `travelbuddy`
- `GCP_WIF_PROVIDER` = `projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/github-pool/providers/github`
- `GCP_SERVICE_ACCOUNT` = `gh-deployer@primal-carport-462506-a0.iam.gserviceaccount.com`

Images are pushed to:

```
${GCP_AR_LOCATION}-docker.pkg.dev/${GCP_PROJECT_ID}/${GCP_AR_REPOSITORY}/${SERVICE_NAME}:${GITHUB_SHA}
```

Notes:
- Workflows assume the Artifact Registry repo already exists (least privilege). They do not attempt to create it.
- The frontend build uses Vite and reads `VITE_API_URL` from `travel_planner_ui/.env.production`, which the workflow writes from the deployed backend URL.

## Local Script Deploy

To deploy from your machine using gcloud and Cloud Build:

```bash
./deploy-script.sh <your-gcp-project-id>
```

This builds and deploys backend first, then frontend, using the correct Docker contexts/Dockerfiles.

## Cloud Build Trigger (optional)

`cloudbuild.yaml` builds/pushes/deploys both services in sequence and injects the backend URL for the frontend. Point a Cloud Build trigger at this file for repo‑driven deploys.

## Troubleshooting

- PERMISSION_DENIED artifactregistry.repositories.create
  - Precreate the repo (above) or grant broader `roles/artifactregistry.repoAdmin` temporarily.
- Workload Identity “principal://…subject/repo:” appears in errors
  - The GitHub identity reached GCP, but impersonation wasn’t allowed. Verify the `roles/iam.workloadIdentityUser` binding and the provider attribute condition matches `KrutrimaMedha/travelbuddy-ai` and your branch.
- Frontend can’t reach backend
  - Confirm the frontend `.env.production` was written and that Cloud Run ingress allows unauthenticated access for the backend.

