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

## Setup & Deployment

### Prerequisites
- AWS CLI configured with valid credentials
- Google Cloud project with OAuth 2.0 Client ID created
- Python 3.x and pip available

### 1. Google OAuth
- Create a project at [Google Cloud Console](https://console.cloud.google.com)
- Create OAuth 2.0 credentials (Web application type)
- Note your client ID — you'll need it in step 3

### 2. Clone the repo
```bash
git clone https://github.com/SSchmitt2024/pub_It718.git
cd pub_It718
```

### 3. Insert your Google client ID
```bash
sed -i 's/YOUR_CLIENT_ID/your-client-id.apps.googleusercontent.com/' deploy/lambda/verifyToken.py
sed -i 's/YOUR_CLIENT_ID/your-client-id.apps.googleusercontent.com/' website/login.html
```

### 4. Deploy
```bash
cd deploy
bash deploy.sh your-unique-prefix
```

The script will output your CloudFront URL when complete.

### 5. Update Google OAuth
Add the CloudFront URL to your OAuth credentials:
- **Authorized JavaScript origins:** `https://your-cloudfront-url.cloudfront.net`
- **Authorized redirect URIs:** `https://your-cloudfront-url.cloudfront.net/v1/verifyToken`

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
