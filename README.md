## Wymagania

- Python 3.8+
- pip (Python package manager)
- (Opcjonalnie) `virtualenv` lub `venv` do środowisk wirtualnych

## 🔧 Instalacja i uruchomienie projektu

### 1. Sklonuj repozytorium
```
git clone https://github.com/kacperMa25/In-ynieriaOprogramowania.git
cd In-ynieriaOprogramowania/projekt
```
### 2. Postawienie wirtualnego środowiska w Pythonie
## MacOS/Linux
```
python3 -m venv venv
source venv/bin/activate
```

## Windows
```
python -m venv venv
venv\Scripts\activate
```
### 3. Instalowanie zależności
```
pip install flask pytest
```

### 4. Uruchamianie apikacji
```
flask --app flaskr init-db
flask --app flaskr run
```
### 5. Uruchamianie testów
```
python -m pytest tests/testy.py -v
```
