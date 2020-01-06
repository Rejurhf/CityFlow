# CityFlow
Projekt dyplomowy, Akademia Górniczo-Hutnicza im. Stanisława Staszica w Krakowie, 2019/2020

## Temat
Modelowanie i symulacja przepływu powietrza w obszarach zurbanizowanych na przykładzie Krakowa.

### Cel pracy
Celem pracy jest opracowanie uproszczonych modeli przepływu powietrza w obszarach miejskich oraz symulacja przepływu powietrza („przewietrzanie”) z wykorzystaniem danych o topografii i zabudowie terenu. W ramach opracowanych modeli powinien zostać zbadany wpływ zabudowy tzw. „korytarzy przewietrzania” na przepływ powietrza w poszczególnych rejonach miasta i na propagację zanieczyszczeń.

# Instrukcja uruchomienia
Program uruchamia się poleceniem `python cityflow.py <config>`, gdzie <config> to ścieżka do pliku konfiguracyjnego. Jeżeli nic nie zostanie podane jako argument wywołany zostanie domyślny plik konfiguracyjny (config.txt). W projekcie jest już zaimplementowany przykładowy plik konfiguracyjny, po pobraniu projektu wystarczy tylko uruchomić polecenie `python cityflow.py`.

## Moduły potrzebne do uruchomienia
Program pisany był na wersji Pythona 3.7.4

**Potrzebne moduły:**
* json
* sys
* numpy
* math
* shapely
* datetime
* xml
* geopy
* osmium
* matplotlib
* descartes

# Plik konfiguracyjny
Wszystkie ustawienia programu definiuje się w pliku konfiguracyjnym.

![Config](https://github.com/Rejurhf/CityFlow/blob/master/resources/config.png)

**Parametry:**
* `"name"` - nazwa projektu
* `"raydenspermeter"` - ilość promieni na metr, im wyższa wartość, tym wyższa dokładność, ale też wydłużony czas wykonania symulacji
* `"osmmap"` - śnieżka do mapy OSM (w folderze resources znajduje się kilpa przykładowych map). W programie zaimplementowane zostały przypadki testowe, można je uruchomić ustawiając wartość parametru na jedną z poniższych:
  - `"cube"` - pojedynczy prostopadłościan
  - `"cubeRow"` - 2 prostopadłościany w rzędzie
  - `"cubeCol"` - 2 prostopadłościany obok siebie
  - `"cylinder"` - cylinder
* `"visualize"` - lista widoków do wizualizacji. Każdy element skłąda się z 2 części pierwsza to pozycja ("top", "side"), druga to odległość od początku osi współżędnych w metrach ("0", "6"). Przykład poprawnego argumentu: `["top6", "side10", "top0", "side0"]`
* `"outbuildingname"` - nazwa pliku wyjściowego z budynkami
* `"outrayname"` - nazwa pliku wyjściowego z promieniami
* `"savebuildings"` - flaga czy plik z budynkami ma być zapisany, jeżeli `"True"` to tak, każda inna wartość to nie
* `"saverays"` - flaga czy plik z promieniami ma być zapisany, jeżeli `"True"` to tak, każda inna wartość to nie
* `"withoutstraightrays"` - flaga czy w zapisanym pliku powinny znajdować się promienie któe nie napotkały żadnej przeszkody, jeżeli `"True"` to nie pojawią się, każda inna wartość to wszystkie promienie zostaną zapisane
* `"everynray"` - parametr informujący co który promień będzie zapisany, np. jeżeli `2` to co 2 promień będzie zapisany, jeżeli `1` to każdy promień będzie zapisany

# Wizualizacja 3D
Do wizualizacji 3D potrzebny jest program Blender.

Aby przedstawić wizualizację należy uruchomic 2 skrypty `blender\city.py` i `blender\rays.py`. W obu skryptach należy podać ścieżki do wygenerowanych wcześniej plików.

W projekcie są dołączone przykładowe, wcześniej wygenerowane pliki z budynkami i promieniami.

W skrypcie `city.py` należy podać ścieżkę do pliku `building_2.txt`, a w skrypcie `rays.py` należy podać ścieżkę do pliku `ray_2_0.5_2.txt`.
