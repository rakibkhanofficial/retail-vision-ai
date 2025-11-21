# Retail Vision AI - Project Structure

## Complete Folder Structure

```
retail-vision-ai/
├── .env                           # Root environment variables
├── .gitignore                     # Git ignore file
├── docker-compose.yml             # Docker orchestration
├── README.md                      # Main documentation
│
├── backend/                       # Backend service
│   ├── .env                       # Backend environment variables
│   ├── .dockerignore
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── alembic.ini               # Database migrations config
│   │
│   ├── app/                       # Main application package
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI application entry
│   │   │
│   │   ├── api/                   # API endpoints
│   │   │   ├── __init__.py
│   │   │   ├── deps.py           # Dependencies (auth, db)
│   │   │   └── v1/               # API v1
│   │   │       ├── __init__.py
│   │   │       ├── endpoints/
│   │   │       │   ├── __init__.py
│   │   │       │   ├── auth.py   # Authentication endpoints
│   │   │       │   ├── detection.py # Detection endpoints
│   │   │       │   └── analysis.py  # Analysis endpoints
│   │   │       └── router.py     # Main router
│   │   │
│   │   ├── core/                  # Core functionality
│   │   │   ├── __init__.py
│   │   │   ├── config.py         # Configuration
│   │   │   ├── security.py       # JWT, password hashing
│   │   │   └── logging.py        # Logging configuration
│   │   │
│   │   ├── models/                # Database models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── detection.py
│   │   │   └── product.py
│   │   │
│   │   ├── schemas/               # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── detection.py
│   │   │   ├── product.py
│   │   │   └── response.py
│   │   │
│   │   ├── services/              # Business logic
│   │   │   ├── __init__.py
│   │   │   ├── yolo_service.py   # YOLO detection
│   │   │   ├── gemini_service.py # AI analysis
│   │   │   └── analysis_service.py # Product analysis
│   │   │
│   │   ├── db/                    # Database
│   │   │   ├── __init__.py
│   │   │   ├── session.py        # Database session
│   │   │   └── base.py           # Base model
│   │   │
│   │   └── utils/                 # Utilities
│   │       ├── __init__.py
│   │       ├── image_processing.py
│   │       └── helpers.py
│   │
│   ├── uploads/                   # Uploaded files (gitignored)
│   │   ├── original/
│   │   ├── annotated/
│   │   └── thumbnails/
│   │
│   ├── models/                    # ML models (gitignored)
│   │   └── yolov8n.pt
│   │
│   └── tests/                     # Tests
│       ├── __init__.py
│       ├── test_auth.py
│       └── test_detection.py
│
└── frontend/                      # Frontend service
    ├── .env.local                 # Frontend environment variables
    ├── .dockerignore
    ├── Dockerfile
    ├── package.json
    ├── tsconfig.json
    ├── tailwind.config.ts
    ├── next.config.js
    ├── postcss.config.js
    │
    ├── public/                    # Static assets
    │   ├── icons/
    │   ├── images/
    │   └── logos/
    │
    ├── src/                       # Source code
    │   │
    │   ├── app/                   # Next.js 14 App Router
    │   │   ├── layout.tsx         # Root layout
    │   │   ├── page.tsx           # Landing page
    │   │   ├── globals.css        # Global styles
    │   │   │
    │   │   ├── (auth)/            # Auth group
    │   │   │   ├── login/
    │   │   │   │   └── page.tsx
    │   │   │   └── register/
    │   │   │       └── page.tsx
    │   │   │
    │   │   ├── (dashboard)/       # Dashboard group
    │   │   │   ├── layout.tsx
    │   │   │   ├── dashboard/
    │   │   │   │   └── page.tsx
    │   │   │   ├── detections/
    │   │   │   │   ├── page.tsx
    │   │   │   │   └── [id]/
    │   │   │   │       └── page.tsx
    │   │   │   └── analytics/
    │   │   │       └── page.tsx
    │   │   │
    │   │   └── api/               # API routes
    │   │       └── auth/
    │   │           └── [...nextauth]/
    │   │               └── route.ts
    │   │
    │   ├── components/            # React components
    │   │   ├── ui/                # UI components
    │   │   │   ├── button.tsx
    │   │   │   ├── card.tsx
    │   │   │   ├── input.tsx
    │   │   │   ├── modal.tsx
    │   │   │   ├── table.tsx
    │   │   │   └── loading.tsx
    │   │   │
    │   │   ├── layout/            # Layout components
    │   │   │   ├── header.tsx
    │   │   │   ├── sidebar.tsx
    │   │   │   └── footer.tsx
    │   │   │
    │   │   ├── features/          # Feature components
    │   │   │   ├── ImageUploader.tsx
    │   │   │   ├── CameraCapture.tsx
    │   │   │   ├── DetectionResults.tsx
    │   │   │   ├── ProductAnalysis.tsx
    │   │   │   └── ChatInterface.tsx
    │   │   │
    │   │   └── landing/           # Landing page components
    │   │       ├── Hero.tsx
    │   │       ├── Features.tsx
    │   │       └── CTA.tsx
    │   │
    │   ├── lib/                   # Libraries & utilities
    │   │   ├── api.ts            # API client
    │   │   ├── auth.ts           # NextAuth config
    │   │   ├── utils.ts          # Utility functions
    │   │   └── constants.ts      # Constants
    │   │
    │   ├── hooks/                 # Custom React hooks
    │   │   ├── useAuth.ts
    │   │   ├── useCamera.ts
    │   │   └── useDetection.ts
    │   │
    │   ├── types/                 # TypeScript types
    │   │   ├── index.ts
    │   │   ├── api.ts
    │   │   └── detection.ts
    │   │
    │   └── styles/                # Additional styles
    │       └── animations.css
    │
    └── tests/                     # Frontend tests
        └── components/
            └── ImageUploader.test.tsx
```

## Key Design Decisions

### Backend Structure
- **Clean Architecture**: Separation of concerns (API, Services, Models, Schemas)
- **Standard Python Package**: Proper `app/` package structure
- **Service Layer**: Business logic isolated from API endpoints
- **Database Models**: SQLAlchemy ORM with proper relationships
- **API Versioning**: `/api/v1/` for future compatibility

### Frontend Structure
- **Next.js 14 App Router**: Modern routing with layouts
- **Route Groups**: `(auth)` and `(dashboard)` for different layouts
- **Component Organization**: UI, Layout, Features separation
- **Custom Hooks**: Reusable logic extracted
- **Type Safety**: Full TypeScript coverage

### File Naming Conventions
- **Backend**: `snake_case.py` (Python standard)
- **Frontend**: `PascalCase.tsx` for components, `camelCase.ts` for utilities
- **Folders**: `lowercase` or `kebab-case`
