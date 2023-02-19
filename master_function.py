import openai
import json
import os
from audio_recognition import onlyAudio
from slides import processSlides
from pdf_text_recognition import read_pdf
from generate_prompt import generate_notecards_prompt, generate_mc_prompt, generate_tf_prompt, generate_p_summary_prompt, generate_bullets_prompt, generate_initial_summary
from config_keys import OPENAI_KEY

MAX_INPUT_LEN = 1500

def generateLearningMaterials(filename, material_type, num_items, grade_level):
    openai.api_key = OPENAI_KEY
    name, ext = filename.split(".")[0], filename.split(".")[1]
    output = ""
    if os.path.exists(f"caches/{name}.txt"):
        print("Loading from Cache")
        if os.path.exists(f"caches/{name}.txt"):
            with open(f"caches/{name}.txt", "r") as f:
                lines = f.readlines()
                output += "\n".join(lines)
            f.close()
    else:
        if ext.lower() == "mp4":
            res = processSlides(filename)
            for slide_text, audio_text in res:
                output += "\nNext Slide:\n"
                output += slide_text
                output += audio_text
        elif ext.lower() == "wav":
            output = onlyAudio(filename)
        elif ext.lower() == "pdf":
            output = read_pdf(filename)

        with open(f"caches/{name}.txt", "w") as f:
            f.writelines(output)
        f.close()

    words = output.split(" ")
    
    if len(words) > MAX_INPUT_LEN:
        output = ""
        chunks = [" ".join(words[i:i+MAX_INPUT_LEN]) for i in range(0, len(words), MAX_INPUT_LEN)]

        chunk_summary_len = int(MAX_INPUT_LEN/len(chunks))
        print(f"Summary Length: {chunk_summary_len}")
        for i in range(len(chunks)):
            print(f"Truncating Part {i}")
            chunk = chunks[i]

            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=generate_initial_summary(chunk, chunk_summary_len),
                temperature=0.3,
                max_tokens=chunk_summary_len,
            )
            output += response.choices[0].text

        
    
    # Default to summary prompt
    prompt_func = generate_p_summary_prompt

    if material_type == "NOTECARD":
        prompt_func = generate_notecards_prompt

    if material_type == "MCQUIZ":
        prompt_func = generate_mc_prompt

    if material_type == "TFQUIZ":
        prompt_func = generate_tf_prompt

    if material_type == "BULLET":
        prompt_func = generate_bullets_prompt
    
    response = openai.Completion.create(
        model="text-davinci-003",
        prompt=prompt_func(output, num_items, grade_level),
        temperature=0.3,
        max_tokens=1000,
    )

    result = response.choices[0].text
    print(result)

    json_data = json.loads(result)
    
    with open(f"outputs/{name}_{material_type}.json", "w") as outfile:
        json.dump(json_data, outfile, indent=4)
    return json_data
        

if __name__ == "__main__":
    openai.api_key = OPENAI_KEY
    filename = "semantics.mp4"
    material_type = "NOTECARD"
    num_items = 5
    grade_level = "University"
    generateLearningMaterials(filename, material_type, num_items, grade_level)

    


    

