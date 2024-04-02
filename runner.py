import argparse
import subprocess 
import os
import time
from enum import StrEnum

class ProgramType(StrEnum):
    NoLanguage = "noLanguage"
    Cpp = ".cpp"
    Java = ".java"
    Python = ".py"
    Out = ".out"

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

def compileProgram(programName, program, lang):
    compileProcess = None
    match lang:
        case ProgramType.Cpp: 
            # Command to compile the C++ program 
            compileArr = ["g++ -std=c++20 -o", programName, program]
            compileCmd = " ".join(str(x) for x in compileArr)
            # Compile the C++ program 
            compileProcess = subprocess.run(compileCmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        case ProgramType.Java:
            # Command to compile the java program 
            compileArr = ["javac", program]
            compileCmd = " ".join(str(x) for x in compileArr)
            compileProcess = subprocess.run(compileCmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        case _:
            print("Language not supported, plese check your program")
            return

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

def runFunc(lang, inData, program):
    match lang:
        case ProgramType.Cpp | ProgramType.Out:
            runProcess = subprocess.run(f"./{program}", input=bytes(inData, "utf-8") ,stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            return runProcess.stdout.decode() 
        case ProgramType.Java:
            runProcess = subprocess.run(f"java {program}", input=bytes(inData, "utf-8") ,stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            return runProcess.stdout.decode() 
        case ProgramType.Python:
            runCmd = f"python3 {workingProgramName}"
            workingPy = subprocess.run(runCmd, input=bytes(inData, "utf-8"), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
            return workingPy.stdout.decode()
        case _:
            raise Exception("Language not supported, plese check your program")

def runFuncFile(lang, testName, testNumb, resName, testFolder, program, doPrint, testTime):
    inF = open(testFolder +"/"+ testName, "rb")
    inFile = inF.read()
    startTime = time.time()
    # Run the compiled program 
    # Command to execute the compiled program
    try:
        runProcess = None
        match lang:
            case ProgramType.Cpp:
                runProcess = subprocess.run(f"./{program}", input=inFile ,stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, timeout=testTime)
            case ProgramType.Java:
                runProcess = subprocess.run(f"java {program}", input=inFile ,stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, timeout=testTime)
            case _:
                raise Exception("Language not supported, plese check your program")
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

def getLangType(program):
    lang = ProgramType.NoLanguage
    if ".cpp" in program:
        lang = ProgramType.Cpp
    elif ".py" in program:  
        lang = ProgramType.Python
    elif ".java" in program or ".class" in program:
        lang = ProgramType.Java
    elif "." not in program or ".out" in program:
        lang = ProgramType.Out
    return lang

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
testFolder = args.testFolder

testTime = 2
if args.timeoutTime:
    testTime = args.timeoutTime

programName = (program.split("/")[-1]).replace(".cpp","").replace(".java", "")
print(programName)
lang = getLangType(program)
compileProcess = compileProgram(programName, program, lang)

if args.fuzzy:
    # so initialize fuzzy testing 
    # NOTE: to self we have alredy compiled the user program outside the if statement
    workingProgram = args.workingProgram
    testGenProgram = args.testGenProgram
    if workingProgram == "." or testGenProgram == ".":
        print("Please list all argument required for fuzzing")
        exit(1)
    
    # determin the type of working program and shorten the name if needed
    workingProgramName = workingProgram
    worklang = getLangType(workingProgram)
    if not args.noCompile:
        workingProgramName = (workingProgram.split("/")[-1]).replace(".cpp","").replace(".java", "")

    # set interval
    interval = 20
    if args.interval:
        print(args.interval)
        interval = int(args.interval)

    for i in range(interval):
        # firt generate test input
        runCmd = f"python3 {testGenProgram}"
        runPython = subprocess.run(runCmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        test = runPython.stdout.decode()

        # run the test on the known working program and time it
        startTime = time.time()
        results = runFunc(worklang, test, workingProgramName)
        workingDeltaTime = time.time() - startTime

        # run the test on the user program and time it
        startTime = time.time()
        posibleResults = runFunc(lang, test, programName)
        myDeltaTime = time.time() - startTime

        # compare the results and print the result
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
    # first we read the test and results folders
    tests = getFiles(testFolder, ".in")
    results = getFiles(testFolder, ".out")
    testInterval = sorted(tests.keys())

    try:
        # set interval
        if args.interval:
            interval = args.interval.split("-")
            testInterval = range(int(interval[0]), int(interval[1])+1)
    except:        
        print("Parameter not deffined correctly use -h for help")
        exit(1)

    # run the tests for each test in interval
    for testNumb in testInterval:
        testName = tests[testNumb]
        resName = results[testNumb]
        
        noPrint = False
        if args.noPrint:
            noPrint = True

        runFuncFile(lang, testName, testNumb,resName, testFolder, programName, noPrint, testTime)


        
