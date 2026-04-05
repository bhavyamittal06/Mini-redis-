# mini-redis

A Redis-like key-value store built from scratch in Python.
Built to understand how real databases work under the hood.

## Features
- TCP server accepting multiple concurrent clients
- GET / SET / DEL commands
- Thread-safe with RLock — no race conditions
- TTL expiry with background cleanup thread
- Persistence (in progress)

## How to run
python3 server.py

## Connect
nc localhost 6379

## Commands
SET key value
GET key
DEL key
EXPIRE key seconds

## Design decisions
- Used RLock over Lock — reentrant, prevents self-deadlock as codebase grows
- One thread per client — simple concurrency model, bottleneck at ~10k connections
- Background cleanup thread sweeps expired keys every second
- What breaks at scale: threading model fails at high connection counts
  → next step would be asyncio with epoll

## What I would build next
- AOF persistence — survive crashes
- Asyncio instead of threading — handle 10k+ connections
- KEYS * pattern matching
- Benchmarking — ops/sec under load
  
### Why RLock over Lock
RLock is reentrant — the same thread can acquire it multiple 
times without deadlocking. As functions call other locking 
functions, RLock prevents accidental self-deadlock.

### Why AOF + Snapshot together
AOF alone = durable but slow recovery on restart.
Snapshot alone = fast recovery but loses up to 30 seconds of data.
Together: load snapshot for bulk restore, replay AOF for 
recent commands. Same approach real Redis uses.

### What breaks at scale
One thread per connection fails at ~10k connections.
Next step: asyncio with epoll — handles 100k+ connections
on a single thread. That's how real Redis does it.

### What I would build next
- KEYS * pattern matching
- Asyncio rewrite for scale
- Replication — master/replica
- Benchmark script — measure ops/sec under load
