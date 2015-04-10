'''
Created on Nov 25, 2011

@author: JSU
pylint score 9.17/10 as of 17 Jan 2012
'''
class DualDict(dict):
    """
    a dictionary which can lookup value by key, or keys by value
    """
    def __init__(self, items):  #=[]):
        """items can be a list of pair_lists or a dictionary"""
        dict.__init__(self, items)
 
    def get_key(self, value):
        """find the key(s) as a list given a value"""
        return [item[0] for item in self.items() if item[1] == value]
 
    def get_value(self, key):
        """find the value given a key"""
        try:
            return self[key]
        except Exception as ex:
            #print ex
            return ''
        
if __name__ == '__main__':    
    MONTHS = DualDict({'Jan':1, 'Feb':2, 'Mar':3})
    print MONTHS.get_value('Jan')
    print MONTHS.get_key(1)
    
    print [m for m in MONTHS]
    print [k for k in MONTHS.keys()]
    print [v for v in MONTHS.values()]

    MONTHS_REV = DualDict({1:'Jan', 2:'Feb', 3:'Mar'})
    print MONTHS_REV.get_value('Jan')
    print MONTHS_REV.get_key(1)
    
    print [m for m in MONTHS_REV]
    print [k for k in MONTHS_REV.keys()]
    print [v for v in MONTHS_REV.values()]
