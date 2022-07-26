from sentence_transformers import SentenceTransformer, util
from flask import Flask, jsonify, request
# import the sentence transformer
embedder = SentenceTransformer('all-MiniLM-L6-v2')
# creating a Flask app
app = Flask(__name__)

@app.route("/s1/<s1>/s2/<s2>", methods = ['GET'])
def sentence_simi():
    s1 = request.args.get('s1')
    s2 = request.args.get('s2')
    print(s1,s2)
    s1_embed = embedder.encode(s1, convert_to_tensor=True)
    s2_embed = embedder.encode(s2, convert_to_tensor=True)
    cos_scores = util.cos_sim(s1_embed, s2_embed)
    return jsonify({'similarity-score': cos_scores[0][0]})


# driver function
if __name__ == '__main__':
  
    app.run(debug = True)

