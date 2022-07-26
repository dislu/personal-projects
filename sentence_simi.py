'''Create a flask app to calculate text similarity between two strings'''
from sentence_transformers import SentenceTransformer, util
from flask import Flask, jsonify, request
# import the sentence transformer
embedder = SentenceTransformer('all-MiniLM-L6-v2')
# creating a Flask app
app = Flask(__name__)

@app.route("/home/<string:s1>/<string=s2>", methods = ['GET'])
def sentence_simi(s1,s2):
    # s1 = request.args.get('s1')
    # s2 = request.args.get('s2')
    # print(s1,s2)
    s1_embed = embedder.encode(s1, convert_to_tensor=True)
    s2_embed = embedder.encode(s2, convert_to_tensor=True)
    cos_scores = util.cos_sim(s1_embed, s2_embed)
    return jsonify({'similarity-score': cos_scores[0][0]})

# # Using flask to make an api
# # import necessary libraries and functions
# from flask import Flask, jsonify, request

# creating a Flask app
app = Flask(__name__)

# on the terminal type: curl http://127.0.0.1:5000/
# returns hello world when we use GET.
# returns the data that we send when we use POST.
@app.route('/', methods = ['GET', 'POST'])
def home():
	if(request.method == 'GET'):

		data = "sentence-similarity...'/home/s1/s2"
		return jsonify({'data': data})

# driver function
if __name__ == '__main__':

	app.run(debug = True)

# driver function
if __name__ == '__main__':
  
    app.run(debug = True)


