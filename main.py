import PIL
from PIL import Image
from io import BytesIO
import replicate
import requests
import openai
import os
import re


openai.api_key = "sk-"
openai.organization = "org"
# replicate key

def main(iterations: int = 10) -> None:
    preprompt: str = (
        "You are a battle image description imagineer. Your job is to given a description that I give "
        "you of mid evil attack create a counter attack to the event. The counter attack should be in "
        "a simple 3 sentence description. The only output to my input should be the "
        "counter description. Use very simple and logical statements but make it fantastical. Initial prompt: \n"
    )
    initial_prompt: str = (
        "The attacking force lined the hill in preparation for attack on the castle"
    )

    for i in range(iterations):
        initial_prompt = initial_prompt.lstrip(".\n")
        initial_prompt = re.sub(r"^[^a-zA-Z]+", "", initial_prompt.strip())
        initial_prompt = initial_prompt.replace('\n', '')
        current_prompt = preprompt + initial_prompt

        print(f"creating image... {i}")
        img = create_image(initial_prompt)
        file_name = "fight" + str(i) + ".png"
        img.save("./tmp/" + file_name)
        print("image created")

        print("saving text...")
        with open("./tmp/story.md", "a") as f:
            f.write("\n### " + initial_prompt + "\n")
            f.write(f"![]({file_name})\n")

        print("grabbing next prompt...")
        if i == iterations-2:
            print("last iteration")
            current_prompt += "\nThis is the last battle end the story."
        initial_prompt = gpt_request(current_prompt)
    



def create_image(prompt: str) -> Image:
    img_url = replicate.run(
        "ai-forever/kandinsky-2:65a15f6e3c538ee4adf5142411455308926714f7d3f5c940d9f7bc519e0e5c1a",
        input={
            "prompt": prompt,
            "prior_cf_scale": 1,
            "num_inference_steps": 40
        }
    )
    response = requests.get(img_url)
    if response.status_code == 200:
        try:
            return Image.open(BytesIO(response.content))
        except PIL.UnidentifiedImageError:
            raise Exception(f'Error: {response.status_code}')
    else:
        raise Exception(f'Error: {response.status_code}')



def gpt_request(input_prompt: str)-> str:
    resp = openai.Completion.create(
        model="text-davinci-003",
        prompt=input_prompt,
        temperature=0.5,
        max_tokens=60,
        top_p=1.0,
        frequency_penalty=0.5,
        presence_penalty=0.0,
        # stop=["Initial prompt:"]
    )
    return resp.choices[0].text




if __name__ == "__main__":
    main()