import os
import unittest
import coverage
import sys

def runTests(filePattern=None):
    if filePattern is not None:
        tests = unittest.TestLoader().discover('bin/tests/', pattern=filePattern)
    else:
        tests = unittest.TestLoader().discover('bin/tests/')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    return result

def mainOnlyTest(filePattern=None):

    try:
        result = runTests(filePattern)

    except Exception as e:
        print(e, file=sys.stderr)
        return 1

    if result.wasSuccessful():
        return 0
    else:

        return 1

def mainTestWithCoverage():
    """Runs the unit tests with coverage."""

    COV = coverage.coverage(
        branch=False,
        include='bin/*',
        omit=[
            'bin/tests/*',
            'bin/__init__.py'
        ]
    )

    COV.start()

    try:
        
        result = runTests()
        
        if result.wasSuccessful():

            COV.stop()
            COV.save()
            print('Coverage Summary:')
            COV.report()

            basedir = os.path.abspath(os.path.dirname(__file__))
            covdir = os.path.join(basedir, 'tmp/coverage')
            COV.html_report(directory=covdir)
            print('HTML version: file://%s/index.html' % covdir)
            COV.erase()
            return 0
        
        else:

            return 1

    except Exception:

        return 1

    

if __name__ == '__main__':



    if len(sys.argv) > 1:
        if "no_coverage" != sys.argv[1] :
            sys.exit(mainOnlyTest(sys.argv[1]))
        else:
            sys.exit(mainOnlyTest())
        
    else:
        sys.exit(mainTestWithCoverage())