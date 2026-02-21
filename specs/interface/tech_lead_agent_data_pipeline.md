# Spec: Tech Lead Agent Data Pipeline

**Target:** data_pipeline/tech_lead_agent.py

## Overview
This script defines a data pipeline that aggregates information from various sources to generate a summary report for a tech lead. The report focuses on active incidents, unresolved pull requests, and upcoming critical deadlines. This script pulls data from existing services/databases (assumed to exist).

## Requirements
- The script must be written in Python 3.11 or higher.
- The script must utilize FastAPI and Pydantic v2.
- The script must connect to the Incident Management System (IMS) database to retrieve active incident data.
- The script must connect to the Version Control System (VCS) API (e.g., GitHub, GitLab) to retrieve unresolved pull request data.
- The script must connect to the Project Management System (PMS) API (e.g., Jira, Asana) to retrieve upcoming deadline data.
- The script must format the data into a summary report that is both human-readable and machine-parseable (JSON).
- The script must be configurable to allow for different API keys, database connection strings, and report settings.
- The script should log all operations, including data fetching, processing, and report generation.
- The script must handle potential errors gracefully, such as API request failures and database connection errors.
- The script must be designed to be easily extendable to include additional data sources or metrics in the future.
- The script must be idempotent - rerunning the script with the same configuration and data should produce the same result.

## Data Contract

**Input:**

Configuration data passed as environment variables:

- `IMS_DB_CONNECTION_STRING`:  String representing the connection string to the Incident Management System database.
- `VCS_API_URL`: String representing the base URL for the Version Control System API.
- `VCS_API_TOKEN`: String representing the API token for authenticating with the Version Control System API.
- `PMS_API_URL`: String representing the base URL for the Project Management System API.
- `PMS_API_TOKEN`: String representing the API token for authenticating with the Project Management System API.
- `TECH_LEAD_EMAIL`: String representing the email address of the tech lead the report is for.

**Output:**

JSON object representing the summary report, returned via a FastAPI endpoint:

```json
{
  "tech_lead_email": "string",
  "active_incidents": [
    {
      "incident_id": "string",
      "title": "string",
      "severity": "string",
      "assigned_to": "string",
      "created_at": "string",
      "url": "string"
    }
  ],
  "unresolved_pull_requests": [
    {
      "pr_id": "string",
      "title": "string",
      "author": "string",
      "created_at": "string",
      "url": "string",
      "repository": "string"
    }
  ],
  "upcoming_deadlines": [
    {
      "task_id": "string",
      "title": "string",
      "due_date": "string",
      "project": "string",
      "url": "string"
    }
  ],
  "report_generated_at": "string"
}
```

**Data Source Schemas (assumed to exist, but schemas are illustrative):**

*   **Incident Management System (IMS) Database (Example using SQLAlchemy):**

    ```python
    from sqlalchemy import create_engine, Column, Integer, String, DateTime
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker
    from datetime import datetime

    Base = declarative_base()

    class Incident(Base):
        __tablename__ = 'incidents'
        id = Column(Integer, primary_key=True)
        title = Column(String)
        severity = Column(String)
        assigned_to = Column(String)
        created_at = Column(DateTime)
        url = Column(String)
    ```

*   **Version Control System (VCS) API (Example using GitHub API):**

    *   Request: `GET /pulls?state=open`
    *   Response (list of PR objects):

        ```json
        [
          {
            "id": 123,
            "title": "Fix bug in X",
            "user": { "login": "developer1" },
            "created_at": "2024-01-01T10:00:00Z",
            "html_url": "https://github.com/org/repo/pull/123",
            "base": { "repo": { "name": "repo" } }
          }
        ]
        ```

*   **Project Management System (PMS) API (Example using Jira API):**

    *   Request: `GET /search?jql=duedate <= now() + 7d AND status != Done`
    *   Response:

        ```json
        {
          "issues": [
            {
              "id": "PRJ-123",
              "key": "PRJ-123",
              "fields": {
                "summary": "Implement Y feature",
                "duedate": "2024-01-08",
                "project": { "name": "MyProject" }
              },
              "permalink": "https://jira.example.com/browse/PRJ-123"
            }
          ]
        }
        ```

## Behavior Scenarios

- **Scenario: Successful report generation**
  - Input: Valid IMS database connection string, VCS API URL and token, PMS API URL and token, and TECH_LEAD_EMAIL.  The IMS database contains active incidents, the VCS has unresolved pull requests, and the PMS has upcoming deadlines.
  - Outcome: The script successfully retrieves data from all three sources, aggregates it into a summary report in JSON format, and returns it via the FastAPI endpoint.  The `report_generated_at` field is set to the current timestamp.  A log message is written confirming successful report generation.

- **Scenario: VCS API failure**
  - Input: Invalid VCS API token. Valid IMS database connection string, PMS API URL and token, and TECH_LEAD_EMAIL.
  - Outcome: The script catches the VCS API error, logs the error, and continues execution with the other data sources. The "unresolved_pull_requests" field in the output JSON will be an empty list (`[]`). A log message is written indicating the VCS API failure.

- **Scenario: No data found in any source**
  - Input: Valid IMS database connection string, VCS API URL and token, PMS API URL and token, and TECH_LEAD_EMAIL.  The IMS database has no active incidents, the VCS has no unresolved pull requests, and the PMS has no upcoming deadlines.
  - Outcome: The script retrieves empty datasets from all three sources and generates a summary report in JSON format with empty lists for "active_incidents", "unresolved_pull_requests", and "upcoming_deadlines". The `report_generated_at` field is set to the current timestamp.  A log message confirms successful report generation (though the report is empty).

- **Scenario: Invalid TECH_LEAD_EMAIL format**
  - Input: Valid IMS database connection string, VCS API URL and token, PMS API URL and token, but TECH_LEAD_EMAIL is not a valid email address (e.g., "notanemail").
  - Outcome:  The script raises a `ValueError` due to invalid TECH_LEAD_EMAIL during Pydantic model validation, logs the error, and returns a 400 HTTP error with a descriptive message.

## Out of Scope
- User authentication and authorization for accessing the FastAPI endpoint.
- Persistence of the generated report.  This spec only covers generating the report and returning it as a response.
- Detailed error handling for specific database or API errors beyond logging and graceful degradation.
- Automated deployment of the script.
- Implementing the Incident Management System (IMS) database, Version Control System (VCS) API, or Project Management System (PMS) API.  These are assumed to exist and be accessible.
