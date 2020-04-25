class ReaderBase():
    __tablename__ = 'settings_spv'

    def kpis(self, seq):
    	joinseq = ','.join(seq)
    	return joinseq
    	
    def toKeyJSON(self, _dict):
    	_reversedDict = {}
    	for key in _dict:
    		_reversedDict.setdefault(key, _dict[key])

    	return _reversedDict

    def getKeyJSON(self):
    	_dict = self.toJSON()

    	_reversedDict = {}
    	for key in _dict:
    		_reversedDict.setdefault(_dict[key], key)

    	return _reversedDict