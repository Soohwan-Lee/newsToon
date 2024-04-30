### 현재 문제점 -> 최종 prompot이 일관되지 못해서 parsing이 힘듦. 더 나은 전략이 필요함. 4줄 씩 요약 먼저 시키고, 각 4줄에 알맞는 일러스트 생성 프롬프트를 다시 생성해야하나..?
### 그것만 수정하면 parser 함수만 수정하면 이미지 생성 가능.

from openai import OpenAI
from IPython.display import Image, display

client = OpenAI(api_key='YOUR-API-KEY')

def news_summary_generator(news_article):
  personality = "Please transform this news article into a clearly structured format suitable for a first-time reader. Generate an output of exactly eight consecutive lines: four brief summaries alternated with four text descriptions of visual images. Each summary should be immediately followed by a visual description that closely illustrates the content summarized. Ensure there are no line breaks between pairs and maintain a strict sequence without any deviations or extraneous elements. This structured format is crucial for smooth parsing and data processing."
  messages = [{"role" : "system", "content" : f"{personality}"}]
  messages.append({"role" : "user", "content" : news_article})

  completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=messages,
    temperature=0.8
  )

  bot_response = completion.choices[0].message.content
  # messages.append({"role" : "assistant", "content" : f"{bot_response}"})
  # print(f'Devil Advocate: {bot_response}')

  return bot_response


def parser(text):
    lines = text.strip().split("\n")
    summaries = []
    illustrations = []
    
    # 요약과 프롬프트를 번갈아 읽으며 리스트에 추가
    for i in range(0, len(lines), 2):
        if i+1 < len(lines):
            summaries.append(lines[i].strip())
            illustrations.append(lines[i+1].replace("DALL-E prompt: ", "").strip())
    
    return summaries, illustrations



def generate_and_display_images(illustrations):
    images = []
    for illustration in illustrations:
        response = client.images.generate(
            model="dall-e-3",
            prompt=illustration,
            size="1024x1024",
            quality="standard",
            n=1
        )
        image_url = response.data[0].url
        images.append(image_url)
        print("Generated Image URL:", image_url)

    return images



if __name__ == "__main__":
    # News articles: https://www.bbc.com/news/business-68914929
    news_article = """
    Elon Musk is visiting Beijing with media reports saying he aims to discuss enabling autonomous driving mode on Tesla cars in China. Mr Musk wants to enable Full Self Driving (FSD) in China and transfer data collected in the country abroad to train its algorithms. FSD is available in countries including the US but not in China. The news came after a US report tied Tesla's autonomous driving modes to at least 13 crashes, involving one death. During a meeting with Chinese Premier Li Qiang, Mr Musk was quoted by state media as saying Tesla was willing deep cooperation with China to "achieve more win-win results". In response, Mr Li told Mr Musk the Chinese market would "always be open to foreign-funded firms," according to the reports. China is Tesla's second-biggest market. Other carmakers such as Xpeng - headquartered in Guangzhou - have been attempting to compete with Tesla by rolling out similar self-driving functions in their cars. On Sunday, Mr Musk described Chinese car manufacturers as "the most competitive car companies in the world". Tesla has previously taken steps to reassure Chinese authorities about the rollout of FSD in the country, including establishing a data centre in Shanghai to process data about Chinese consumers in accordance with local laws. The trip comes days after the US's National Highway Traffic Safety Administration (NHTSA) said it was investigating whether a recall successfully addressed safety concerns relating to Tesla's driver assistance system. The NHTSA said that despite requirements that drivers maintain focus on the road and be prepared to take control at a moment's notice when autonomous driving was enabled, drivers involved in the crashes "were not sufficiently engaged". The regulator's analysis was conducted before a recall Tesla said would fix the issue. Tesla's software is supposed to make sure that drivers are paying attention and that the feature is only in use in appropriate conditions, such as driving on highways. Mr Musk has promised that Teslas will be able to act as autonomous "robotaxis" for years. In 2015, he said Teslas would achieve "full autonomy" by 2018. And in 2019, he said the company would have robotaxis operating by the following year. This month, the Tesla chief executive said he would reveal the company's robotaxi in August. Critics accuse Mr Musk of consistently hyping up the prospects of full autonomous driving to prop up the company's share price, which has fallen on the back of challenges including falling demand for electric vehicles worldwide and competition from cheaper Chinese manufacturers. Mr Musk denies the accusations. Tesla has been cutting the prices of its cars in China and other markets to drum up demand. "Tesla prices must change frequently in order to match production with demand," Mr Musk recently said on X, the microblogging platform previously known as Twitter which the billionaire owns. Tesla recently reported a 13% fall in automotive sales to $17.3bn (£13.7bn) for the first three months of this year. Overall sales across Tesla dropped by 9% while its profits fell sharply to $1.13bn compared to $2.51bn for the same period last year. So far in 2024, its share price has collapsed by 32%.
    """

    news_summary = news_summary_generator(news_article)
    print(news_summary)
    
    summaries, illustrations = parser(news_summary)

    print("="*20)
    print("Summaries:")
    for summary in summaries:
        print(summary)

    print("="*20)
    print(illustrations)
    print("\nIllustrations:")
    for illustration in illustrations:
        print(illustration)

    print("="*20)
    print("\nGenerated Images:")
    generate_and_display_images(illustrations)