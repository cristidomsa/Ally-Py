'''
Created on Jan 9, 2012

@package support - cdm
@copyright 2012 Sourcefabric o.p.s.
@license http: // www.gnu.org / licenses / gpl - 3.0.txt
@author: Mugur Rus

Provides unit testing for the local filesystem module.
'''

# Required in order to register the package extender whenever the unit test is run.
if True:
    import package_extender
    package_extender.PACKAGE_EXTENDER.setForUnitTest(True)

# --------------------------------------------------------------------

from ally.cdm.impl.local_filesystem import HTTPDelivery, LocalFileSystemCDM, \
    LocalFileSystemLinkCDM
from ally.cdm.spec import PathNotFound
from ally.zip.util_zip import normOSPath
from datetime import datetime
from io import BytesIO
from os import makedirs, remove, sep, stat
from os.path import join, dirname, isfile, isdir
from shutil import rmtree
from tempfile import NamedTemporaryFile, TemporaryDirectory
import json
import re
import unittest

normpath = lambda txt: re.sub('[\\W]+', '', txt)

class TestHTTPDelivery(unittest.TestCase):

    def testHTTPDelivery(self):
        d = HTTPDelivery()
        d.serverURI = 'http://localhost:8080/content/'
        self.assertEqual(d.getURI('somedir/somefile.jpg'),
                         'http://localhost:8080/content/somedir/somefile.jpg',
                         'Computing the URI')

    def testLocalFilesystemCDM(self):
        d = HTTPDelivery()
        rootDir = TemporaryDirectory()
        d.serverURI = 'http://localhost/content/'
        d.repositoryPath = rootDir.name
#        d.repositoryPath = '/var/www/repository'
#        ioc.Initializer.initialize(d)
        cdm = LocalFileSystemCDM()
        cdm.delivery = d

        # test publish from a file from the file system
        try:
            srcTmpFile = NamedTemporaryFile(delete=False)
            srcTmpFile.close()
            dstPath = 'testdir1/tempfile.txt'
            cdm.publishFromFile(dstPath, srcTmpFile.name)
            dstFilePath = join(d.getRepositoryPath(), normOSPath(dstPath))
            self.assertTrue(isfile(dstFilePath))
            self.assertEqual(datetime.fromtimestamp(stat(dstFilePath).st_mtime),
                             cdm.getTimestamp(dstPath))
        finally:
            rmtree(dirname(dstFilePath))
            remove(srcTmpFile.name)

        # test publish from a file from a zip archive
        try:
            inFileName = join('dir1', 'subdir2', 'file1.txt')
            dstPath = join('testdir2', 'tempfile2.txt')
            cdm.publishFromFile(dstPath,
                                join(dirname(__file__), 'test.zip', inFileName))
            dstFilePath = join(d.getRepositoryPath(), normOSPath(dstPath))
            self.assertTrue(isfile(dstFilePath))
        finally:
            rmtree(dirname(dstFilePath))

        # test publish from a directory from the file system
        srcTmpDir = TemporaryDirectory()
        dirs = ('test1/subdir1', 'test2/subdir1')
        for dir in dirs:
            fullPath = join(srcTmpDir.name, dir)
            makedirs(fullPath)
            with open(join(fullPath, 'text.html'), 'w') as _f: pass
        try:
            cdm.publishFromDir('testdir3', srcTmpDir.name)
            dstDirPath = join(d.getRepositoryPath(), 'testdir3')
            for dir in dirs:
                dstFilePath = join(dstDirPath, dir, 'text.html')
                self.assertTrue(isfile(dstFilePath))
                self.assertEqual(datetime.fromtimestamp(stat(dstFilePath).st_mtime),
                                 cdm.getTimestamp(join('testdir3', dir, 'text.html')))
            # test remove path
            filePath = 'testdir3/test1/subdir1/text.html'
            self.assertTrue(isfile(join(d.getRepositoryPath(), filePath)))
            cdm.republish(filePath, filePath + '.new')
            self.assertTrue(isfile(join(d.getRepositoryPath(), filePath + '.new')))
            cdm.republish(filePath + '.new', filePath)
            cdm.remove(filePath)
            self.assertFalse(isfile(join(d.getRepositoryPath(), filePath)))
            dirPath = 'testdir3/test2'
            self.assertTrue(isdir(join(d.getRepositoryPath(), dirPath)))
            cdm.remove(dirPath)
            self.assertFalse(isdir(join(d.getRepositoryPath(), dirPath)))
        finally:
            rmtree(dstDirPath)

        # test publish from a directory from a zip file
        try:
            cdm.publishFromDir('testdir4', join(dirname(__file__), 'test.zip', 'dir1'))
            dstDirPath = join(d.getRepositoryPath(), 'testdir4')
            dstFilePath = join(dstDirPath, 'subdir1', 'file1.txt')
            self.assertTrue(isfile(dstFilePath))
            dstFilePath = join(dstDirPath, 'subdir2', 'file2.txt')
            self.assertTrue(isfile(dstFilePath))
            # Test whether republishing the same directory checks the last modified date
            # The file created manually in the repository should not be deleted because
            # the zip archive was not modified from the last publish
            dstFilePath = join(dstDirPath, 'sometestfile.txt')
            with open(dstFilePath, 'w') as _f: pass
            cdm.publishFromDir('testdir4', join(dirname(__file__), 'test.zip', 'dir1'))
            self.assertTrue(isfile(dstFilePath))
        finally:
            rmtree(dstDirPath)

        # test publish from a string
        try:
            path = join('testdir5', 'somecontent.txt')
            cdm.publishContent(path, BytesIO(b'test'))
            dstFilePath = join(d.getRepositoryPath(), path)
            self.assertTrue(isfile(dstFilePath))
        finally:
            rmtree(join(d.getRepositoryPath(), dirname(path)))

        # test publish from a file object
        try:
            path = join('testdir6', 'somecontent2.txt')
            cdm.publishFromFile(path, BytesIO(b'test 2'))
            dstFilePath = join(d.getRepositoryPath(), path)
            self.assertTrue(isfile(dstFilePath))
        finally:
            rmtree(join(d.getRepositoryPath(), dirname(path)))

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
