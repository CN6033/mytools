#!/usr/bin/env python

# Function: scan and find conflict classes between jar packages for maven project
# Usage: python scanner.py $YOUR_PROJECT_ROOT_PATH
# For example: python scanner.py /Users/huangshitao/Workspaces/waimai_service_parttime_server

import sys
import os
import commands

def main(libPath):
    classJarMapping = {}
    libs = getLibs(libPath)
    for lib in libs:
        # print "scanning {0} ...".format(lib)
        libClasses = getLibClasses(lib)
        if ".war" in lib:
            scanWarClasses(lib, libClasses, classJarMapping)
        else: # .jar
            scanJarClasses(lib, libClasses, classJarMapping)
    conflictClassJarMapping = getConflictClasses(classJarMapping)
    jarClassMapping = transferToJarClassMapping(conflictClassJarMapping)
    output(jarClassMapping)

def getLibClasses(libPath):
    statusAndOutput = commands.getstatusoutput('jar tf {0} | grep ".class$"'.format(libPath))
    output = statusAndOutput[1]
    return output.split('\n')

def scanWarClasses(libPath, warClasses, classJarMapping):
    MAGIC_PREFIX = 'WEB-INF/classes/'
    for warClass in warClasses:
        clz = warClass[len(MAGIC_PREFIX): len(warClass)]
        simpleWarPath = os.path.basename(os.path.normpath(libPath))
        if (clz not in classJarMapping):
            classJarMapping[clz] = []
        classJarMapping[clz] = [simpleWarPath]
    return classJarMapping

def getLibs(libPath):
    statusAndOutput = commands.getstatusoutput('ls .scanner_work_space')
    output = statusAndOutput[1]
    return map(lambda x: ".scanner_work_space/" + x, output.split('\n'))

def scanJarClasses(libPath, warClasses, classJarMapping):
    for warClass in warClasses:
        simpleWarPath = os.path.basename(os.path.normpath(libPath))
        if (warClass not in classJarMapping):
            classJarMapping[warClass] = []
        classJarMapping[warClass].append(simpleWarPath)
    return classJarMapping

def getConflictClasses(classJarMapping):
    conflictClassJarMapping = {}
    for k, v in classJarMapping.iteritems():
        if len(v) > 1:
            conflictClassJarMapping[k] = v
    return conflictClassJarMapping

def transferToJarClassMapping(classJarMapping):
    jarClassMapping = {}
    for k, v in classJarMapping.iteritems():
        jarPairs = getJarPairs(v)
        for jarPair in jarPairs:
            if jarPair not in jarClassMapping:
                jarClassMapping[jarPair] = []
            jarClassMapping[jarPair].append(k)
    return jarClassMapping

def getJarPairs(jars):
    pairs = []
    for i in range(len(jars)):
        for j in range(i+1, len(jars)):
            if cmp(jars[i], jars[j]) > 0:
                pairs.append(jars[j] + " -- " + jars[i])
            elif cmp(jars[i], jars[j]) < 0:
                pairs.append(jars[i] + " -- " + jars[j])
            else:
                continue
    return pairs

def output(jarClassMapping):
    for k, v in jarClassMapping.iteritems():
        print(k + " [total: {0}]".format(len(v)))
        for i in range(min(10, len(v))):
            print("    " + v[i])

def preprocess(workspace):
    # print "preprocess ..."
    os.chdir("{0}".format(workspace))
    commands.getstatusoutput('rm -rf .scanner_work_space')
    commands.getstatusoutput('mkdir -p .scanner_work_space')
    # print "package ..."
    commands.getstatusoutput('mvn -U clean dependency:copy-dependencies -DoutputDirectory=.scanner_work_space package')
    commands.getstatusoutput('cp -v ./target/*.?ar .scanner_work_space')

if __name__ == '__main__':
    preprocess(sys.argv[1])
    main(sys.argv[1])
