# Serverless OIDC Authentication App

A fully serverless web application that authenticates users via Google Sign-In (OIDC), stores session data in DynamoDB, and displays JWT identity information on a dashboard.

**Live URL:** https://d3d6kluuz25cc4.cloudfront.net

---

## Architecture

```
User → CloudFront → S3 (static files)
                 → API Gateway V2 → Lambda → DynamoDB
                                  ↑
                             Google OIDC
```

| Component | Service | Purpose |
|---|---|---|
| Static Hosting | S3 + CloudFront | Serves HTML/JS files with low latency CDN |
| Authentication | Google OIDC | Verifies user identity via JWT |
| API | API Gateway V2 | Routes POST /v1/verifyToken to Lambda |
| Backend | AWS Lambda (Python) | Verifies JWT, generates UUID, writes to DB |
| Database | DynamoDB | Stores session UUID and user email |
| IaC | CloudFormation | Deploys all AWS infrastructure |
| CI/CD | GitHub Actions | Syncs static content to S3 on push |

---

## Application Flow

1. `/index.html` redirects the user to `/login.html`
2. User clicks "Sign in with Google" — Google authenticates and returns a JWT
3. `login.html` POSTs the JWT to `/v1/verifyToken` via API Gateway
4. Lambda verifies the JWT with Google, extracts the email, generates a UUID
5. UUID and email are stored in DynamoDB
6. User is redirected to `/dashboard.html` with UUID and JWT as URL parameters
7. Dashboard displays JWT contents, email, and UUID

---

## Infrastructure

Deployed via three CloudFormation stacks using `deploy/deploy.sh`:

- **Storage stack** — S3 bucket for static files and Lambda package
- **Backend stack** — Lambda function, DynamoDB table, API Gateway V2
- **Distribution stack** — CloudFront distribution fronting S3 and API Gateway

---

## Security Notes

- JWT verification is handled server-side in Lambda using `google.auth` — tokens are never trusted without verification
- Client secret is never exposed to the browser — only the client ID is used client-side
- Session cookies are set with `Secure` and `SameSite=Lax` flags
- DynamoDB access is scoped to the Lambda execution role via IAM — no public access
- S3 bucket content is served exclusively through CloudFront, not directly

---

## Project Structure

```
pub_It718/
├── deploy/
│   ├── deploy.sh           # Deployment script
│   ├── storage.json        # CloudFormation: S3
│   ├── backend.json        # CloudFormation: Lambda, DynamoDB, API Gateway
│   ├── distribution.json   # CloudFormation: CloudFront
│   └── lambda/
│       └── verifyToken.py  # Lambda function
├── website/
│   ├── index.html          # Redirects to login
│   ├── login.html          # Google Sign-In button
│   ├── dashboard.html      # Displays JWT, email, UUID
│   └── oidc.js             # OIDC helper
└── tests/
    └── tests.sh            # Integration tests
```

---

## Teardown

To remove all AWS infrastructure:
```bash
aws cloudformation delete-stack --stack-name your-prefix-distribution --region us-east-2
aws cloudformation delete-stack --stack-name your-prefix-backend --region us-east-2
aws cloudformation delete-stack --stack-name your-prefix-storage --region us-east-2
```
