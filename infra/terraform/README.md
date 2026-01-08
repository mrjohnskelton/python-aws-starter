Infra Terraform scaffold for `python-aws-starter`.

Quickstart

1. Install Terraform (>= 1.0.0).
2. Configure AWS credentials via env vars or profiles (e.g., `AWS_PROFILE`).
3. (Optional) Create an S3 bucket and DynamoDB table for remote state, then copy
   `backend.tf.example` to `backend.tf` and fill values.
4. Initialize Terraform:

```bash
cd infra/terraform
terraform init
```

5. Plan and apply:

```bash
terraform plan -out=tfplan
terraform apply tfplan
```

Notes

- This scaffold intentionally contains no live resources. Add modules under
  `modules/` and resources in `main.tf` when ready.
- Keep real backend details out of the repo. Use `backend.tf` locally or CI
  secrets for remote state configuration.
