# CityFlow
Projekt dyplomowy, Akademia Górniczo-Hutnicza im. Stanisława Staszica w Krakowie, 2019/2020

## Temat
Modelowanie i symulacja przepływu powietrza w obszarach zurbanizowanych na przykładzie Krakowa.

### Cel pracy
Celem pracy jest opracowanie uproszczonych modeli przepływu powietrza w obszarach miejskich oraz symulacja przepływu powietrza („przewietrzanie”) z wykorzystaniem danych o topografii i zabudowie terenu. W ramach opracowanych modeli powinien zostać zbadany wpływ zabudowy tzw. „korytarzy przewietrzania” na przepływ powietrza w poszczególnych rejonach miasta i na propagację zanieczyszczeń.

# Instrukcja uruchomienia
Program uruchamia się poleceniem `python cityflow.py <config>`, gdzie <config> to ścieżka do pliku konfiguracyjnego. Jeżeli nic nie zostanie podane jako argument wywołany zostanie domyślny plik konfiguracyjny (config.txt). W projekcie jest już zaimplementowany przykładowy plik konfiguracyjny, po pobraniu projektu wystarczy tylko uruchomić polecenie `python cityflow.py`.

## Plik konfiguracyjny
Wszystkie ustawienia programu definiuje się w pliku konfiguracyjnym.
