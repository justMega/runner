import argparse
import subprocess 
import os
import time

def compareOutput(myres, correctres):
    if "$#%" not in correctres:
        return myres == correctres
    beginres, endres = correctres.split("$#%")
    endres.replace("%#$", "")
    if myres[:len(beginres)] == beginres:
        for vr in endres.splitlines():
            if myres[len(beginres):] == vr.strip():
                return True
    return False

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
            if len(numb) == 0:
                continue
            if numb[0] == "0":
                numb = numb[1:]
            numb = int(numb)
            out[numb] = file 
    return out

def runFunc(inData, program):
    runProcess = subprocess.run(f"./{program}", input=bytes(inData, "utf-8") ,stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output = runProcess.stdout.decode() 
    return output

def runFuncFile(testName, testNumb, resName, testFolder, program, doPrint, testTime):
    inF = open(testFolder +"/"+ testName, "rb")
    inFile = inF.read()
    startTime = time.time()
    # Run the compiled program 
    # Command to execute the compiled program
    try:
        runProcess = subprocess.run(f"./{program}", input=inFile ,stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, timeout=testTime)
        timeDelta = time.time()-startTime
        # Get the output and error messages from the program
        output = runProcess.stdout.decode()
        error = runProcess.stderr.decode()

        # Print the output and error messages
        outF = open(testFolder +"/"+resName)
        resFile = outF.read().strip()
        outF.close()
        outStr = str(testNumb)+"."
        if compareOutput(output.strip(),resFile):
            print(f"\033[1;32m{outStr:<15} [*] {timeDelta:.6f}\033[0;0m")
        else:
            print(f"\033[1;31m{outStr:<15} [X] {timeDelta:.6f}\033[0;0m")
            if not noPrint:
                print(output)
            print(error)
    except subprocess.TimeoutExpired:
        outStr = str(testNumb)+"."
        print(f"\033[1;35m{outStr:<15} [T]\033[0;0m")
    inF.close()

def saveTest(name):
    f = open(name, "w")
    f.write(test)

parser = argparse.ArgumentParser()
parser.add_argument("programName", help="name of the script you want to run ending in .cpp")
parser.add_argument("testFolder", help="folder where the test are located")

parser.add_argument("workingProgram",nargs="?", default=".", help="OPTIONAL (use with -f/--fuzzy only!!) program which is correct ending in .cpp")
parser.add_argument("testGenProgram", nargs="?", default=".", help="OPTIONAL (use with -f/--fuzzy only!!) program that generetes input ending in .py")

parser.add_argument("-f", "--fuzzy", help="enable fuzzy testing", action='store_true')
parser.add_argument("-no", "--noPrint", help="dissable printing of wrong outputs", action='store_true')
parser.add_argument("-nc", "--noCompile", help="when used with -f/--fuzzy allows the use of precompiled working program", action='store_true')
parser.add_argument("-t", "--timeoutTime", help="define timeout time", type=float)
parser.add_argument("-i", "--interval", help="define interval as x1-x2 or if used with -f/--fuzzy just x1",)
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
    
    isPython = False
    workingProgramName = workingProgram
    if not args.noCompile:
        if ".py" in workingProgramName:
            isPython = True
            print("is python")
        else:
            workingProgramName = (workingProgram.split("/")[-1]).replace(".cpp","")
            compileProcess = compileCpp(workingProgramName, workingProgram)

    interval = 20
    if args.interval:
        print(args.interval)
        interval = int(args.interval)

    #compileWorkingProcess = compileCpp(workingProgramName, workingProgram)
    for i in range(interval):
        runCmd = f"python3 {testGenProgram}"
        runPython = subprocess.run(runCmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        test = runPython.stdout.decode()

        startTime = time.time()
        results = ""
        if not isPython:
            results = runFunc(test, workingProgramName)
        else:
            runCmd = f"python3 {workingProgramName}"
            workingPy = subprocess.run(runCmd, input=bytes(test, "utf-8"), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            results = workingPy.stdout.decode()
        workingDeltaTime = time.time() - startTime

        startTime = time.time()
        posibleResults = runFunc(test, programName)
        myDeltaTime = time.time() - startTime

        outStr = str(i+1)+"."
        if compareOutput(results.strip(),posibleResults.strip()):
            print(f"\033[1;32m{outStr:<15} [*] your time: {myDeltaTime:.6f}, compered to {workingDeltaTime:.6f}\033[0;0m")
            if myDeltaTime >= testTime:
                fileName = f"{testFolder}/timeOutTest{i+1}.in"
                saveTest(fileName)
        else:
            print(f"\033[1;31m{outStr:<15} [X]\033[0;0m")
            fileName = f"{testFolder}/fuzzyTest{i+1}.in"
            saveTest(fileName)
            print(runPython.stderr.decode())
            print(test)


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
        
        noPrint = False
        if args.noPrint:
            noPrint = True

        runFuncFile(testName, testNumb,resName, testFolder, programName, noPrint, testTime)


        
