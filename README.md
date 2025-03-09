# Wine Region Evaluator - OI Assessment

This project is a Django-based application designed to evaluate the suitability of different wine-growing regions based on climate data. It provides APIs to manage regions, fetch and process climate data, and analyze the suitability and performance of regions for grape growing.

This project has been done as part of the Software Engineering Assessment for Operative Intelligence. I estimate this took me between 8 and 10 hours in total.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
    - [Region Management](#region-management)
    - [Climate Analysis](#climate-analysis)

## Prerequisites
- [Docker](https://docs.docker.com/get-started/get-docker/)

- Docker Compose

## Installation

1. Clone the repository:
```
git clone https://github.com/yourusername/wine_region_evaluator.git
```
2. Navigate to the project directory:
```
cd wine_region_evaluator
```

3. Create and configure the `.env` file:
```
cp .env.example .env
# Edit the .env file to set your environment variables
```

4. Build and run the Docker containers:
```
docker compose up --build
```
- Example data will be automatically populated in the database when first running the docker container.

5. The application will be available at `http://localhost:8000`.

## Usage

### Running Tests

The tests will automatically run when running the docker container.

To manually run the tests you can run:
```
docker compose run api python manage.py test
```

## API Endpoints

### Region Management

#### Get Region
- **Endpoint:** `/api/region/`
- **Method:** `GET`
- **Query Parameters:**
    - `name` (required): The name of the region to fetch.
- **Response:**
    ```json
    {
        "name": "Region Name",
        "latitude": 45.0,
        "longitude": 45.0,
        "description": "Region Description"
    }
    ```

#### Create Region
- **Endpoint:** `/api/region/`
- **Method:** `POST`
- **Request Body:**
    ```json
    {
        "name": "New Region",
        "latitude": 50.0,
        "longitude": 50.0,
        "description": "New Region Description"
    }
    ```
- **Response:** `200 OK` on success.

#### Delete Region
- **Endpoint:** `/api/region/`
- **Method:** `DELETE`
- **Query Parameters:**
    - `name` (required): The name of the region to delete.
- **Response:** `200 OK` on success.

### Climate Analysis

#### Seasonal Suitability
- **Endpoint:** `/api/analysis/season`
- **Method:** `GET`
- **Query Parameters:**
    - `region` (optional, repeatable): The names of the regions to analyze. If not provided, all regions will be analyzed.
- **Response:**
    ```json
    [
        {
            "name": "Region Name",
            "best_growing_season": ["December", "January", "February"]
        }
    ]
    ```

#### Long-term Viability
- **Endpoint:** `/api/analysis/viability`
- **Method:** `GET`
- **Query Parameters:**
    - `region` (optional, repeatable): The names of the regions to analyze. If not provided, all regions will be analyzed.
- **Response:**
    ```json
    [
        {
            "name": "Region Name",
            "longterm_viability": 75.5
        }
    ]
    ```

#### Performance Comparison
- **Endpoint:** `/api/analysis/compare_performance`
- **Method:** `GET`
- **Query Parameters:**
    - `region` (optional, repeatable): The names of the regions to compare. If not provided, all regions will be compared.
    - `only` (optional): Specify `best` or `worst` to get only the best or worst performing region.
- **Response:**
    ```json
    [
        {
            "name": "Region Name",
            "avg_historical_performance": 85.0
        }
    ]
    ```

