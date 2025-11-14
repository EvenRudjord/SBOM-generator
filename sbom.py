import json
import os
import sys
import csv

if len(sys.argv) != 2: #Check for correct number of arguments
    print("You need to provide one argument - the path to the directory you want to scan")
    sys.exit(1)

inputen = sys.argv[1] #Path to the directory to scan
numberOfRepositories = 0

if not os.path.isdir(inputen): #Check if the provided path is a valid directory
    print(f"Error: {inputen} is not a valid directory")
    sys.exit(1)
    
all_data = []

def checkForPackages(thePath):  #Checks for package files in the given path
    global numberOfRepositories
    filesInPath = os.listdir(thePath)
    if "requirements.txt" in filesInPath or "package.json" in filesInPath:
        numberOfRepositories += 1
        if "requirements.txt" in filesInPath:
            all_data.extend(getSBOMData(os.path.join(thePath, "requirements.txt"), "pip"))
        if "package.json" in filesInPath:
            all_data.extend(getSBOMData(os.path.join(thePath, "package.json"), "npm"))
    if "package-lock.json" in filesInPath:
        all_data.extend(getSBOMData(os.path.join(thePath, "package-lock.json"), "npm-lock"))
    

def checkDownwardsInFile(newPath): #Recursively checks directories for package files
    checkForPackages(newPath)
    for fil in os.listdir(newPath):
        underFilePath = os.path.join(newPath, fil)
        if os.path.isdir(underFilePath): #Checks if it is a directory
            checkDownwardsInFile(underFilePath)

def getSBOMData(fileName, type): #Saves the SBOM data from the given file
    data = []
    if type == "pip":
        with open(fileName, "r", encoding="utf-8") as fil:
            linjer = fil.readlines()
            
            for linje in linjer:
                linje = linje.strip()
                if not linje or linje.startswith("#"): #Skipping empty lines and comments
                    continue
                for operator in ["==", ">=", "~=", "<=", "<", ">"]: #Removing version specifiers
                    if operator in linje:
                        parts = linje.split(operator, 1)
                        name = parts[0].strip()
                        version = parts[1].strip()
                        break
                else: #If no operator is found
                    name = linje
                    version = "unknown"
        
                data.append({ #Adding package data to the list
                    "name": name,
                    "version": version,
                    "type": type,
                    "path": os.path.abspath(fileName)
                })

    elif type == "npm":
        with open(fileName, "r", encoding="utf-8") as fil:
            filData = json.load(fil) #Loading JSON data from package.json
            
            for dep_type in ["dependencies", "devDependencies"]: #Checking both dependencies and devDependencies
                for name, version in filData.get(dep_type, {}).items(): #Iterating through each dependency
                    if version:
                        version = version.lstrip("^~<>=")
                    
                    data.append({
                        "name": name,
                        "version": version,
                        "type": type,
                        "path": os.path.abspath(fileName)
                    })

    elif type == "npm-lock": #Processing package-lock.json
        with open(fileName, "r", encoding="utf-8") as fil:
            lock_data = json.load(fil)
            packages = lock_data.get("packages", {}) #Getting the packages section

            for package_path, package_info in packages.items(): #Iterating through each package
                name = package_info.get("name") or package_path #Using package path as name if name is not available
                version = package_info.get("version")

                if name and version:
                    version = version.lstrip("^~<>=")
                    data.append({
                        "name": name,
                        "version": version,
                        "type": type,
                        "path": os.path.abspath(fileName)
                    })  

    return data #Returning the collected package data

checkDownwardsInFile(inputen)

json_path = os.path.join(inputen, "sbom.json") #Saving SBOM data to sbom.json
with open(json_path, "w") as newSBOM:
        json.dump(all_data, newSBOM, indent=4)

csv_path = os.path.join(inputen, "sbom.csv")
with open(csv_path, "w", newline='', encoding="utf-8") as csvfile: #Saving SBOM data to sbom.csv
    fieldNames = ["name", "version", "type", "path"]
    writer = csv.DictWriter(csvfile, fieldnames=fieldNames)

    writer.writeheader() 
    for row in all_data:
        writer.writerow(row)

if all_data: #Printing summary information
    print(f"Found {numberOfRepositories} repositories in {inputen}")
    print(f"SBOM files saved as sbom.json and sbom.csv in {inputen}")
else:
    print("No dependencies found in the given directory.")


    

        