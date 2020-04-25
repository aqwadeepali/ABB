class ReaderBase():
	def kpis(self, seq):
		# seq = ['Flour', 'G Sugar', 'Salt', 'SBC', 'Vitamin', 'Calcium', 'ABC', 'Lecithin', 'GMS', 'SMP', 'Milk', 'Syrup', 'Vannila', 'Flavour', 'FFM', 'Water', 'Biscuit Dust', 'Cream', 'Sugar', 'Palm Oil']
		joinseq = ','.join(seq)
		return joinseq
		
	def toKeyJSON(self, _dict):
		# _dict = self.toJSON()

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

	def toJSON(self):
		json = {
			'TIME':'time',
			'Flour:Batch Count':'flour_batch_count',
			'Flour:Batch Set Weight':'flour_batch_set_weight',
			'Flour:Actual Weight':'flour_actual_weight',
			'Flour:Total Valve Day':'flour_total_valve_day',
			'G Sugar Batch Count':'g_sugar_batch_count',
			'G Sugar Batch Set Weight':'g_sugar_batch_set_weight',
			'G Sugar Actual Weight':'g_sugar_actual_weight',
			'G Sugar Total Valve Day':'g_sugar_total_valve_day',
			'Salt Batch Count':'salt_batch_count',
			'Salt Batch Set Weight':'salt_batch_set_weight',
			'Salt Actual Weight':'salt_actual_weight',
			'Salt Total Valve Day':'salt_total_valve_day',
			'SBC Batch Count':'sbc_batch_count',
			'SBC Batch Set Weight':'sbc_batch_set_weight',
			'SBC Actual Weight':'sbc_actual_weight',
			'SBC Total Valve Day':'sbc_total_valve_day',
			'Vitamin Batch Count':'vitamin_batch_count',
			'Vitamin Batch Set Weight':'vitamin_batch_set_weight',
			'Vitamin Actual Weight':'vitamin_actual_weight',
			'Vitamin Total Valve Day':'vitamin_total_valve_day',
			'Calcium Batch Count':'calcium_batch_count',
			'Calcium Batch Set Weight':'calcium_batch_set_weight',
			'Calcium Actual Weight':'calcium_actual_weight',
			'Calcium Total Valve Day':'calcium_total_valve_day',
			'ABC Batch Count':'abc_batch_count',
			'ABC Batch Set Weight':'abc_batch_set_weight',
			'ABC Actual Weight':'abc_actual_weight',
			'ABC Total Valve Day':'abc_total_valve_day',
			'Lecithin Batch Count':'lecithin_batch_count',
			'Lecithin Batch Set Weight':'lecithin_batch_set_weight',
			'Lecithin Actual Weight':'lecithin_actual_weight',
			'Lecithin Total Valve Day':'lecithin_total_valve_day',
			'GMS Batch Count':'gms_batch_count',
			'GMS Batch Set Weight':'gms_batch_set_weight',
			'GMS Actual Weight':'gms_actual_weight',
			'GMS Total Valve Day':'gms_total_valve_day',
			'SMP Batch Count':'smp_batch_count',
			'SMP Batch Set Weight':'smp_batch_set_weight',
			'SMP Actual Weight':'smp_actual_weight',
			'SMP Total Valve Day':'smp_total_valve_day',
			'Milk Batch Count':'milk_batch_count',
			'Milk Batch Set Weight':'milk_batch_set_weight',
			'Milk Actual Weight':'milk_actual_weight',
			'Milk Total Valve Day':'milk_total_valve_day',
			'Syrup Batch Count':'syrup_batch_count',
			'Syrup Batch Set Weight':'syrup_batch_set_weight',
			'Syrup Actual Weight':'syrup_actual_weight',
			'Syrup Total Valve Day':'syrup_total_valve_day',
			'Vannila Batch Count':'vannila_batch_count',
			'Vannila Batch Set Weight':'vannila_batch_set_weight',
			'Vannila Actual Weight':'vannila_actual_weight',
			'Vannila Total Valve Day':'vannila_total_valve_day',
			'Flavour Batch Count':'flavour_batch_count',
			'Flavour Batch Set Weight':'flavour_batch_set_weight',
			'Flavour Actual Weight':'flavour_actual_weight',
			'Flavour Total Valve Day':'flavour_total_valve_day',
			'FFM Batch Count':'ffm_batch_count',
			'FFM Batch Set Weight':'ffm_batch_set_weight',
			'FFM Actual Weight':'ffm_actual_weight',
			'FFM Total Valve Day':'ffm_total_valve_day',
			'Water Batch Count':'water_batch_count',
			'Water Batch Set Weight':'water_batch_set_weight',
			'Water Actual Weight':'water_actual_weight',
			'Water Total Valve Day':'water_total_valve_day',
			'Biscuit Dust Batch Count':'biscuit_dust_batch_count',
			'Biscuit Dust Batch Set Weight':'biscuit_dust_batch_set_weight',
			'Biscuit Dust Actual Weight':'biscuit_dust_actual_weight',
			'Biscuit Dust Total Valve Day':'biscuit_dust_total_valve_day',
			'Sugar Batch Count':'sugar_batch_count',
			'Sugar Batch Set Weight':'sugar_batch_set_weight',
			'Sugar Actual Weight':'sugar_actual_weight',
			'Sugar Total Valve Day':'sugar_total_valve_day',
			'Cream Batch Count':'cream_batch_count',
			'Cream Batch Set Weight':'cream_batch_set_weight',
			'Cream Actual Weight':'cream_actual_weight',
			'Cream Total Valve Day':'cream_total_valve_day',
			'Palm Oil Batch Count':'palm_oil_batch_count',
			'Palm Oil Batch Set Weight':'palm_oil_batch_set_weight',
			'Palm Oil Actual Weight':'palm_oil_actual_weight',
			'Palm Oil Total Valve Day':'palm_oil_total_valve_day'
		}
		return json