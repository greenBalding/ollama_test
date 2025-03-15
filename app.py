from flask import Flask, render_template, request
import ollama

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        user_input = request.form['prompt']
        
        # Create a clear prompt to request a multiple-choice question with one correct answer
        model_prompt = f"Generate a simple multiple-choice question about {user_input} with 4 options. " \
                       "Please ensure that one option is correct, and provide the question in the following format:\n" \
                       "Question: <question text>\n" \
                       "a) <option 1>\n" \
                       "b) <option 2>\n" \
                       "c) <option 3>\n" \
                       "d) <option 4>\n" \
                       "Correct Answer: <option>"

        # Call Ollama API to generate the response
        response = ollama.chat(model='gemma3:1b', messages=[{'role': 'user', 'content': model_prompt}])
        
        # Check if response contains the correct structure
        if 'message' in response and 'content' in response['message']:
            generated_content = response['message']['content']
        else:
            generated_content = "Sorry, there was an error generating the response."
        
        # Format the response to split the question and options
        formatted_content, correct_answer = format_response(generated_content)
        
        return render_template('index.html', question=formatted_content, correct_answer=correct_answer)
    
    return render_template('index.html', question=None, correct_answer=None)

def format_response(response):
    """
    This function formats the response into a structured multiple-choice question
    with HTML formatting and ensures there are 4 options, extracting the correct answer.
    """
    lines = response.split("\n")
    
    question = None
    options = {}
    correct_answer = None
    
    # Find the question text
    for line in lines:
        if line.strip().startswith("Question:"):
            question = line.strip().replace("Question:", "").strip()
            break
    
    if not question:
        return "Error: No valid question found.", "N/A"
    
    # Extract the options (lines starting with a, b, c, d)
    option_letters = ['a', 'b', 'c', 'd']
    for i, option_letter in enumerate(option_letters):
        option_line = next((line for line in lines if line.strip().startswith(f"{option_letter})")), None)
        if option_line:
            options[option_letter] = option_line.strip()[3:].strip()  # Remove the option letter and space
        else:
            options[option_letter] = f"Option {chr(97 + i)} not provided"
    
    # Extract the correct answer
    correct_answer_line = next((line for line in lines if line.strip().startswith("Correct Answer:")), None)
    if correct_answer_line:
        correct_answer = correct_answer_line.replace("Correct Answer:", "").strip()
    
    # Create an HTML-formatted multiple choice question
    formatted_content = f"<h2>{question}</h2>"
    formatted_content += "<ul>"
    for letter, option in options.items():
        formatted_content += f"<li>{letter}) {option}</li>"
    formatted_content += "</ul>"
    
    return formatted_content, correct_answer

if __name__ == '__main__':
    app.run(debug=True)