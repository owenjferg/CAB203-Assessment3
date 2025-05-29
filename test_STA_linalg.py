import os
import ast
import unittest
from inspect import getsource
import sys

import specialtopics as ST

scriptDirectory = os.path.dirname(__file__)
allowed_modules =  [ "csv", "probability", "numpy", "re", "itertools", "functools" ]

tolerance = 0.01

def closeEnough(s, a, b):
    if abs(a - b) > tolerance:
        s.fail(f"Amounts differ.  Expected: {a} Got {b}")


def closeEnoughDict(s, a, b):
    if set(a.keys()) != set(b.keys()):
        s.fail(f"Dictionaries don't have the same keys.\nExpected: {a}\nGot: {b}")

    r = all(abs(a[k] - b[k]) <= tolerance for k in a.keys())
    if not r:
        s.fail(f"Dictionaries have different values.\nExpected: {a}\nGot: {b}")


class TestLinearAlgebra(unittest.TestCase):
    def test_no_loops(self):
        """No loops"""
        assert_no_loops(self, ST.blendWheat)

    def run_for_csvfile(self, csvfilename, correctDict, correctAmount):
        rDict, rAmount = ST.blendWheat(csvfilename)

        closeEnoughDict(self, correctDict, rDict)
        closeEnough(self, correctAmount, rAmount)

    def test_bins1(self):
        self.run_for_csvfile("bins1.csv", {"A": 12.0, "B": 10.29, "C": 3.43}, 25.71)

    def test_bins2(self):
        self.run_for_csvfile("bins2.csv", {'Big one': 7.0, 'One beside the big one': 8.17, 'Old one': 2.33}, 17.5)
    
    def test_bins3(self):
        self.run_for_csvfile("bins3.csv", {'A': 17.5, 'B': 15.0, 'C': 5.0}, 37.5)

    def test_bins4(self):
        self.run_for_csvfile("bins4.csv", {'A': 14.0, 'B': 12.0, 'C': 4.0}, 30.0)

    def test_bins5(self):
        self.run_for_csvfile("bins5.csv", {'A': 7.5, 'B': 15.0, 'C': 0.0}, 22.5)

    def test_bins6(self):
        self.run_for_csvfile("bins6.csv", {'A': 3.5, 'B': 3.5, 'C': 7.0}, 14.0)

    def test_bins7(self):
        self.run_for_csvfile("bins7.csv", {'A': 22.0, 'B': 8.25, 'C': 2.75}, 33.0)

    def test_bins8(self):
        self.run_for_csvfile("bins8.csv", {'Bravo': 5.5, 'Charlie': 0.0, 'Alpha': 22.0}, 27.5)

    def test_bins9(self):
        self.run_for_csvfile("bins9.csv",  {'Top': 9.33, 'Middle': 2.67, 'Bottom': 4.0}, 16.0)



def calls(startNode):
    '''Find function calls in an AST'''
    return {
        node.func.id if isinstance(node.func, ast.Name) else node.func.attr
        for node in ast.walk(startNode)
        if isinstance(node, ast.Call)
    }

def hasLoop(startNode):
    '''Find For and While loops in an AST.'''
    return any( 
        isinstance(node, ast.For) or
        isinstance(node, ast.While)
        for node in ast.walk(startNode)
    )

def functionsWithLoopsR(F=None, functionNodes=None):
    '''Look for functions that have a loop themselves or that depend on a function that has a loop.
    
    This code doesn't understand scopes, so it can't distinguish between functions from different scopes
    that have the same name.  So it can produce a false positive in such cases.
    '''
    
    # base case: functions that have loops in their body
    if F is None:
        syntaxTree = ast.walk(ast.parse(getsource(ST)))
        functionNodes = { node for node in syntaxTree if isinstance(node, ast.FunctionDef) }
        F = { node.name for node in functionNodes if hasLoop(node) }

    # Functions that call something in F, but aren't themselves in F yet
    callersOfF = { 
        node.name
        for node in functionNodes
        if node.name not in F and 
        not calls(node).isdisjoint(F)
    }

    if not callersOfF: return F
    
    return functionsWithLoopsR(F | callersOfF, functionNodes)

functionsWithLoops = functionsWithLoopsR()

def assert_no_loops(self, f):
    if f.__name__ in functionsWithLoops:
        self.fail(f'function {f.__name__} uses a loop.')
    
# This test does not count for any marks.  It just helps to ensure
# that your code will run on the test system.
class TestImportedModules(unittest.TestCase):
   def test_modules(self):
      with open('specialtopics.py', "r") as f:
         file_raw = f.read()
         player_ast = ast.parse(file_raw)

      def imported_modules():
         for node in ast.walk(player_ast):
               if isinstance(node, ast.Import):
                  yield from (x.name.split('.')[0] for x in node.names)
               if isinstance(node, ast.ImportFrom) and node.level == 0:
                  yield node.module.split('.')[0]

      for module in imported_modules():
         if module not in allowed_modules:
               self.fail(f'module {module} imported by submission but not allowed.')




if __name__ == "__main__":
    print(f"Python version {sys.version}")
    unittest.main(argv=["-b"])
