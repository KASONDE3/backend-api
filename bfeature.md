## Backend Features

### Authentication & Authorization
- User registration with secure password hashing
- Login with credential verification (bcrypt/passlib)
- JWT access and refresh tokens (HS256)
- Role-based access control (admin, technician, etc.)
- Extract role and department from JWT for RBAC
- Access logging for login/logout with timestamps, IP, and user-agent

### Users & Technicians
- Users stored in `users` table with roles and departments
- Fetch technician with lowest workload (assigned ticket count)
- List all technicians with ticket statistics by status (open, in-progress, completed)
- Dynamic list of unassigned/available technicians for assignment

### Tickets
- Create tickets with category, priority, status, and optional technician assignment
- View all tickets or fetch by ID (joined user and technician details)
- Update ticket status with authorization validation for assigned technician
- Department-wise ticket counts aggregation
- Email notifications:
  - Email assigned technician on ticket creation (if assigned)
  - Email ticket creator on status update

### Ticket Metadata
- Manage and expose ticket priorities with response times
- Manage and expose ticket categories
- Manage and expose ticket statuses

### Ticket Status Details
- Fetch ticket status details with timestamps
- Include technician name, created-by name, and department

### Recommendations
- Create, retrieve, update, delete recommendations
- Fetch recommendations for a specific ticket

### Chatbot & Reporting
- Conversational endpoint with generated responses and confidence scoring
- Persist chatbot conversations with timestamps and optional recommendations
- Conversation history and single-conversation detail retrieval
- Conversation summary endpoint for weekly reporting payloads
- Weekly report system:
  - Send weekly reports on-demand
  - Recover missed reports
  - Track report sends in `weekly_report_logs`
  - Report status endpoints for observability
- Health check and capabilities endpoints

### Security & Observability
- OAuth2 Bearer authentication scheme for protected endpoints
- Centralized JWT verification and helpers
- Access logs: admin-only view with pagination (timestamps, IP, user-agent)

### Infrastructure & Data Access
- Async SQLAlchemy with MySQL (aiomysql driver)
- Declarative models wired into a shared `Base`
- Dependency-injected async sessions for routes

### Developer Experience
- Modular route files grouped by feature (auth, tickets, chatbot, technicians, etc.)
- Pydantic response and request schemas for type-safe APIs


