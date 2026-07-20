```js
/**
 * Run `fn`, retrying if it throws.
 *
 * `retry` calls `fn` and returns its result. If the call throws, it waits
 * `delay` seconds and tries again, up to `attempts` calls in total. When
 * every attempt fails, it throws the error from the last one. The wait is
 * the same after every failure; there is no backoff.
 *
 * @param {Function} fn        The operation to run. It must be safe to run
 *                             more than once, since every retry repeats
 *                             whatever the earlier attempts already did.
 * @param {number}   attempts  Maximum number of calls, counting the first.
 * @param {number}   delay     Seconds to wait after each failed call.
 * @returns The value returned by the first call that succeeds.
 * @throws The error from the final call, when all attempts fail.
 */
```

Use `retry` for operations that fail transiently and succeed on another try: a network request during a deploy, a file another process is still writing, a service that is starting up. Pick `attempts` and `delay` to match the failure you expect. Three attempts with a two-second delay covers a brief blip; anything that outlasts that deserves to surface as an error.

```js
const config = retry(fetchRemoteConfig, 3, 2);
```

Two cautions. Because `retry` repeats the whole operation, `fn` must tolerate running more than once — retrying a payment is not the same as retrying a read. And retries make real failures slower, not rarer. If the call can never succeed, `retry` spends every attempt and every delay before the error reaches you. When a failure is deterministic, let it fail once.
