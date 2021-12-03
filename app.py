# Import Section
import json
from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import AutoTokenizer, TFAutoModelForQuestionAnswering
import tensorflow as tf
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# Initializing Models
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-cased-distilled-squad")
model = TFAutoModelForQuestionAnswering.from_pretrained("distilbert-base-cased-distilled-squad")
model_sim = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')

# Sample Text

def generate_answer(question, input_text):
    inputs = tokenizer(question, input_text, add_special_tokens=True, return_tensors="tf")
    input_ids = inputs["input_ids"].numpy()[0]
    outputs = model(inputs)
    answer_start_scores = outputs.start_logits
    answer_end_scores = outputs.end_logits
    answer_start = tf.argmax(answer_start_scores, axis=1).numpy()[0]
    answer_end = tf.argmax(answer_end_scores, axis=1).numpy()[0] + 1
    answer = tokenizer.convert_tokens_to_string(tokenizer.convert_ids_to_tokens(input_ids[answer_start:answer_end]))
    return answer

def get_similarity(gen_answer, correct_answer):
    sentences = []
    sentences.append(correct_answer)
    sentences.append(gen_answer)
    sentence_embeddings = model_sim.encode(sentences)
    arr = cosine_similarity([sentence_embeddings[0]],sentence_embeddings[1:])
    return arr[0]



def getResults(input_text, questions, correct_answers):
    generated_answers = []
    for question in questions:
        generated_answers.append(generate_answer(question, input_text))

    similarities = []
    for i in range(0, len(correct_answers)):
        sim = get_similarity(correct_answers[i], generated_answers[i])
        similarities.append(sim)
    
    return [generated_answers, similarities]
    

app = Flask(__name__)
CORS(app)


# NLP Tasks



# Flask Routes

@app.route('/')
def hello_world():
    return 'Works !'


@app.route('/results', methods=["POST"])
def get_results():
    req_body = request.get_json(force=True)
    # print(req_body)
    # data = json.loads(req_body)
    data = req_body
    input_text = data['input_text']
    questions = data['questions']
    correct_answers = data['correct_answers']
    # print("printing values ==== " + input_text, questions, correct_answers, data)
    results = getResults(input_text, questions, correct_answers)
    # print("results")
    print(results)
    gen_answer = results[0]
    sims = results[1]

    print("printing types")
    print(type(sims))
    print(type(gen_answer))

    # sims = sims.tolist()

    sims = list(sims)
    
    print(gen_answer)


    gen_answer = list(gen_answer)


    b = []
    for item in sims:
        print(item[0])
        b.append(str(item[0]))

    print(gen_answer, b)
    
    response = {
        "similarity": b,
        "generated_answers": gen_answer,
    }
    return response
