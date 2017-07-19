
# TODO: this should really be a json file in a config module...

DEFAULT_TASKS = [
    {
        'name': 'File Business Plan',
        'priority': 1.0,
        'status': "IN_PROGRESS",
        'workspaces': [
            "FORMATION",
            "FINANCE",
        ]
    },
    {
        'name': 'File for Tax ID',
        'priority': 1.0,
        'status': "COMPLETE",
        'workspaces': [
            "TAX",
            "FORMATION",
        ]
    },
    {
        'name': 'Contract Electrician',
        'priority': 0.0,
        'status': "NOT_STARTED",
        'workspaces': [
            "STRUCTURAL",
            "EQUIPMENT",
        ]
    },
    {
        'name': 'Register as Employer',
        'priority': 0.0,
        'status': "IN_PROGRESS",
        'workspaces': [
            "OPERATIONS",
            "EMPLOYEES",
        ]
    },
    {
        'name': 'Schedule Health Dept. Inspection',
        'priority': 0.5,
        'status': "NOT_STARTED",
        'workspaces': [
            "COMPLIANCE",
        ]
    },
]
