import pygame
import requests
from bs4 import BeautifulSoup
from pydantic import BaseModel
from typing import List
from openai import OpenAI
import io
from PIL import Image
import json

# Initialize OpenAI client
client = OpenAI(api_key="YOUR_API_KEY")

# Initialize Pygame
pygame.init()

# Set up the display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("NewsToon")  # Updated window name

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Fonts
font = pygame.font.Font(None, 16)  # Further reduced font size
number_font = pygame.font.Font(None, 36)  # Font for numbering

# Predefined URL
NEWS_URL = "https://www.forbes.com/sites/lanceeliot/2024/09/23/ai-hallucinations-invade-openai-latest-gpt-model-o1-in-quite-surprising-places/"

class NewsSummary(BaseModel):
    sentences: List[str]
    prompts: List[str]

def extract_text_from_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    paragraphs = soup.find_all('p')
    return ' '.join([p.text for p in paragraphs])

def generate_summary_and_prompts(url):
    text = extract_text_from_url(url)
    
    completion = client.chat.completions.create(
        model="gpt-4o-2024-08-06",
        messages=[
            {"role": "system", "content": "You are an expert at creating satirical and caricatured summaries and image prompts from news articles."},
            {"role": "user", "content": f"Create a 4-sentence summary of this news article, followed by 4 image-generating prompts that represent each sentence in a satirical or caricatured way. Respond with a JSON object in the following format:\n\n{{\"summary\": [\"sentence1\", \"sentence2\", \"sentence3\", \"sentence4\"], \"prompts\": [\"prompt1\", \"prompt2\", \"prompt3\", \"prompt4\"]}}\n\nHere's the article:\n\n{text}"}
        ],
        response_format={ "type": "json_object" }
    )
    
    result = json.loads(completion.choices[0].message.content)
    return NewsSummary(sentences=result['summary'], prompts=result['prompts'])

def generate_image(prompt):
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    image_url = response.data[0].url
    image_data = requests.get(image_url).content
    image = Image.open(io.BytesIO(image_data))
    return image.resize((400, 300))

def wrap_text(text, font, max_width):
    words = text.split()
    lines = []
    current_line = []
    for word in words:
        test_line = ' '.join(current_line + [word])
        if font.size(test_line)[0] <= max_width:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    if current_line:
        lines.append(' '.join(current_line))
    return lines

def main():
    print(f"Generating comic strip for news article: {NEWS_URL}")
    summary = generate_summary_and_prompts(NEWS_URL)
    
    print("Generating images...")
    images = []
    for i, prompt in enumerate(summary.prompts):
        print(f"\nSentence {i+1}: {summary.sentences[i]}")
        print(f"Prompt {i+1}: {prompt}")
        images.append(generate_image(prompt))
    
    print("\nComic strip generated. Displaying result...")
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        screen.fill(BLACK)
        
        for i in range(4):
            x = (i % 2) * 400
            y = (i // 2) * 300
            
            # Convert PIL Image to Pygame surface
            py_image = pygame.image.fromstring(images[i].tobytes(), images[i].size, images[i].mode)
            
            screen.blit(py_image, (x, y))
            
            # Draw black rectangle for text background
            pygame.draw.rect(screen, BLACK, (x, y + 260, 400, 40))
            
            # Wrap and render text
            wrapped_text = wrap_text(summary.sentences[i], font, 390)
            for j, line in enumerate(wrapped_text[:2]):  # Limit to 2 lines
                text_surface = font.render(line, True, WHITE)
                screen.blit(text_surface, (x + 5, y + 265 + j * 18))
            
            # Draw number in top left corner
            number_surface = number_font.render(str(i+1), True, RED)
            screen.blit(number_surface, (x + 10, y + 10))
        
        pygame.display.flip()
    
    pygame.quit()

if __name__ == "__main__":
    main()