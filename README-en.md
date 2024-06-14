# Microservice Carts

## Overview

The carts microservice is an autonomous module within the microservice architecture of an online store, designed for managing customer shopping carts. The service allows users to add items to the cart, change item quantities, remove items, and view the current state of the cart. It also handles the logic for applying promo codes and coupons.

## Project Structure

```
carts/
└── src/                                # Application source code
    ├── app/                            # Main application directory
    │   │
    │   ├── api/                        # Entry points - Primary adapters (API)
    │   │   ├── cli/                    # Command line interface entry points
    │   │   ├── events/                 # Entry points for processing events from message queues
    │   │   └── rest/                   # Entry points for RESTful API
    │   │
    │   ├── app_layer/                  # Use cases - Application
    │   │   ├── interfaces/             # Application layer interfaces
    │   │   └── use_cases/              # Specific use case implementations
    │   │
    │   ├── domain/                     # Business entities - Domain
    │   │   ├── cart_config/            # Entities and business logic for cart configuration
    │   │   ├── cart_coupons/           # Entities and business logic for cart coupons
    │   │   ├── cart_items/             # Entities and business logic for cart items
    │   │   ├── cart_notifications/     # Entities and business logic for cart notifications
    │   │   ├── carts/                  # Entities and business logic for carts
    │   │   └── interfaces/             # Domain layer interfaces
    │   │
    │   ├── infra/                      # Infrastructure components - Secondary adapters (Infra)
    │   │   ├── events/                 # Message queue consumers, task producers, etc.
    │   │   ├── http/                   # Components for HTTP interaction
    │   │   ├── repositories/           # Components for forming SQL queries
    │   │   └── unit_of_work/           # Component for working with data in a single transactional context
    │   │
    │   ├── config.py                   # Configuration file
    │   └── containers.py               # Dependency injection container
    │   
    └── tests/                          # Tests
        ├── environment/                # Test environment components
        ├── functional/                 # Functional tests
        └── unit/                       # Unit tests
```

## Key Features

- **Item Management**: Users can add items to the cart, change item quantities, and remove items from the cart.
- **Validation**: The system checks:
    - Maximum number of items in the cart
    - Minimum cart value before checkout
    - Purchase limits on certain items to prevent shortages for other customers
- **Order Processing**: Carts can be converted into orders. The system uses a status model for the cart. A cart is considered converted into an order when it changes to the COMPLETED status. The order business logic is not described in this microservice.
- **Promo Code Handling**: The microservice supports validation and application of promo codes, providing appropriate discounts to the user.
- **Cart State Management**: 
    Carts can be in various states, such as:
    - OPENED - open for user editing
    - LOCKED - closed for editing, order formation from this cart is in progress
    - COMPLETED - the orders microservice has successfully created an order from this cart
    - DEACTIVATED - cart is deleted and cannot be edited
    At any given time, a specific cart can change its state by only one process. This is a necessary requirement to ensure that the cart does not change state while the orders microservice is forming an order from it.
- **Forgotten Cart Identification**: The service tracks carts that have not been updated for a certain period and can send notifications to users to return and complete their purchases.

## Architecture

The microservice architecture is based on the principles of Clean Architecture and Hexagonal Architecture, ensuring clear separation of logic and infrastructure. The diagram shows the application layers:

![Code design concept.jpg](content%2Fru%2FCode%20design%20concept.jpg)

- **Domain layer**: Contains business rules and entities such as `Cart`, `CartItem`, `CartCoupon`, `CartNotification`, and `CartConfig`.
- **Application layer**: Orchestrates logic to achieve business goals. It calls business logic found in business entities and interacts with other system components through interfaces.
- **Primary adapters layer (API)**: Entry points to the application. They take input from users and package it into a form suitable for the application layer, then return data in a form suitable for user display (HTTP, HTML, JSON, CLI, etc.).
- **Secondary adapters layer (Infra)**: Contains technical tools (such as repositories, external API/service access, message brokers, platforms, etc.) and adapts input/output to the interface that meets the application layer needs.
- **Frameworks**: Frameworks, tools, technologies, libraries, etc.

