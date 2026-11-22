# 🎟️ Turnstile

> *Click through. Get counted.*

**Turnstile** is a small visit counter built from three containers managed by Docker Compose. **Nginx** receives each request and passes it to the **Flask** app, which stores the visit count in **Redis**. The pages are styled HTML templates that show your visitor number and which container served you.

**Built with:** 🐍 Python · 🌶️ Flask · 🟥 Redis · 🟩 Nginx · 🐳 Docker Compose

## Architecture

```
        Browser 🌐
           │
  http://localhost:5003
           │
┌──────────┼──────────────── Compose network ──────────────────────┐
│          ▼                                                       │
│   ┌──────────┐  web:5003  ┌─────────────┐  redis:6379  ┌───────┐ │
│   │  nginx   │ ─────────► │ web (Flask) │ ───────────► │ redis │ │
│   └──────────┘            └─────────────┘              └───┬───┘ │
│                                                            │     │
│                                                  💾 redis-data   │
│                                                     (volume)     │
└──────────────────────────────────────────────────────────────────┘
```

- **nginx**: reverse proxy, and the only service published to the host (`5003:5003`)
- **web**: the Flask app; uses `expose`, so only other containers can reach it
- **redis**: stores the `visits` counter in the `redis-data` named volume, so the count survives `docker compose down`

Flask connects using the hostname `redis`. Compose's built-in DNS resolves each **service name** to that container's IP address.

## 📁 Project structure

```
.
├── app.py               # Flask app: / and /count routes
├── templates/
│   ├── base.html        # Shared layout: nav bar, styles, footer
│   ├── home.html        # Landing page
│   └── count.html       # Visitor counter page
├── requirements.txt     # flask, redis
├── Dockerfile           # Flask image
├── nginx.conf           # Reverse proxy config (forwards to web:5003)
├── docker-compose.yml   # Defines and connects all three services
├── .dockerignore        # Keeps venv/ and caches out of the image
└── .gitignore
```

## 🚀 How to run

All you need is [Docker](https://www.docker.com/products/docker-desktop/) with Compose v2.

```bash
git clone https://github.com/Qasim980/turnstile.git
cd turnstile
docker compose up --build   # build and start
docker compose ps           # check all three services are up
docker compose down         # stop and remove (the count is kept in the volume)
```

Then open **http://localhost:5003**.

> 💡 On macOS, container IPs like `172.18.0.x` can't be reached from the browser, because Docker Desktop runs containers inside a Linux VM. Always go through `localhost:5003`, which Nginx publishes.

> 💡 The code is copied into the image at build time, so after editing `app.py` or the templates, run `docker compose up -d --build` to see the change.

## 🔗 Endpoints

| URL | What it does |
|---|---|
| `http://localhost:5003/` | 🏠 Home page explaining how the stack fits together |
| `http://localhost:5003/count` | 🔢 Increments the count and shows your visitor number |

## ✨ App features

- **Styled pages** built from Jinja templates that share one layout (`base.html`), with a dark theme that works on phones
- **Animated visitor number**, plus a line like *"7 people passed through before you."*
- **Container hostname in the footer**: shows which container served the request, which is useful once Flask is scaled to several replicas
- **Friendly error page** if Redis is unreachable, instead of a 500

## 🧠 Key design decisions

- **`INCR` for the counter**: atomic, so the count stays correct across multiple Flask instances
- **Flask binds to `0.0.0.0`**: the default `127.0.0.1` would only accept traffic from inside the container
- **Dependencies installed before the code is copied**: layer caching means editing `app.py` doesn't reinstall packages
- **Redis not published to the host**: it has no password by default, and Flask reaches it internally anyway
- **Nginx in front of Flask**: only the proxy is exposed to the host, which sets up load balancing across several Flask containers later
- **Redis host and port from environment variables** (`REDIS_HOST`, `REDIS_PORT`), set in `docker-compose.yml` instead of hard-coded
- **`build:` instead of `image:`**: Compose rebuilds from source, so code changes get picked up

## 🛠️ What broke and what I learned

| Problem ❌ | Lesson ✅ |
|---|---|
| `redis-server: not found` during build | `RUN` runs at build time and processes don't carry over. Redis gets its own container. |
| `/count` returned **500** | A container started with plain `docker run` sits on the default network, where `redis` doesn't resolve. Use Compose. |
| `address already in use` on port 5000 | macOS AirPlay Receiver holds 5000. Found it with `lsof -i :5000` and moved to 5003. |
| `port is already allocated` on 5003 | An old `docker run` container held the port. `docker compose ps` only shows this project; `docker ps` shows everything. |
| `/count` gave **404**, `/counter` worked | Compose was running an old pre-built image. Switched to `build:` and checked with `docker compose exec web cat app.py`. |
| `version` is obsolete warning | Compose v2 ignores it, so I removed it. |
| `http://172.18.0.3:5003` wouldn't load | That's the container's internal IP. On macOS it isn't reachable from the host; use `localhost:5003` through Nginx. |

## 🗺️ Roadmap

- [x] Persistent Redis storage with a named volume
- [x] Redis connection details from environment variables
- [x] Put Flask behind an Nginx reverse proxy
- [ ] Scale Flask to several replicas and load-balance across them
- [ ] Health checks so Compose waits for Redis before starting Flask
- [ ] Run Flask with a production server (Gunicorn) instead of the dev server

## 📋 Handy commands

```bash
docker compose up -d --build     # rebuild after code changes
docker compose logs web          # logs for one service
docker compose exec web <cmd>    # run a command inside a container
docker ps                        # all running containers
lsof -P -i :<port>               # what's holding a port?
```
