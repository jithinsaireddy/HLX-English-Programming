# Deployment Guide (EB + S3/CloudFront)

This document captures your exact values and the steps to deploy using the existing GitHub Actions workflow `.github/workflows/deploy.yml`.

## Your AWS values

- AWS account ID: 963329266790
- Region: us-east-2
- EB Application: english-programming
- EB Environment: English-programming-env
- EB Environment URL (CNAME): English-programming-env.eba-8xub3cj3.us-east-2.elasticbeanstalk.com
- EB App Versions S3 Bucket: elasticbeanstalk-us-east-2-963329266790
- Frontend S3 Bucket: english-frontend (us-east-2)
- CloudFront Distribution ID: E2YRRPGYR2F51S
- GitHub OIDC Role ARN (for Actions): arn:aws:iam::963329266790:role/github-oidc-eb-s3-cf
- API URL (HTTPS, custom domain): https://api.englishprogramming.com

## Prerequisites (one-time)

1) ACM certificate (us-east-2) for `api.englishprogramming.com` is Issued.
2) Namecheap DNS:
   - CNAME `api` → `English-programming-env.eba-8xub3cj3.us-east-2.elasticbeanstalk.com`
   - The ACM DNS validation CNAME is added and validated.
3) EB Environment is Load Balanced with HTTPS :443 listener using the ACM cert.
4) CloudFront distribution E2YRRPGYR2F51S uses S3 OAC; the S3 bucket policy on `english-frontend` allows OAC access.

## Configure GitHub Secrets (exact names)

In GitHub → Repo → Settings → Secrets and variables → Actions → New repository secret:

- AWS_ROLE_ARN = arn:aws:iam::963329266790:role/github-oidc-eb-s3-cf
- AWS_REGION = us-east-2
- EB_S3_BUCKET = elasticbeanstalk-us-east-2-963329266790
- EB_APP_NAME = english-programming
- EB_ENV_NAME = English-programming-env
- S3_BUCKET_FRONTEND = english-frontend
- CLOUDFRONT_DISTRIBUTION_ID = E2YRRPGYR2F51S
- API_URL = https://api.englishprogramming.com

## Deploy (each time)

1) Push your code to `main` branch.
2) GitHub → Actions → “Deploy” → Run workflow (on `main`).
3) Wait for both jobs to succeed:
   - Backend to Elastic Beanstalk
   - Frontend to S3 + CloudFront (with invalidation)

## Validate after deploy

- Backend: `https://api.englishprogramming.com/health` → should return `ok`.
- Frontend (CloudFront domain): open, then in EPL tab run:
  ```
  create a list called xs
  insert 9 into list xs
  count of xs store in n
  print n
  ```
- Learn tab should load Synonyms and Telemetry.

## Troubleshooting

- If `https://api.englishprogramming.com/health` shows EB Sample page:
  - Your app is not deployed yet; run the GitHub Actions Deploy.
- If HTTPS fails:
  - Verify ALB has HTTPS :443 with the ACM cert.
  - Confirm Namecheap CNAME for `api` points to the EB env CNAME exactly.
  - Wait 5–10 minutes for DNS propagation.
- If frontend can’t load assets:
  - Ensure CloudFront OAC bucket policy is applied on `english-frontend`.
  - Re-run deploy to create invalidation or manually create one in CloudFront.
- Mixed-content errors in browser (HTTPS site calling HTTP API):
  - Ensure `API_URL` secret uses `https://api.englishprogramming.com`.
