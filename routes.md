## Auth

- POST `/auth/register`
  - Sub-features: hashes password and persists new auth record
- POST `/auth/login`
  - Sub-features: verifies password, loads user profile (role, dept, name), issues access/refresh JWTs, logs access event with IP and user-agent
- POST `/auth/refresh`
  - Sub-features: verifies refresh token and re-issues new access/refresh tokens
- POST `/auth/logout`
  - Sub-features: logs logout event even if token is missing/expired; captures IP and user-agent
- GET `/auth/me`
  - Sub-features: reads user from JWT (`sub` email)
- GET `/auth/all`
  - Sub-features: lists registered auth users
- PUT `/auth/update-password`
  - Sub-features: hashes and updates password
- DELETE `/auth/delete/{email}`
  - Sub-features: deletes auth user by email
- GET `/auth/my-role`
  - Sub-features: extracts role from JWT
- GET `/auth/admin-only`
  - Sub-features: role guard `admin` required
- GET `/auth/technician-only`
  - Sub-features: role guard `technician` required
- GET `/auth/count`
  - Sub-features: counts total records in `users` table
- GET `/auth/access-logs`
  - Sub-features: admin-only; paginated access logs with timestamps, IP, user-agent

## Chatbot

- POST `/chatbot/chat`
  - Sub-features: generates response with confidence and optional recommendation; logs conversation
- GET `/chatbot/conversations`
  - Sub-features: lists conversation history (with pagination in route code)
- GET `/chatbot/conversations/summary`
  - Sub-features: weekly summary aggregation payload
- GET `/chatbot/conversations/{conversation_id}`
  - Sub-features: fetch single conversation detail
- POST `/chatbot/conversations/analyze`
  - Sub-features: analyzes conversations for trends/insights
- POST `/chatbot/reports/recover-missed`
  - Sub-features: attempts to resend missed weekly reports; logs to `weekly_report_logs`
- GET `/chatbot/reports/status`
  - Sub-features: returns report scheduling/sent status
- GET `/chatbot/health`
  - Sub-features: health check endpoint
- POST `/chatbot/reports/send-now`
  - Sub-features: triggers on-demand weekly report; logs send metadata
- GET `/chatbot/reports/send-now/status`
  - Sub-features: returns status of last on-demand send
- GET `/chatbot/capabilities`
  - Sub-features: lists chatbot capabilities

## Tickets

- GET `/tickets/verify-email`
  - Sub-features: validates user exists by email and returns profile basics
- GET `/tickets/all`
  - Sub-features: lists all tickets
- GET `/tickets/{ticket_id}`
  - Sub-features: returns ticket plus joined user and technician details
- POST `/tickets/create`
  - Sub-features: creates ticket; optionally emails assigned technician with ticket info
- PUT `/tickets/update-status`
  - Sub-features: validates assigned technician; updates status; emails ticket creator about new status
- GET `/tickets/counts/department-wise`
  - Sub-features: aggregates tickets by user department

## Ticket Metadata

- GET `/meta/ticket-priorities`
  - Sub-features: lists configured priorities with response times
- GET `/meta/ticket-categories`
  - Sub-features: lists categories
- GET `/meta/ticket-statuses`
  - Sub-features: lists statuses

## Ticket Status

- GET `/ticket-status/status/{ticket_id}`
  - Sub-features: returns ticket status detail with timestamps and associated names

## Recommendations

- POST `/recommendations/`
  - Sub-features: creates recommendation for ticket/content
- GET `/recommendations/`
  - Sub-features: lists recommendations
- GET `/recommendations/ticket/{ticket_id}`
  - Sub-features: lists recommendations for a ticket
- GET `/recommendations/{recomm_id}`
  - Sub-features: fetch single recommendation
- PUT `/recommendations/{recomm_id}`
  - Sub-features: updates recommendation content/fields
- DELETE `/recommendations/{recomm_id}`
  - Sub-features: deletes recommendation

## Technicians

- GET `/technicians`
  - Sub-features: returns technician with the lowest current workload (counts assigned tickets via subquery)
- GET `/technicians/with-ticket-stats`
  - Sub-features: per-technician counts of tickets by status (open, in-progress, completed)

## Dynamic Technician

- GET `/dynamic-technician/unassigned-technicians`
  - Sub-features: lists technicians available for assignment (no or low assignments)

## Meta

- GET `/meta/categories/`
  - Sub-features: lists meta categories
- GET `/meta/priorities/`
  - Sub-features: lists meta priorities
- GET `/meta/statuses/`
  - Sub-features: lists meta statuses


