from flask import Flask, request, render_template, jsonify
from dialog import findProduct


app = Flask(__name__)

@app.route('/search', methods=['GET'])
def query():
	query = request.args.get('q')
	query = query.replace("%20", " ")
	query = query.encode('utf-8')
	out = findProduct(query)
	resp = jsonify(products=out, code=200)
	return resp

@app.route("/")
def dialog():
	return render_template('index.html')
    
if __name__ == "__main__":
    app.run()