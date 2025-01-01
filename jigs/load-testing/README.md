# Load testing

## Conclusion

Single process handles any realistic load the local beauty salon website can produce.
Starlette spawns (and despawns) worker threads in the pool to keep backlog at zero.

## Availability

Endpoint performed at 2.5k RPS maxing out CPU both on Locust and FastAPI sides.
After adding TTLCache with 60 seconds TTL, RPS went up to 3.2k.
The latency is in single digit milliseconds.

No surprises here, the function is heavily cached, and doesn't have any IO on most runs.

## Checkout

This is just a thin wrapper around Stripe's API.
In testing account, checkout session takes 500 ms to create on average.

As the concurency goes up, latency remains flat, as FastAPI (starlette) adds more threads to the server to accomodate all requests without filling backlog.
[Stripe has a rate limit of 25 RPS](https://stripe.com/docs/rate-limits), which kicks in before FastAPI shows any sign of degradation.

This is how rate limit exception looks like:

```
  File ".../site-packages/starlette/routing.py", line 76, in app
    await wrap_app_handling_exceptions(app, request)(scope, receive, send)
  File ".../site-packages/starlette/_exception_handler.py", line 53, in wrapped_app
    raise exc
  File ".../site-packages/starlette/_exception_handler.py", line 42, in wrapped_app
    await app(scope, receive, sender)
  File ".../site-packages/starlette/routing.py", line 73, in app
    response = await f(request)
               ^^^^^^^^^^^^^^^^
  File ".../site-packages/fastapi/routing.py", line 301, in app
    raw_response = await run_endpoint_function(
                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File ".../site-packages/fastapi/routing.py", line 214, in run_endpoint_function
    return await run_in_threadpool(dependant.call, **values)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File ".../site-packages/starlette/concurrency.py", line 39, in run_in_threadpool
    return await anyio.to_thread.run_sync(func, *args)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File ".../site-packages/anyio/to_thread.py", line 56, in run_sync
    return await get_async_backend().run_sync_in_worker_thread(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File ".../site-packages/anyio/_backends/_asyncio.py", line 2505, in run_sync_in_worker_thread
    return await future
           ^^^^^^^^^^^^
  File ".../site-packages/anyio/_backends/_asyncio.py", line 1005, in run
    result = context.run(func, *args)
             ^^^^^^^^^^^^^^^^^^^^^^^^
  File "api/endpoints/payment.py", line 18, in checkout
    session = stripe.checkout.Session.create(
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File ".../site-packages/stripe/checkout/_session.py", line 4475, in create
    cls._static_request(
  File ".../site-packages/stripe/_api_resource.py", line 172, in _static_request
    return _APIRequestor._global_instance().request(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File ".../site-packages/stripe/_api_requestor.py", line 197, in request
    resp = requestor._interpret_response(rbody, rcode, rheaders, api_mode)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File ".../site-packages/stripe/_api_requestor.py", line 853, in _interpret_response
    self.handle_error_response(
  File ".../site-packages/stripe/_api_requestor.py", line 336, in handle_error_response
    raise err
stripe._error.RateLimitError: Request rate limit exceeded.
You can learn more about rate limits here https://stripe.com/docs/rate-limits.
```
