Żeby postawić projekt lokalnie, należy sklonować repozytorium, następnie z poziomu folderu projekty uruchomić komendę, która utworzy wirtualne środowisko:
  python3 -m venv .venv;

  Następnie w przypadku Windowsa:
    activate
  MacOS/Linux:
    source .venv/bin/activate

  Następnie należy zainstalować zależności:
  pip install flask

I po tym można uruchomić stronę na lokal hostcie za pomocą polecenia:
  flask flaskr run
