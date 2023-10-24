# runner
Program za avtomatsko testiranje c++ programov. Podpira izbiro intervalov testov in nastavitev timeout časa. Vhodne testne datoteke naj se končajo z ```.in``` datoteke z rezultatom pa z ```.out```, stem da ```testXX.out``` vsebuje rezultat vhoda ```testXX.in```, kjer XX predstavlja število. Vsi testi naj bodo v isti mapi.

Za več infoirmaci ```python3 runner.py -h```

### English
Program for automatic testing of c++ programs. Curently supports setting of test interval and timeout time. Input files shuld end with file extensin ```.in``` and files with result data with ```.out```, also  ```testXX.out``` should contain results from ```testXX.in```, where XX is a number. All tests should be in the same folder.

For more information run ```python3 runner.py -h```
