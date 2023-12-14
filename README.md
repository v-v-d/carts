# Clean architecture example

## Project structure
```
clean-architecture/
└── src/                        # Source code of the application
    ├── alembic/                # Database migrations for SQLAlchemy
    ├── app/                    # Main application directory
    │   │
    │   ├── api/                # Entry points (Primary adapters layer)
    │   │   ├── cli/            # Entry point for command line interface (CLI)
    │   │   │   └── main.py     # Main CLI file
    │   │   ├── events/         # Entry point for events handling
    │   │   └── rest/           # Entry point for RESTful API
    │   │       └── main.py     # Main RESTful API file
    │   │
    │   ├── app_layer/          # Application layer (Use Case)
    │   │   ├── interfaces/     # Interfaces of the application layer
    │   │   └── services/       # Services of the application layer (Use Cases)
    │   │
    │   ├── domain/             # Domain layer (Business logic)
    │   │   ├── interfaces/     # Interfaces of the domain layer
    │   │   ├── items/          # Entities and business logic for item domain
    │   │   └── carts/          # Entities and business logic for cart domain
    │   │
    │   ├── infra/              # Infrastructure layer (Secondary adapters layer)
    │   │   ├── events/         # Event implementation (workers, queues, etc.)
    │   │   ├── http/           # HTTP transports, retry systems and clients
    │   │   ├── repositories/   # Data repositories
    │   │   └── unit_of_work/   # Unit of Work implementation
    │   │
    │   ├── config.py           # Configuration file
    │   └── containers.py       # Dependency container (DI container)
    │   
    └── tests/                  # Tests
        ├── environment/        # Test environments (test repositories, test unit of works, etc.)
        ├── functional/         # Functional tests
        │   └── conftest.py     # Configuration for functional tests
        ├── unit/               # Unit tests
        └── conftest.py         # Common configuration for tests
```