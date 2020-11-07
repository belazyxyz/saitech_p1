'''
git add .
git commit -am 'msg'
git push heroku master

heroku logs --tail
'''
from flask import Flask , request
import pandas as pd
from flask import render_template, send_from_directory
import os
import app.modules.rulebook as rulebook

# app = Flask(__name__) 
app = Flask(__name__,
 static_folder = './public',
 template_folder="./templates")

@app.route("/") 
def home_view(): 
	return render_template("index.html")

@app.route('/api/outs/<path:path>')
def send_js(path):
	print("========= DOWNLOAD API =========")
	return app.send_static_file('outputs/{}'.format(path))

def _save_file(file):
	filename = file.filename
	filepath = '/tmp/{}'.format(filename)
	file.save(filepath)
	return filename

@app.route("/api/", methods=['POST']) 
def api(): 
	file = request.files['tallydata']
	tally_file = _save_file(file)

	file = request.files['asaldata']
	asal_file = _save_file(file)

	file = request.files['ledgerdata']
	ledger_file = _save_file(file)

	date_of_operation = request.form['data_date']

	response = rulebook.read_data(tally_file,asal_file,ledger_file, date_of_operation)
	return render_template("response.html", response = response)

@app.route("/merge/", methods=['POST']) 
def merge(): 
	files = request.files.getlist('mergefiles[]')
	local_file_paths = []
	dfs = []
	for f in files:
		saved_file = _save_file(f)
		local_file_paths.append(saved_file)

		df_file = os.path.join('/tmp', saved_file)
		print(df_file)
		df = pd.read_excel(df_file)
		dfs.append(df)
	
	master_df = pd.concat(dfs, axis=0).drop_duplicates(['Voucher Number', 'Item Name'],keep='last').sort_values('Date')
	print(master_df)
	output_file = os.path.join('app','public','outputs','combined.xlsx')
	master_df.to_excel(output_file, sheet_name='data', index=False)
	return app.send_static_file('outputs/combined.xlsx')

# if __name__ == "__main__": 
# 	# app.debug = 1
# 	app.run() 