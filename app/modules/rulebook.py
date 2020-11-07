import pandas as pd
import numpy as np
import os
from openpyxl import load_workbook

def _desc_pd_table(df):
	tbl_str = ''
	col_names = ['Column', 'Sum', 'Average', 'Count', 'Unique Values']
	rows = []
	for col in list(df):
		cols = {}
		print(df.dtypes[col])
		cols['column'] = col
		if df.dtypes[col] == np.float64 or df.dtypes[col] == np.int64:
			cols['sum'] = str(round(df[col].sum(skipna = True),2))
			cols['avg'] = str(round(df[col].mean(skipna = True),2))
		else:
			cols['sum'] = 'n/a'
			cols['avg'] = 'n/a'
		cols['rows'] = df[col].shape[0]
		cols['unique'] = df[col].nunique()
		print(cols)
		rows.append(cols)
		
	return rows


#read files
def read_data(tally_file, asal_file, ledger_file, date_of_operation, combined_file = None):
	response = {}
	data_report = {}
	data_report['date'] = date_of_operation
	print("Started reading {}".format(tally_file))
	# df = pd.read_excel(os.path.join('app','data',tally_file))
	if not os.path.exists('/tmp/'):
		os.makedirs('/tmp/')
	df = pd.read_excel('/tmp/{}'.format(tally_file))
	print(df['Date'])
	data_report['original_row_count'] = df.shape[0]

	mask = (df['Date'] >= date_of_operation) & (df['Date'] <= date_of_operation)
	df = df.loc[mask]
	data_report['desc_original_data'] = _desc_pd_table(df)
	data_report['row_count_after_date_filter'] = df.shape[0]
	pd.set_option('display.max_columns', None)
	# data_report['desc_original_data'] = df.apply(pd.DataFrame.describe, axis=1)
	
	print("After Filtering ===> ")
	print(df['Date'])
	# return None

	combined_file_location = None
	if combined_file is not None:
		combined_file_location = os.path.join('app','public','outputs',combined_file)
	ledger_file = '/tmp/{}'.format(ledger_file)
	asal_file = '/tmp/{}'.format(asal_file)
	# ledger_df = pd.read_excel(ledger_file, sheet_name='Pro Group', names=['s6_Group','s8_ProGroup'], header=None)
	ledger_df = pd.read_excel(ledger_file, sheet_name='Sheet1', names=['s6_Group','s8_ProGroup'], header=None)
	asal_df = pd.read_excel(asal_file, skiprows=3, sheet_name='newstock pv')
	asal_df = asal_df.rename(columns = {"Row Labels": "s9_ItemNameModified"})
	print(asal_df)
	asal_df = asal_df[['s9_ItemNameModified', 'P.RATE','ASAL','BROKER','OWNER','DATE OF ARRIVED', 'S.RATE',]]
	asal_df['S.RATE'] = asal_df['S.RATE'].replace("NO SALES",0)
	output_file = tally_file.replace('.xlsx', '-{}.xlsx'.format(date_of_operation))
	output_file = os.path.join('app','public','outputs',output_file)

	def party_group(x):
		if x=='Caz':
			return 'Cash'
		elif x=='':
			return 'Direct'
		else:
			return 'Broker'

	df['s3_PartyName'] = df['Party Name'].apply(lambda x: x.split("/")[0])
	df['s3_Location_bef'] = df['Party Name'].apply(lambda x: x.split("/")[1] if len(x.split("/"))>1 else '')
	df['s3_Location'] = df['s3_Location_bef'].apply(lambda x: x.split("(")[0])
	df['s3_Pincode_bef'] = df['s3_Location_bef'].apply(lambda x: x.split("(")[1].split(")")[0] if len(x.split("("))>1 else '')
	df['s3_Pincode'] = df['s3_Pincode_bef'].apply(lambda x: x if x.isnumeric() else '')
	df['s3_LedgerGroup'] = df['s3_Pincode_bef'].apply(lambda x: x if not x.isnumeric() else '')
	df['s3_PartyGroup'] = df['s3_LedgerGroup'].apply(party_group)
	df['s5_Brand'] = df['Item Name'].apply(lambda x: x.split(' ')[0])
	df['s6_Group'] = df['Item Name'].apply(lambda x: x.split(' ')[1])
	df['s7_KG'] = df['Item Name'].apply(lambda x: x.split(' ')[2])
	print(df)

	data_report['records_before_merging_ledger'] = df.shape[0]
	df1 = pd.merge(df, ledger_df, on='s6_Group')
	data_report['records_after_merging_ledger'] = df1.shape[0]

	current_ledgers = df['s6_Group'].unique()
	available_ledgers = ledger_df['s6_Group'].unique()

	data_report['missing_items_in_ledger'] = [item for item in current_ledgers if item not in available_ledgers]

	df1['s9_ItemNameModified'] = df1['s5_Brand'] + " " + df1['s6_Group']

	df1['s10_ModifiedBilledQuantity'] = df1['Billed Quantity']/50

	df2 = pd.merge(df1, asal_df, on='s9_ItemNameModified')
	df2['s18_DIF'] = pd.to_numeric(df2['Rate']) - pd.to_numeric(df2['S.RATE'])

	current_items = df1['s9_ItemNameModified'].unique()
	asal_items = asal_df['s9_ItemNameModified'].unique()
	data_report['records_before_merging_asal'] = df1.shape[0]
	data_report['records_after_merging_asal'] = df2.shape[0]

	data_report['missing_items_in_asal'] = [item for item in current_items if item not in asal_items]


	print(df2.describe())
	data_report['desc_report_data'] = _desc_pd_table(df2)

	transaction_dates = pd.unique(df2['Date'])
	# splitted_df = {}
	# for i, transaction_date in enumerate(transaction_dates):
		# splitted_df[transaction_date] = df2[df2['Date'] == transaction_date]
	
	# table = pd.pivot_table(df2,index=["Voucher Type","s3_PartyGroup","s9_ItemNameModified"],
	# 		   values=["S.RATE","Billed Quantity"],
	# 		   aggfunc=[np.sum,np.mean],fill_value=0)

	
	if combined_file_location is not None and os.path.exists(combined_file_location):
		print("Combining....")
		combined_df = pd.read_excel(combined_file_location, sheet_name='data',)
		combined_df = combined_df.append(df2).drop_duplicates(['Voucher Number'],keep='last').sort_values('Date')
		print("Writing to file...")
		book = load_workbook(combined_file_location)
		std=book.get_sheet_by_name('data')
		print("Deleting existing sheet...")
		book.remove_sheet(std)
		writer = pd.ExcelWriter(combined_file_location, engine = 'openpyxl')
		writer.book = book
		combined_df.to_excel(writer, sheet_name='data', index=False)
		writer.save()
		writer.close()
		print("Closed file...")

		

	with pd.ExcelWriter(output_file) as writer:
		df2.to_excel(writer, sheet_name='Consolidated', index=False)
		# table.to_excel(writer, sheet_name='Report')
		print("Writing main data")
		# for dd in splitted_df:
			# print("Writing data for {}".format(dd))
			# splitted_df[dd].to_excel(writer, sheet_name=str(dd).replace(":","_").split("T")[0], index=False)
	response['output_file'] = str(os.path.basename(output_file))
	response['logs'] = data_report
	return response
	

if __name__ == "__main__":
	arr = os.listdir('data')
	print(arr)
	for f in arr:
		if f.endswith('.xlsx'):
			source = os.path.join('data',f)
			archieve = os.path.join('data','archieve',f)
			read_data(source)
			os.rename(source, archieve)