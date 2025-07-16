# FastAPI Reviews App

## Setup

1. Copy environment variables template:
   ```bash
   cp .env.template .env
2. Edit .env and set your SQLITE_PATH

    By default:
    ```bash
    SQLITE_PATH=reviews.db
    ```
3. Create virtual environment and install dependencies:
    ```bash
    python -m venv .venv
    source .venv/bin/activate

    pip install -r requirements.txt
    ```
4. Run the app:
    ```bash
    uvicorn main:app --reload
    ```

### Notes

**Performance is guaranteed with pyhon3.12**

## Test

1. Open http://localhost:8000/docs for Swagger UI

2. Test with curl:

    POST /reviews:

    ```bash
    curl -X POST http://localhost:8000/reviews -H "Content-Type: application/json" -d '{"text":"очень хорошо"}'
    ```
    Response sample:
    ```bash
    {"id":4,"text":"очень очень хорошо","sentiment":"positive","createdAt":"2025-07-16T12:49:11.790270"}
    ```
    <br><br>

    GET /reviews (optional with filter):
    ```bash
    curl "http://localhost:8000/reviews?sentiment=positive"
    ```

    Response sample:
    ```bash
    [{"id":3,"text":"очень очень хорошо","sentiment":"positive","createdAt":"2025-07-16T12:48:41.375683"},{"id":4,"text":"очень очень хорошо","sentiment":"positive","createdAt":"2025-07-16T12:49:11.790270"}]
    ```