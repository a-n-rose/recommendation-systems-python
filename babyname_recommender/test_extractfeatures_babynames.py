import unittest
import sqlite3
import os
import numpy as np
from numpy.testing import assert_equal

#import class from module with my functions:
from extractfeatures_babynames import BuildTables, BuildFeatures




class TestFeatureEngineering(unittest.TestCase):
    '''
    Test the user vocab collection database
    '''
    
    def setUp(self):
        '''
        Setup a temporary database
        '''
        #create database
        self.db = BuildTables('test_features.db')
        
    # create_names_table
        msg = '''CREATE TABLE IF NOT EXISTS names(name_id INTEGER PRIMARY KEY,name text,sex text) '''
        self.db.c.execute(msg)
        self.db.conn.commit()
        
        name1 = ('1','Stacey','F')
        name2 = ('2','Frederick','M')
        name3 = ('3','Barbara','F')
        name4 = ('4','Shelman','M')
        
        msg = '''INSERT INTO names VALUES (?,?,?) '''
        self.db.c.executemany(msg,[name1,name2,name3,name4])
        self.db.conn.commit()
        
        self.bf = BuildFeatures()

    def tearDown(self):
        if self.db.conn:
            self.db.conn.close()
        os.remove("test_features.db")
        
    def test_get_names_all(self):
        expected_output = [(1,'Stacey'),(2,'Frederick'),(3,'Barbara'),(4,'Shelman')]
        self.assertEqual(self.db.get_names(),expected_output)
        
    def test_get_chars_length_dicts_all(self):
        names_tuples_list = self.db.get_names()
        expected_output = {1: 'a', 2: 'b', 3: 'c', 4: 'd', 5: 'e', 6: 'f', 7: 'h', 8: 'i',9: 'k', 10: 'l', 11: 'm', 12: 'n', 13: 'r', 14: 's', 15: 't', 16: 'y'}
        self.assertEqual(self.bf.get_chars_length_dicts(names_tuples_list)[0],expected_output)
        
    def test_coll_letter_length_data_all_name1(self):
        names_tuples_list = self.db.get_names()
        num_cols = len(self.bf.get_chars_length_dicts(names_tuples_list)[0])+2
        expected_output = np.array([1., 1., 0., 1., 0., 1., 0., 0., 0., 0., 0., 0.,  0., 0., 1., 1., 1., 6.])
        assert_equal(self.bf.coll_letter_length_data(names_tuples_list,num_cols)[0],expected_output) 
        
    def test_coll_letter_length_data_all_name2(self):
        names_tuples_list = self.db.get_names()
        num_cols = len(self.bf.get_chars_length_dicts(names_tuples_list)[0])+2
        expected_output = np.array([2., 0., 0., 1., 1., 1., 1., 0., 1., 1., 0., 0.,  0., 1., 0., 0., 0., 9.])
        assert_equal(self.bf.coll_letter_length_data(names_tuples_list,num_cols)[1],expected_output)    
        
    def test_coll_letter_length_data_all_name4(self):
        names_tuples_list = self.db.get_names()
        num_cols = len(self.bf.get_chars_length_dicts(names_tuples_list)[0])+2
        expected_output = np.array([4., 1., 0., 0., 0., 1., 0., 1., 0., 0., 1., 1.,  1., 0., 1., 0., 0., 7.])
        assert_equal(self.bf.coll_letter_length_data(names_tuples_list,num_cols)[3],expected_output)  
        
if __name__ == '__main__':
    unittest.main()
