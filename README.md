# runner
Program za avtomatsko testiranje c++/java programov. Podpira izbiro intervalov testov in nastavitev timeout časa. Vhodne testne datoteke naj se končajo z ```.in``` datoteke z rezultatom pa z ```.out```, stem da ```testXX.out``` vsebuje rezultat vhoda ```testXX.in```, kjer XX predstavlja število. Vsi testi naj bodo v isti mapi.

Podpira tudi fuzzy testing, in sicer kot ```python3 runner.py programName.cpp testFolder workingProgram testGenerator.py -f```, kjer se ```workingProgram``` konča na ```.cpp``` ali na ```.py```, z opcijo ```-nc```/```--noCompile``` pa omogoča uporbo že comilane verzije ```workingProgram```. Program bo podal vhodne podate, ki jih generira ```testGenerator.py``` tako ```workingProgram``` in ```programName.cpp``` in primerjal njume izhode v primeru razlik pa zapisal vhod kot ```FailedTestXX.in``` v mapo ```testFolder```. Vhod bo tudi zapisal v ```timeOutTestXX.in``` v primeru da ```programName.cpp``` porabi več kot timeout čas za rešitev testa.

Za več infoirmaci ```python3 runner.py -h```

### English
Program for automatic testing of c++/java programs. Curently supports setting of test interval and timeout time. Input files shuld end with file extensin ```.in``` and files with result data with ```.out```, also  ```testXX.out``` should contain results from ```testXX.in```, where XX is a number. All tests should be in the same folder.

It also supports fuzzy testing, as ```python3 runner.py programName.cpp testFolder workingProgram testGenerator.py -f```, where ```workingProgram``` ends in ```.cpp``` or ```.py```, the option ```-nc```/```--noCompile``` allows to use the already compiled version of ```workingProgram```. The program will provide the input data generated by ```testGenerator.py``` to both ```workingProgram``` and ```programName.cpp``` and compare their outputs in case of differences it will write the input as ```FailedTestXX.in``` to the ```testFolder``` folder. It will also save the input to ```timeOutTestXX.in``` in case that the ```programName.cpp``` takes more than timeout time to solve the test.

For more information run ```python3 runner.py -h```
