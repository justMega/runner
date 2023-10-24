import argparse
import subprocess 
import os
import time
import multiprocessing

def compileCpp(programName, program):
    # Command to compile the C++ program 
    compileArr = ["g++ -std=c++20 -o", programName, program]
    compileCmd = " ".join(str(x) for x in compileArr)
    # Compile the C++ program 
    compileProcess = subprocess.run(compileCmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    # Check if the compilation was not successful 
    if compileProcess.returncode != 0:
        # Print the compilation error messages 
        print("Compilation failed.") 
        print(compileProcess.stderr.decode())
        exit(1)
    print("Compilation successful.") 
    return compileProcess

def getFiles(testFolder, fileExtension):
    out = dict() 
    for file in os.listdir(testFolder):
        if file.endswith(fileExtension):
            numb = ''.join(c for c in file if c.isdigit())
            if numb[0] == "0":
                numb = numb[1:]
            numb = int(numb)
            out[numb] = file 
    return out

def runFunc(inData, program):
    runProcess = subprocess.run(f"./{program}", input=bytes(inData, "utf-8") ,stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output = runProcess.stdout.decode() 
    return output

def runFuncFile(testName, testNumb, resName, testFolder, program):
    inF = open(testFolder +"/"+ testName, "rb")
    inFile = inF.read()
    startTime = time.time()
    # Run the compiled program 
    # Command to execute the compiled program 
    runProcess = subprocess.run(f"./{program}", input=inFile ,stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    timeDelta = time.time()-startTime
    inF.close()

    # Get the output and error messages from the program 
    output = runProcess.stdout.decode()
    error = runProcess.stderr.decode() 
     
    # Print the output and error messages
    outF = open(testFolder +"/"+resName)
    resFile = outF.read().strip()
    outF.close()
    outStr = str(testNumb)+"."
    if output.strip() == resFile:
        print(f"\033[1;32m{outStr:<15} [*] {timeDelta:.6f}\033[0;0m")
    else:
        print(f"\033[1;31m{outStr:<15} [X] {timeDelta:.6f}\033[0;0m")
        print(output)
        print(error)

parser = argparse.ArgumentParser()
parser.add_argument("programName", help="name of the script you want to run ending in .cpp")
parser.add_argument("testFolder", help="folder where the test are located")

parser.add_argument("workingProgram",nargs="?", default=".", help="OPTIONAL (use with -f/--fuzzy only!!) program which is correct ending in .cpp")
parser.add_argument("testGenProgram", nargs="?", default=".", help="OPTIONAL (use with -f/--fuzzy only!!) program that generetes input ending in .py")

parser.add_argument("-f", "--fuzzy", help="enable fuzzy testing", action='store_true')
parser.add_argument("-t", "--timeoutTime", help="define timeout time", type=float)
parser.add_argument("-i", "--interval", help="define interval as x1-x2 or if used with -f/--fuzzy testing just x1",)
args = parser.parse_args()

program = args.programName
programName = (program.split("/")[-1]).replace(".cpp","")
print(programName)
testFolder = args.testFolder

testTime = 2
if args.timeoutTime:
    testTime = args.timeoutTime

compileProcess = compileCpp(programName, program)

if args.fuzzy:
    workingProgram = args.workingProgram
    testGenProgram = args.testGenProgram
    if workingProgram == "." or testGenProgram == ".":
        print("Please list all argument required for fuzzing")
        exit(1)
    workingProgramName = (workingProgram.split("/")[-1]).replace(".cpp","")
    compileProcess = compileCpp(workingProgramName, workingProgram)

    interval = 20
    if args.interval:
        print(args.interval)
        interval = int(args.interval)

    compileWorkingProcess = compileCpp(workingProgramName, workingProgram)
    for i in range(interval):
        runCmd = f"python3 {testGenProgram}"
        runPython = subprocess.run(runCmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        test = runPython.stdout.decode()

        results = runFunc(test, workingProgramName)
        posibleResults = runFunc(test, programName)

        outStr = str(i+1)+"."
        if results.strip() == posibleResults.strip():
            print(f"\033[1;32m{outStr:<15} [*]\033[0;0m")
        else:
            print(f"\033[1;31m{outStr:<15} [X]\033[0;0m")
            fileName = f"fuzzyTest{i+1}.in"
            f = open(fileName, "w")
            print(test)
            f.write(test)

else:
    tests = getFiles(testFolder, ".in")
    results = getFiles(testFolder, ".out")
    testInterval = sorted(tests.keys())

    try:
        if args.interval:
            interval = args.interval.split("-")
            testInterval = range(int(interval[0]), int(interval[1])+1)
    except:        
        print("Parameter not deffined correctly use -h for help")
        exit(1)

    for testNumb in testInterval:
        testName = tests[testNumb]
        resName = results[testNumb]
        
        startTime = time.time()
        p = multiprocessing.Process(target=runFuncFile, name="runFunc", args=(testName, testNumb,resName, testFolder, programName))
        p.start() 
        while p.is_alive() and time.time() - startTime <= testTime:
            pass
        if p.is_alive():
            outStr = str(testNumb)+"."
            print(f"\033[1;35m{outStr:<15} [T]\033[0;0m")
        p.terminate()
        p.join()
        
