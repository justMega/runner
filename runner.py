import sys
import subprocess 
import os
import time
import multiprocessing

def getTests(testFolder):
    files = os.listdir(testFolder)
    tests = dict()
    results = dict()
    for file in files:
        if not "." in file:
            continue

        fType = file.split(".")[1]
        if fType != "in" and fType != "out":
            continue

        numb = file.split(".")[0].replace("test", "")
        if numb[0] == "0":
            numb = numb[1:]
        numb = int(numb)

        if fType == "in":
            tests[numb] = file
        elif fType == "out":
            results[numb] = file
    
    return (tests, results)

def runFunc(testName, resName,testFolder):
    inF = open(testFolder +"/"+ testName, "rb")
    inFile = inF.read()
    startTime = time.time()
    runProcess = subprocess.run(f"./{programName}", input=inFile ,stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    timeDelta = time.time()-startTime
    inF.close()

    # Get the output and error messages from the program 
    output = runProcess.stdout.decode()
    error = runProcess.stderr.decode() 
     
    # Print the output and error messages
    outF = open(resName)
    resFile = outF.read().strip()
    outF.close()
    outStr = str(testNumb)+"."
    if output.strip() == resFile:
        print(f"\033[1;32m{outStr:<15} [*] {timeDelta:.6f}\033[0;0m")
    else:
        print(f"\033[1;31m{outStr:<15} [X] {timeDelta:.6f}\033[0;0m")
        print(output)
        print(error)

if len(sys.argv) <= 1:
    print("Not enought parameters, for help run -h \n")
    exit(1)
firstArg = str(sys.argv[1])
if firstArg == "-h":
    print("""To run program type: python3 runner.py programName testFolder -i Y1-Y2 -t TT
input test should be named testXX.in results should be named testXX.out, XX is test number
-i Y1-Y2 are optinal parameters deffining a close interval of tests you want to run 
-t TT optinal parameter for max exceqution time""")
    exit(1)


program = firstArg 
programName = program.split(".")[0]
testFolder = str(sys.argv[2])

# Command to compile the C++ program 
compileArr = ["g++ -std=c++20 -o", programName, program]
compileCmd = " ".join(str(x) for x in compileArr)
# Compile the C++ program 
compileProcess = subprocess.run(compileCmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

# Check if the compilation was successful 
if compileProcess.returncode == 0: 
    print("Compilation successful.") 
    # Run the compiled program 
    # Command to execute the compiled program 
    (tests, results) = getTests(testFolder)
    testInterval = sorted(tests.keys())
    testTime = 2
    if len(sys.argv) == 5 or len(sys.argv) == 7:
        interval = None
        tempTime = None
        if sys.argv[3] == "-i":
            interval = sys.argv[4]
        elif len(sys.argv) == 7 and sys.argv[5] == "-i":
            interval = sys.argv[6]
        if sys.argv[3] == "-t":
            tempTime = sys.argv[4]
        elif len(sys.argv) == 7 and sys.argv[5] == "-t":
            tempTime = sys.argv[6]
        
        try:
            if interval != None:
                interval = interval.split("-")
                testInterval = range(int(interval[0]), int(interval[1])+1)
            if tempTime != None:
                testTime = float(tempTime)
        except:        
            print("Parameter not deffined correctly use -h for help")
            exit(1)

    for testNumb in testInterval:
        testName = tests[testNumb]
        resName = results[testNumb]
        
        startTime = time.time()
        p = multiprocessing.Process(target=runFunc, name="runFunc", args=(testName, resName, testFolder))
        p.start() 
        while p.is_alive() and time.time() - startTime <= testTime:
            pass
        if p.is_alive():
            outStr = str(testNumb)+"."
            print(f"\033[1;35m{outStr:<15} [T]\033[0;0m")
        p.terminate()
        p.join()
        
else: 
    # Print the compilation error messages 
    print("Compilation failed.") 
    print(compileProcess.stderr.decode()) 
