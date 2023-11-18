# Evolutionary GPT Agent

## Database
**Create a new migration**

```bash
python devc.py new-migration <name>
```

**Run newest migration**

```bash
python devc.py upgrade
```


**Undo last migration**
```bash
python downgrade
```

## Frontend
### Hot reloading
When running all services with `docker-compose`, hot reloading is really slow (can take up to 10-20 seconds).
For development, and exploit fully `vite`'s hot reload avoiding using containers is suggested:

- comment `agent_pov` from `docker-compose.yml`
- `cd agent-pov && npm run dev`

## Deps
```bash
python3.10 -m venv .venv
source .venv/bin/activate
pip3.10 install .
```

### Pre-commit
```
pip3.10 install ".[pre-commit]"
pre-commit install
```

### Dev
```
pip3.10 install ".[dev]"
```
