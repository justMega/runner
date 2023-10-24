import argparse
import subprocess 

def runFunc(inData, program):
    runProcess = subprocess.run(f"./{program}", input=bytes(inData, "utf-8") ,stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    output = runProcess.stdout.decode() 
    return output

def compileCpp(programName, program):
    # Command to compile the C++ program 
    compileArr = ["g++ -std=c++20 -o", programName, program]
    compileCmd = " ".join(str(x) for x in compileArr)
    # Compile the C++ program 
    return subprocess.run(compileCmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)

parser = argparse.ArgumentParser()
parser.add_argument("programName", help="name of the script you want to run ending in .cpp")
parser.add_argument("workingProgram", help="program which is correct ending in .cpp")
parser.add_argument("testGenProgram", help="program that generetes input ending in .py")
parser.add_argument("-t", "--timeoutTime", help="define timeout time", type=float)
parser.add_argument("-i", "--interval", help="define test amout", type=int)
args = parser.parse_args()

program = args.programName
programName = (program.split("/")[-1]).replace(".cpp","")
workingProgram = args.workingProgram
workingProgramName = (workingProgram.split("/")[-1]).replace(".cpp","")
testGenProgram = args.testGenProgram

testTime = 2
if args.timeoutTime:
    testTime = args.timeoutTime

interval = 20
if args.interval:
    print(args.interval)
    interval = args.interval

compileProcess = compileCpp(programName, program)
compileWorkingProcess = compileCpp(workingProgramName, workingProgram)

# Check if the compilation was not successful 
if compileProcess.returncode != 0 or compileWorkingProcess.returncode != 0:
    # Print the compilation error messages 
    print("Compilation failed.") 
    exit(1)

print("Compilation successful.")

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

    
