# HW8 - Dockerized CI/CD Pipeline

A fully Dockerized Express.js REST API with automated CI/CD pipeline using GitHub Actions.

## 📋 Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [API Endpoints](#api-endpoints)
- [Testing](#testing)
- [Docker](#docker)
- [CI/CD Pipeline](#cicd-pipeline)
- [Configuration](#configuration)

## ✨ Features

- RESTful API with CRUD operations
- Dockerized application
- Multi-stage Docker build for optimized images
- Automated testing with Jest
- ESLint for code quality
- GitHub Actions CI/CD pipeline
- Docker Hub integration
- Health checks
- Non-root user in Docker for security

## 🔧 Prerequisites

- Node.js (v18 or higher)
- Docker and Docker Compose
- Git
- Docker Hub account (for CI/CD)

## 📁 Project Structure

```
HW8/
├── .github/
│   └── workflows/
│       └── ci-cd.yml          # GitHub Actions workflow
├── src/
│   ├── app.js                 # Main application file
│   ├── routes/
│   │   └── itemRoutes.js      # API routes
│   └── controllers/
│       └── itemController.js  # Business logic
├── test/
│   └── api.test.js            # API tests
├── Dockerfile                 # Docker configuration
├── docker-compose.yml         # Docker Compose configuration
├── .dockerignore              # Docker ignore file
├── .gitignore                 # Git ignore file
├── .eslintrc.json             # ESLint configuration
├── .env.example               # Environment variables example
├── package.json               # Node.js dependencies
└── README.md                  # This file
```

## 📦 Installation

### Local Development

1. Clone the repository:
```bash
cd Assignments/HW8
```

2. Install dependencies:
```bash
npm install
```

3. Create environment file:
```bash
cp .env.example .env
```

4. Edit `.env` if needed (default port is 3000)

## 🚀 Running the Application

### Local Development

```bash
# Development mode with auto-reload
npm run dev

# Production mode
npm start
```

The API will be available at `http://localhost:3000`

### Using Docker

#### Build and run with Docker:
```bash
docker build -t hw8-api .
docker run -p 3000:3000 hw8-api
```

#### Using Docker Compose:
```bash
docker-compose up --build
```

To stop:
```bash
docker-compose down
```

## 📚 API Endpoints

### Base URL
```
http://localhost:3000
```

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Welcome message and API info |
| GET | `/api/items` | Get all items |
| GET | `/api/items/:id` | Get item by ID |
| POST | `/api/items` | Create new item |
| PUT | `/api/items/:id` | Update item by ID |
| DELETE | `/api/items/:id` | Delete item by ID |

### Example Requests

#### Get all items
```bash
curl http://localhost:3000/api/items
```

#### Get single item
```bash
curl http://localhost:3000/api/items/1
```

#### Create new item
```bash
curl -X POST http://localhost:3000/api/items \
  -H "Content-Type: application/json" \
  -d '{"name":"New Item","description":"Description","quantity":10}'
```

#### Update item
```bash
curl -X PUT http://localhost:3000/api/items/1 \
  -H "Content-Type: application/json" \
  -d '{"name":"Updated Item","quantity":25}'
```

#### Delete item
```bash
curl -X DELETE http://localhost:3000/api/items/1
```

### Response Format

#### Success Response
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Item Name",
    "description": "Item Description",
    "quantity": 10
  }
}
```

#### Error Response
```json
{
  "success": false,
  "error": "Error message"
}
```

## 🧪 Testing

### Run all tests
```bash
npm test
```

### Run tests in watch mode
```bash
npm run test:watch
```

### Run linter
```bash
npm run lint
```

### Fix linting issues
```bash
npm run lint:fix
```

## 🐳 Docker

### Dockerfile Features

- **Multi-stage build**: Optimized image size
- **Alpine Linux**: Minimal base image
- **Non-root user**: Enhanced security
- **Health check**: Container health monitoring
- **Layer caching**: Faster builds

### Docker Commands

```bash
# Build image
docker build -t hw8-api .

# Run container
docker run -p 3000:3000 hw8-api

# Run with environment variables
docker run -p 3000:3000 -e PORT=8080 hw8-api

# View logs
docker logs <container-id>

# Access container shell
docker exec -it <container-id> sh
```

### Docker Compose Commands

```bash
# Start services
docker-compose up

# Start in detached mode
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild and start
docker-compose up --build
```

## 🔄 CI/CD Pipeline

The project uses GitHub Actions for automated CI/CD.

### Pipeline Stages

1. **Test Stage**
   - Checkout code
   - Setup Node.js
   - Install dependencies
   - Run ESLint
   - Run Jest tests
   - Upload coverage reports

2. **Build Stage**
   - Build Docker image
   - Test Docker container

3. **Deploy Stage** (only on main branch)
   - Login to Docker Hub
   - Tag image with version
   - Push to Docker Hub

### Setting up CI/CD

1. **Create Docker Hub account** at https://hub.docker.com

2. **Add GitHub Secrets**:
   Go to your repository → Settings → Secrets and variables → Actions
   
   Add these secrets:
   - `DOCKER_USERNAME`: Your Docker Hub username
   - `DOCKER_PASSWORD`: Your Docker Hub password or access token

3. **Push to main branch** to trigger the pipeline

4. **View workflow** in the Actions tab of your GitHub repository

### Workflow Triggers

- Push to `main` or `develop` branches
- Pull requests to `main` branch

### Docker Hub Tags

The pipeline creates multiple tags:
- `latest`: Latest version from main branch
- `main-<commit-sha>`: Specific commit from main
- Branch-specific tags for other branches

## ⚙️ Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```env
PORT=3000
NODE_ENV=development
```

### ESLint Configuration

The project uses ESLint for code quality. Configuration is in `.eslintrc.json`.

To customize rules, edit the file and run:
```bash
npm run lint:fix
```

## 🛠️ Development

### Adding New Endpoints

1. Add route in `src/routes/itemRoutes.js`
2. Add controller function in `src/controllers/itemController.js`
3. Add tests in `test/api.test.js`
4. Run tests to verify

### Code Style

- Use 2 spaces for indentation
- Use single quotes
- Add semicolons
- Follow ESLint rules

## 📝 Notes

- The API uses in-memory storage (data resets on restart)
- For production, integrate a real database (MongoDB, PostgreSQL, etc.)
- Update DOCKER_USERNAME in CI/CD workflow to your Docker Hub username
- The health check ensures container reliability

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Write/update tests
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

ISC

## 👤 Author

Created for HW8 - Distributed Systems Course
