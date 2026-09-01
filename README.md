# FlowCore: Dynamic Workflow and State Machine Engine

FlowCore is a centralized State Machine platform that enables flexible, role-based, and dynamic management of internal corporate workflows.

## Development Environment Setup

Follow the steps below sequentially to run and develop the project in your local environment:

**1. Clone the Repository:**
```bash
git clone [https://github.com/olmezarda/flowcore](https://github.com/olmezarda/flowcore)
cd flowcore
```

**2. Create and Activate a Virtual Environment:**
```bash
python -m venv venv
```
*Windows:* `venv\Scripts\activate`
*macOS/Linux:* `source venv/bin/activate`

**3. Install Dependencies:**
```bash
pip install -r requirements.txt
```

**4. Apply Database Migrations:**
```bash
python manage.py migrate
```

**5. Create a Superuser Account:**
*(Required to access the system administration panel)*
```bash
python manage.py createsuperuser
```

## Contact

**Email:** olm.zarda@gmail.com
**LinkedIn:** [Arda Ölmez](https://www.linkedin.com/in/olmezarda/)