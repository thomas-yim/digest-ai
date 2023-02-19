import openai
from pdf_text_recognition import read_pdf
import json

def request(text, num_notecards, grade_level, prompt_func):
    prompt_func(text, num_notecards, grade_level)
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt_func(text, num_notecards, grade_level),
        temperature=0.3,
        max_tokens=800,
    )
    return response


def generate_notecards_prompt(text, num, grade_level):
    return f"""
    Using the reference text below, create a {num} set of flashcards at a {grade_level} level of the reference text below. 

    Write it in a .json format as shown below. The example prompt was to create a 2 term set of flashcards.
    
		[
        {{
            "term": "term 1 goes here",
            "definition": "term 2 goes here",
            "starred": "False"

        }},
        {{
            "term": "term 2 goes here",
            "definition": "definition 2 goes here",
            "starred": "False"
        }}
    ]

    Reference text to base your flashcards off of is contained within the ^^:

    ^{text}^

    Insert your {num} set of flashcards at a {grade_level} reading level below:
    """

def generate_mc_prompt(text, num, grade_level):
    return f"""
    Create a {num} multiple choice quiz at a {grade_level} reading level of the reference text below. 

    Write it in a .json format as shown below. The example prompt was to create a 2 question multiple choice quiz questions. Randomize which of the 4 letter options is the correct answer.

    [
        {{
            "question": "Question 1 goes here",
            "A": "Option A goes here",
		    "B": "Option B goes here",
			"C": "Option C goes here, which for this question is correct",
			"D": "Option D goes here",
            "answer": "C"
		}},
        {{
            "question": "Question 2 goes here",
            "A": "Option A goes here, which for this question is correct",
		    "B": "Option B goes here",
		    "C": "Option C goes here",
		    "D": "Option D goes here",
            "answer": "A"
		}}
    ]

    Reference text to base your multiple choice quiz off of is contained within the ^^:

    ^{text}^

    Insert your {num} multiple choice quiz at a {grade_level} reading level of the reference text below:
    """

def generate_tf_prompt(text, num, grade_level):
    return f"""
    Create a {num} question true or false quiz at a {grade_level} reading level of the reference text below. 

    Write it in a .json format as shown below. The example prompt was to create a 2 question true or false quiz questions.
    Try to make an equal number of True and False answers.

    [
		{{
            "question": "Question 1 goes here, which for this question is true.",
            "answer": "True"
		}},
        {{
            "question": "Question 2 goes here, which for this question is false.",
            "answer": "False"
		}}
	]

    Reference text to base your true or false quiz off of is contained within the ^^:

    ^{text}^

    Insert your {num} true or fasle quiz at a {grade_level} reading level of the reference text below:
    """

def generate_p_summary_prompt(text, num_paragraphs, grade_level):
    return f"""
    Create a 1 sentence overview and a {num_paragraphs} paragraph summary at a {grade_level} reading level of the reference text below. 

    Write it in a .json format as shown below. The example prompt was to create a 1 sentence overview and a 2 paragraph summary.

    {{
        "overview": "overview goes here",
	    "paragraphs": [
			"paragraph 1 goes here.", 
			"paragraph 2 goes here." 
        ]
    }}

    Reference text to base your summary off of is contained within the ^^:

    ^{text}^

    Insert your 1 sentence overview and {num_paragraphs} paragraph summary at a {grade_level} reading level of the reference text below:
    """

def generate_bullets_prompt(text, num_bullets, grade_level):
    return f"""
    Create a 1 sentence overview and {num_bullets} bullet point summary at a {grade_level} reading level of the reference text below. 

    Write it in a .json format as shown below. The example prompt was to create a 1 sentence overview and a 2 bullet point summary.

    {{
        "overview": "overview goes here",
		"bps": [
		    "bullet point 1 goes here.", 
			"bullet point 2 goes here." 
        ]
    }}

    Reference text to base your summary off of is contained within the ^^:

    ^{text}^

    Insert your 1 sentence overview and {num_bullets} bullet point summary at a {grade_level} reading level of the reference text below:
    """

def generate_initial_summary(text, max_length):
	return f"""
	Create a summary of the reference text that is a maximum of {max_length} tokens.

		Reference text to base your summary off of is contained within the ^^:

    ^{text}^

		Insert your summary that is a maxiumum of {max_length} tokens below:
		"""

if __name__ == "__main__":
    openai.api_key = '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'
    text_slides = read_pdf("Lecture7.pdf")

    request_type = "summary"

    if request_type == "notecard":
        prompt_func = generate_notecards_prompt

    if request_type == "mcquiz":
        prompt_func = generate_mc_prompt

    if request_type == "tfquiz":
        prompt_func = generate_tf_prompt

    if request_type == "summary":
        prompt_func = generate_p_summary_prompt
        
    text = ""
    for i in range(len(text_slides)-10):
        text += text_slides[i] + "\n"
    
    num = 10
    grade_level = "University"

    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt_func(text, num, grade_level),
        temperature=0.3,
        max_tokens=1000,
    )

    result = response.choices[0].text
    print(result)
    print(result)
    json_data = json.loads(result)
    
    with open(request_type + ".json", "w") as outfile:
        json.dump(json_data, outfile)