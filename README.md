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
