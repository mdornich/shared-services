# Shared Services

Reusable services for all projects:
- Magic Link Authentication (Supabase)
- Company Detection from emails

## Installation

```bash
pip install git+https://github.com/mdornich/shared-services.git@v1.0.0
```

## Usage

```python
from shared_services.supabase_auth import MagicLinkService
from shared_services.company_detection import CompanyDetector
```