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
