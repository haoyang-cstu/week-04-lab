## Week 3 Reflection

1. What was the most confusing thing about Python compared to JavaScript?

   The indentation. In JavaScript the curly braces `{}` decide what's inside a
   function or an `if`, and whitespace doesn't matter. In Python the indentation
   *is* the syntax — if a line is indented wrong, the code either breaks or
   silently does the wrong thing. A few other things that tripped me up:
   - `None` instead of `null`, and `True`/`False` are capitalized.
   - Type hints like `book_id: int` and `status: Optional[str] = None`, which
     JavaScript doesn't make you write.
   - `snake_case` for names instead of `camelCase`.

2. What does an HTTP status code tell you? Give one example.

   It's a number the server sends back to tell the client how the request went,
   without the client having to read the body. Roughly: 2xx = success,
   4xx = the client did something wrong, 5xx = the server broke. Example: when I
   asked for `GET /books/99` and that book didn't exist, the API returned
   **404 Not Found**. Another one I saw: POSTing a book with no `author` returned
   **422**, meaning my input failed validation.

3. What was the difference between a path parameter and a query parameter?

   A path parameter is part of the URL path and usually identifies *one specific
   resource* — like the `2` in `GET /books/2` (give me the book with id 2). A
   query parameter comes after the `?` and is usually for *filtering or options*
   on a collection — like `GET /books?status=reading` (give me the books, but
   only the ones that are being read). In FastAPI, `book_id` showed up in the
   route as `/books/{book_id}` (path), while `status` was just a normal function
   argument with a default (query).

4. What would happen to all the data if you restarted the server right now?
   Why is that a problem, and what will we use to fix it?

   All the books would disappear. Right now they live in a plain Python list
   (`books_db = []`) that only exists in the server's memory, so restarting the
   process resets it to empty and `next_id` goes back to 1. I actually saw this
   happen — every fresh start, the IDs began at 1 again. That's a problem because
   a real app needs data to survive restarts, crashes, and deploys, and to be
   shared if more than one server is running. The fix is to store the data in a
   **database** (so it's saved to disk and persists), which is what we'll use
   instead of the in-memory list.

## Week 4 Reflection

1. What is the difference between the SQLAlchemy model and the Pydantic schema?

   They both describe a "Book," but they live on different sides of the app. The
   **SQLAlchemy model** (`Book` in `models.py`) describes the *database table* —
   its columns, types, primary key, and which fields can be `NULL`. It's about how
   the data is *stored* in Postgres. The **Pydantic schema** (`schemas.py`)
   describes the *API* — the shape of the JSON coming in (`BookCreate`,
   `BookUpdate`) and going out (`BookResponse`), plus validation rules. It's about
   the *contract with the client*. They're deliberately separate: I don't want the
   client to be able to set the `id` (the database owns that), and I might store
   columns I never expose. The bridge between them is
   `model_config = {"from_attributes": True}`, which lets a `BookResponse` be built
   straight from a `Book` ORM object instead of a dict.

2. What does `Depends(get_db)` do? Why does every endpoint need it?

   `get_db` opens a database session, `yield`s it to the route, and then closes it
   in a `finally` block when the request is done. `Depends(get_db)` tells FastAPI
   to run that function for me and hand the session in as the `db` argument — this
   is dependency injection. Every endpoint that touches the database needs it
   because each request should get its own short-lived session that's guaranteed to
   be cleaned up afterward. Without it I'd be manually creating and closing sessions
   in every route (and would leak connections the moment I forgot a `close()`).
   Routes that don't touch the DB (like `/health`) don't need it.

3. When you restarted the server and your data was still there — how does that feel
   compared to storing data in a Python list? What changed architecturally?

   Honestly it felt like the app suddenly became *real*. In Week 3, every restart
   wiped everything and IDs reset to 1. This time I added Dune, The Hobbit, and
   1984, killed the server, started a brand-new process, called `GET /books`, and
   all three were still there with their original IDs. What changed
   architecturally is that the data no longer lives *inside* the Python process's
   memory — it lives in PostgreSQL, on disk, in its own container. The API became
   *stateless* about data: the server is now just a layer that reads and writes to
   the database, so I can restart it, crash it, or run several copies, and the data
   is unaffected. The list version coupled "the program is running" with "the data
   exists"; the database breaks that coupling.

4. What was the most confusing part of connecting the frontend to the backend?

   Two things. First, the **hostname switch** inside Docker Compose: my `.env` on
   the host connects to `localhost:5432`, but the backend *container* has to reach
   the database at `db:5432` — the service name, not localhost — because inside the
   Compose network "localhost" means the container itself, not the db container.
   Second, **CORS**: the request worked fine from `/docs` and from `curl`, so it
   wasn't obvious why a browser on a different port would be treated differently
   until I understood that the browser is the one enforcing it.

5. When does CORS become a problem and why? In your own words.

   CORS becomes a problem the moment the browser page and the API live on different
   *origins* — and an origin is the combination of protocol + host + port. My
   frontend runs on `http://localhost:3000` and my backend on
   `http://localhost:8000`; even though both are "localhost," the different port
   makes them different origins. For security, the browser blocks JavaScript from
   reading responses from another origin *unless that server explicitly says it's
   allowed*. So the server has to send back headers like
   `Access-Control-Allow-Origin: http://localhost:3000`, which is exactly what the
   `CORSMiddleware` does. The key insight is that CORS is enforced by the *browser*,
   not the server — that's why `curl` and Swagger never complained, but a fetch from
   the React app would have been blocked without the middleware.

6. What is the difference between `useEffect` with `[]` and without it?

   The second argument to `useEffect` is the dependency array, and it controls
   *when* the effect re-runs. With an empty array `[]`, the effect runs **once**,
   right after the component first mounts, and never again — that's the right place
   to fetch the initial list of books from the API. With **no** array at all, the
   effect runs after *every* render, which for a data fetch is dangerous: each fetch
   can trigger a state update, which triggers a re-render, which triggers the effect
   again — an infinite loop. (And the in-between case, `[something]`, re-runs the
   effect only when that value changes.) So `[]` = "on mount only," no array =
   "after every render."
