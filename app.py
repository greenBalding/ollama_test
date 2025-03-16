from flask import Flask, render_template, request
import ollama

app = Flask(__name__, static_url_path='/static')

def generate_question(prompt):
    """
    Calls Ollama API to generate a multiple-choice question with an explanation.
    """
    model_prompt = (
        f"Generate a simple multiple-choice question about {prompt} with 4 options. "
        "Ensure that one option is correct and provide an explanation for the correct answer. "
        "Format the response as follows:\n"
        "Question: <question text>\n"
        "a) <option 1>\n"
        "b) <option 2>\n"
        "c) <option 3>\n"
        "d) <option 4>\n"
        "Correct Answer: <correct option>\n"
        "Explanation: <why this option is correct>"
    )
    
    response = ollama.chat(model='gemma3:1b', messages=[{'role': 'user', 'content': model_prompt}])
    
    if 'message' in response and 'content' in response['message']:
        return parse_response(response['message']['content'])
    return "Error generating question.", "N/A", "No explanation available."

def parse_response(response_text):
    """Extracts the question, options, correct answer, and explanation from the response."""
    lines = response_text.split("\n")
    question, options, correct_answer, explanation = None, {}, None, None
    
    for line in lines:
        if line.startswith("Question:"):
            question = line.replace("Question:", "").strip()
        elif line.startswith("a)") or line.startswith("b)") or line.startswith("c)") or line.startswith("d)") :
            key = line[0]
            options[key] = line[3:].strip()
        elif line.startswith("Correct Answer:"):
            correct_answer = line.replace("Correct Answer:", "").strip()
        elif line.startswith("Explanation:"):
            explanation = line.replace("Explanation:", "").strip()

    # Return the options separately to use them in the HTML template
    option_a = options.get('a', '')
    option_b = options.get('b', '')
    option_c = options.get('c', '')
    option_d = options.get('d', '')
    
    return question, option_a, option_b, option_c, option_d, correct_answer, explanation

@app.route('/', methods=['GET', 'POST'])
def index():
    # Initialize variables
    question, option_a, option_b, option_c, option_d, correct_answer, explanation = None, None, None, None, None, None, None
    prompt = ""
    
    # Handle the form submission
    if request.method == 'POST':
        prompt = request.form['prompt']
        
        # If the 'regenerate' button is clicked, regenerate the full question
        if 'regenerate' in request.form:
            question, option_a, option_b, option_c, option_d, correct_answer, explanation = generate_question(prompt)
        else:
            # Initial generation on the first submit
            question, option_a, option_b, option_c, option_d, correct_answer, explanation = generate_question(prompt)
    
    return render_template('index.html', 
                           question=question, 
                           option_a=option_a,
                           option_b=option_b,
                           option_c=option_c,
                           option_d=option_d,
                           correct_answer=correct_answer,
                           explanation=explanation,
                           prompt=prompt)

if __name__ == '__main__':
    app.run(debug=True)