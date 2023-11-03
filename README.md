# evolutionary-gpt-agent

## Database
**Create a new migration**

```bash
python devc.py new-migration <name>
```

**Run newest migratino**

```bash
python devc.py upgrade
```


**Undo last migration**
```bash
python downgrade
```

## Deps
```bash
python3.10 -m venv .venv
source .venv/bin/activate
pip3.10 install .
```

### Pre-commit
```
pre-commit install ".[pre-commit]"
```

### Dev
```
pre-commit install ".[dev]"
```