#### Goal

To create a system with the following characteristics:
- **Framework Independence**: The architecture does not depend on the presence of any particular library. This allows frameworks to be viewed as tools rather than forcing the system into their constraints.
- **Ease of Testing**: Business rules can be tested without the user interface, database, web server, or any other external elements.
- **UI Independence**: The user interface can be easily changed without affecting the rest of the system. For example, the web interface can be replaced with a console interface without changing the business rules.
- **Database Independence**: You can switch from Oracle or SQL Server to Mongo, BigTable, CouchDB, or something else. Business logic is not tied to a database.
- **Independence from External Agents**: Business logic knows nothing about interfaces leading to the outside world.

The key rule driving this architecture is the dependency rule:
	*Dependencies in the source code must point inward toward higher-level policies.*

![Dependency rule.jpg](content%2Fru%2FDependency%20rule.jpg)

#### System Interaction with the External World

The microservice has two points of interaction with the external world:
1. **Primary adapters (API)**: Adapters that manage the application implement interaction with the system via REST, message queues, and CLI. Clients of these adapters can be end-users, other microservices, message queue consumers, technical users, cron jobs, etc.
2. **Secondary adapters (Infra)**: Adapters managed by the application implement system interaction with external dependencies - databases, distributed lock systems, authentication and authorization systems, message queues, external integrations via HTTP.

![System components and its interactors.jpg](content%2Fru%2FSystem%20components%20and%20its%20interactors.jpg)

#### Adding Item to Cart Scenario

The diagram below shows the interaction of system components in the scenario where a user adds an item to the cart:

![add item to cart use case.jpg](content%2Fru%2Fadd%20item%20to%20cart%20use%20case.jpg)

To handle this scenario, the system uses:
- The FastAPI web framework to accept HTTP requests and form HTTP responses
- Redis for establishing a lock on the cart's state change
- JWT-based authentication and authorization system for user identification
- A set of components for database access with PostgreSQL:
	- Sqlalchemy - ORM
	- UnitOfWork - abstraction for working with data in a single transactional context
	- Repository - components encapsulating SQL query logic and retrieving business entities from database data
- Business entities `Cart`, `CartConfig`, `CartItem` encapsulating the microservice's business logic
- A set of components for interaction with the external products integration (catalog microservice):
	- aiohttp - HTTP request tool
	- Clients encapsulating HTTP request logic to external integrations
	- Transport - abstraction forming HTTP requests via aiohttp
	- Retry system - ensures request retries in case of temporary external integration failures

The diagram shows the approximate control flow for this scenario:

![Flow of control.jpg](content%2Fru%2FFlow%20of%20control.jpg)

1. FastAPI web framework:
	1. Accepts HTTP request from the user
	2. Forms HTTP response for the user
2. Controller `app.api.rest.public.v1.cart_items.controllers.add_item`:
	1. Accepts initial HTTP request data
	2. Receives `AddCartItemUseCase` object via dependency injection mechanism
	3. Packages data into `AddItemToCartInputDTO`
	4. Calls `AddCartItemUseCase.execute` method with `AddItemToCartInputDTO`
	5. Processes method result and passes it to `CartViewModel` or throws an HTTP exception in case of errors from the method
3. Use case `AddCartItemUseCase`:
	1. Receives `AddItemToCartInputDTO`
	2. Uses `RedisLockSystem` to establish a lock on the cart
	3. Processes authorization token via `JWTAuthSystem` and retrieves user data
	4. Through transactional context `SqlAlchemyUnitOfWork` and repository `SqlAlchemyCartsRepository`, retrieves the `Cart` business object
	5. Calls `Cart` business logic:
		1. Checks if the user has rights to edit the cart. If not, throws an exception; otherwise
		2. If the item is already in the cart, adds its quantity to the current
