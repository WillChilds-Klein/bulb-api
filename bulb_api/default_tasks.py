
# TODO: this should really be a json file in a config module...

DEFAULT_TASKS = [
    {
        'org_id': None,
        'name': 'File Business Plan',
        'priority': 0.25,
        'status': "IN_PROGRESS",
        'workspaces': [
            "FORMATION",
            "FINANCE",
        ]
    },
    {
        'org_id': None,
        'name': 'File for Tax ID',
        'priority': 1.0,
        'status': "COMPLETE",
        'workspaces': [
            "TAX",
            "FORMATION",
        ]
    },
    {
        'org_id': None,
        'name': 'Contract Electrician',
        'priority': 0.0,
        'status': "NOT_STARTED",
        'workspaces': [
            "STRUCTURAL",
            "EQUIPMENT",
        ]
    },
    {
        'org_id': None,
        'name': 'Register as Employer',
        'priority': 0.0,
        'status': "IN_PROGRESS",
        'workspaces': [
            "OPERATIONS",
            "EMPLOYEES",
        ]
    },
    {
        'org_id': None,
        'name': 'Schedule Health Dept. Inspection',
        'priority': 0.33,
        'status': "NOT_STARTED",
        'workspaces': [
            "COMPLIANCE",
        ]
    },
]