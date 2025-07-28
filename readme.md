API Base url = http://127.0.0.1:8000

ENDPOINTS & PAYLOADS
1. Ticket
1. Ticket	

/tickets/all

curl -X 'GET' \
  'http://127.0.0.1:8000/tickets/all' \
  -H 'accept: application/json'

[
  {
    "ticket_id": 1,
    "user_id": 16,
    "category_id": 1,
    "assigned_to": 1,
    "status_id": 1,
    "priority_id": 3,
    "title": "Network",
    "description": "No network",
    "created_at": "2025-05-27T17:13:08",
    "updated_at": "2025-06-17T17:50:39"
  }
]

/tickets/{ticket_id}
curl -X 'GET' \
  'http://127.0.0.1:8000/tickets/1' \
  -H 'accept: application/json'

{
  "ticket_id": 1,
  "user_id": 16,
  "category_id": 1,
  "assigned_to": 1,
  "status_id": 1,
  "priority_id": 3,
  "title": "Network",
  "description": "No network",
  "created_at": "2025-05-27T17:13:08",
  "updated_at": "2025-06-17T17:50:39"
}



/tickets/create
curl -X 'POST' \
  'http://127.0.0.1:8000/tickets/create' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "email": "charlotte.walker@dev.com",
  "title": "Paper Jam",
  "description": "string",
  "status_id": 1,
  "category_id": 1,
  "priority_id": 1,
  "assigned_to": 21
}'

{
  "message": "Ticket created successfully",
  "ticket_id": 9
}

/tickets/verify-email
/tickets/update-status
curl -X 'PUT' \
  'http://127.0.0.1:8000/tickets/update-status' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "ticket_id": 2,
  "assigned_to": 1,
  "new_status_id": 2
}'

{
  "ticket_id": 2,
  "title": "E22",
  "description": "Network",
  "status_id": 2,
  "assigned_to": 1
}

2. Technicians 
/users/technicians   # used to get all technicians from the table

curl -X 'GET' \
  'http://127.0.0.1:8000/users/technicians' \
  -H 'accept: application/json'


[
  {
    "user_id": 6,
    "first_name": "Sarah",
    "last_name": "Johnson"
  },
  {
    "user_id": 7,
    "first_name": "David",
    "last_name": "Anderson"
  }]

3. Ticket parameters (default)
/ticket/priorities

curl -X 'GET' \
  'http://127.0.0.1:8000/ticket-priorities' \
  -H 'accept: application/json'

[
  {
    "priority_id": 1,
    "name": "Low"
  },
  {
    "priority_id": 2,
    "name": "Medium"
  },
  {
    "priority_id": 3,
    "name": "High"
  }
]

/ticket-categories
curl -X 'GET' \
  'http://127.0.0.1:8000/ticket-categories' \
  -H 'accept: application/json'

[
  {
    "category_id": 1,
    "name": "Computer Hardware"
  },
  {
    "category_id": 2,
    "name": "Computer Software"
  },
  {
    "category_id": 3,
    "name": "Network"
  },
  {
    "category_id": 4,
    "name": "Printer"
  }
]

/ticket-statuses
curl -X 'GET' \
  'http://127.0.0.1:8000/ticket-statuses' \
  -H 'accept: application/json'

[
  {
    "status_id": 1,
    "name": "Open"
  },
  {
    "status_id": 2,
    "name": "In-progress"
  },
  {
    "status_id": 3,
    "name": "Completed"
  }
]