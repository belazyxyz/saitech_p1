from app.main import app 

if __name__ == "__main__": 
		app.debug = 1
		# app.run() 
		app.run(host="0.0.0.0", port=8000)

