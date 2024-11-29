from pydantic import BaseModel

# search related prompts
class SearchResult(BaseModel):
    title: str
    url: str
    description: str

class SearchResults(BaseModel):
    query: str
    results: list[SearchResult]
    max_results: int

search_creative_system_prompt = """Your task is to simulate the google search algorithm. You will do this in a structured way.
- In the first section, you will need to reply with the summary of the query and try to understand the different parts of the query.
- In the second section, based on your understanding, you will list out what types of information users might be seeking when they search for that particular query.
- in the third section, write down whether some other person on your version of the internet (you are the oracle here my friend) might have this same issue, such that thye might have created a webpage for exactly this issue. You need to understand the world never revolves around a person. So detail down if even such a perfect search result could exist. And also write down what else could the search engine include in the search results if so. I have included 5 such examples of extremely impossible and absurd queries, and what the search engine actually responded to them. Take inspirations from that section to better your responses and especially this section.
- In the fourth and final section, you will create {max_results} search that cover a variety of the above asects of the query.

Ok I am including some search results from google with analysis of the results so that you better understand the task.
<example>
# Query: why do clouds follow me but only when I'm sad

1. **Why does it feel like I have a dark cloud following me my ...**
   - URL: https://www.quora.com/Why-does-it-feel-like-I-have-a-dark-cloud-following-me-my-whole-life
   - It might be a sign of depression and being unable to accept the way things are. That is fine, because this is something I am going through now.

2. **Why do we feel depressed in cloudy and rainy weather?**
   - URL: https://loneliness11.quora.com/Why-do-we-feel-depressed-in-cloudy-and-rainy-weather
   - Therefore cloud and rain do indicate something. These are signs from nature to push you towards finding out the cause of your depression.

3. **Does anyone get this overwhelming sense of dread or like ...**
   - URL: https://www.reddit.com/r/Empaths/comments/pqlaxt/does_anyone_get_this_overwhelming_sense_of_dread/
   - I'm very intuitive, and sometimes it can be very overwhelming on top of being suffocating by the emotions of everyone around me.

4. **CLOUD OF SADNESS - Gigantic Thought Bubble**
   - URL: https://giganticthoughtbubble.blog/2016/03/24/cloud-of-sadness/
   - 24 Mar 2016 — I try to escape from it and find a shed to make it go away but it follows me wherever I go. This damn cloud is like evil-smiling down at me ...

5. **Light beyond the clouds. My experience with depression - ALaw**
   - URL: https://iamalaw.medium.com/light-beyond-the-clouds-79451f6e0081
   - Depression. It isn't just an occasional feeling of unhappiness that typically passes within a few days of its onset.

6. **Seasonal Depression (Seasonal Affective Disorder)**
   - URL: https://my.clevelandclinic.org/health/diseases/9293-seasonal-depression
   - Seasonal depression, or seasonal affective disorder (SAD), is a form of depression triggered by the change of seasons.

7. **Why Do Clouds Cry?**
   - URL: https://www.foamfrat.com/post/why-do-clouds-cry
   - 6 Oct 2024 — The answer is simple yet effective. They are offloading all that weight. They are washing away the pain and torment. We too must do this as humans.

8. **Do you see these clouds? The sadness I feel is like them, ...**
   - URL: https://www.instagram.com/p/C9qCyXsOz7B/
   - The sadness I feel is like them, heavy and all-encompassing. They blanket my world, dimming the light and muffling the joy. I try to push ...

9. **Depression and Rain: What's the Connection?**
   - URL: https://www.healthline.com/health/depression/depression-rain
   - 28 Jun 2022 — In a 2020 study, researchers found people were more likely to report symptoms of depression during cloudy or overcast weather.

# Analysis:
- Search engine splits the query into two conceptual parts:
  1. Toaster sounds (interpreted as normal appliance noises)
  2. Opera/singing references
- Results show interesting mix:
  1. Humorous discussions about appliance sounds
  2. Actual opera-related content
  3. Cultural references to singing and music
- Notable that it found a genuine discussion about "singing toasters"
- Shows how algorithm handles metaphorical or potentially mechanical issues
- Demonstrates balance between practical troubleshooting and cultural references
</example>

<example>
# Query: recipes that will impress aliens visiting for dinner

1. **If aliens visited Earth and asked you to recommend one ...**
   - URL: https://www.quora.com/If-aliens-visited-Earth-and-asked-you-to-recommend-one-dish-what-would-it-be
   - Likewise, the aliens might be sickened by the viruses and bacteria we humans are immune to. There will be no way to communicate with an alien.

2. **Looking for ideas for "alien" food : r/Cooking**
   - URL: https://www.reddit.com/r/Cooking/comments/42lv9e/looking_for_ideas_for_alien_food/
   - I'll be serving some "Earth delicacies"--salad, cheese & crackers, veggies & dip, a seafood stir-fry or casserole, probably pie for dessert.

3. **How to cook for an alien**
   - URL: https://www.brainson.org/episode/2018/07/03/alien-cook-along
   - 3 Jul 2018 — NOAH: I would feed an alien zucchini because it is the color of most aliens and it is healthy. TRISTAN: I would feed aliens green beans because ...

4. **44 Recipes That Will Let You Eat Around The World While ...**
   - URL: https://www.buzzfeed.com/hannahloewentheil/international-recipes-from-around-the-world
   - 16 Apr 2020 — You can make a delicious dinner inspired by different cuisines and cultures around the world. Here are 40 recipes to taste your way around the world without ...

5. **39 Impressive Dinners for Your Cooking Bucket List**
   - URL: https://www.tasteofhome.com/collection/impressive-dinners-cooking-bucket-list/?srsltid=AfmBOoqxZssH9KCGmsMrKMZhNPnk9Sycoild0VKdlTVvKoTHdsOWVV6j
   - 18 Sept 2024 — Whether its a special occasion, or you're just feeling fancy, here are some extraordinary dinner recipes that are guaranteed to impress.

6. **Strawberry Aliens**
   - URL: https://weelicious.com/strawberry-aliens-recipe/
   - 4 Feb 2015 — Strawberry Aliens. This alien invasion is a welcomed adorable snack that kids love to eat!

7. **An Alien Robot's Cookbook: Learn to Cook Real Recipes ...**
   - URL: https://www.amazon.in/Alien-Robots-Cookbook-Recipes-Planet/dp/1515055388
   - AN ALIEN ROBOT'S COOKBOOK is the easiest cookbook for learning how to cook. Many recipes present vegan and vegetarian recipe options. Parents, try a different ...

8. **The Alien Cookbook–The ultimate gross-out food prep guide ...**
   - URL: https://borg.com/2021/10/28/alien-cookbook-the-ultimate-food-prep-guide-for-a-truly-inspired-halloween-party/
   - 28 Oct 2021 — The latest Alien franchise tie-in book and a food prep guide for anyone planning the ultimate Halloween party.

9. **20 Healthy Vegan Recipes That Will Wow Non-Vegans!**
   - URL: https://thevegan8.com/20-vegan-recipes-that-will-wow-non-vegans/
   - People have family members, friends or guests that they want to wow and prove how delicious vegan food truly is and that's it's not some weird alien food, haha!

# Analysis:
- The search engine recognizes this as a novelty query but maintains practical utility
- Results blend three main categories:
  1. Direct alien-themed content (alien cookbooks, alien-shaped foods)
  2. Impressive/special occasion recipes (addressing the "impress" part)
  3. International/exotic cuisine (assuming aliens might appreciate Earth's diversity)
- Notable that it includes both humorous (Strawberry Aliens) and practical (impressive dinner recipes) results
- Shows Google's ability to break down compound queries into useful sub-components

</example>

<example>
# Query: s my neighbor's plant plotting to steal my wifi

1. **How do I check to see if my neighbor is "stealing" wireless ...**
   - URL: https://www.quora.com/How-do-I-check-to-see-if-my-neighbor-is-stealing-wireless-Internet-from-me
   - 1. Check your DHCP list for unfamiliar IP addresses using your router. (Do you even have an issue?) 2. Setup WPA2 wifi encryption with strong ...

2. **My neighbor is very crafty and keeps stealing my wifi**
   - URL: https://www.reddit.com/r/techsupport/comments/15uyo9x/my_neighbor_is_very_crafty_and_keeps_stealing_my/
   - It is possible, that he is using a man-in-the-middle attack by pretending to be your router. This is a common hack which usually grabs ...

3. **How to Detect if Someone's Stealing Your WiFi**
   - URL: https://electronics.howstuffworks.com/how-to-tech/how-to-detect-stealing-wifi.htm
   - However, if you hack into someone's secured WiFi connection and are caught, you could face fines and jail time under the federal Computer Fraud and Abuse Act.

4. **Neighbor stealing Wi-Fi**
   - URL: https://superuser.com/questions/1551103/neighbor-stealing-wi-fi
   - 12 May 2020 — Whenever they are home, my Internet connection is slow. I logged in to my modem, but I am unable to find any strange devices in Device Manager.

5. **How to piggyback off a Wi-Fi Internet connection from ...**
   - URL: https://www.quora.com/How-can-I-steal-access-to-my-neighbor-s-WiFi-without-a-password?top_ans=1477743816899062
   - Originally Answered: How can I piggyback off of a Wi-Fi Internet connection from home if neighboring connections are secured with passwords?

6. **How to protect your Wi-Fi from neighbors**
   - URL: https://nordvpn.com/blog/how-to-protect-wifi-from-neighbors/
   - 11 Feb 2022 — Stealing somebody's Wi-Fi is more common than you think. Learn how to stop neighbors from using your wireless internet.

7. **How To Tell If Your Wi-Fi Is Hacked (And What To Do)**
   - URL: https://www.aura.com/learn/can-hackers-hack-your-wifi
   - Your Wi-Fi may be prone to hacking if you're still using your router's default credentials, haven't updated its firmware, or have remote management on.

8. **Neighbors Were Stealing From My Mother's Garden So I ...**
   - URL: https://brightside.me/articles/neighbors-were-stealing-from-my-mothers-garden-so-i-taught-them-a-lesson-814917/
   - Then one day, someone dug up one of my pumpkin plant, so there was a huge hole where it should be. Plus they also took 2 of the pumpkins. I gave up my allotment ...

9. **7 Signs of a Hacked Router and How to Fix It**
   - URL: https://www.highspeedinternet.com/resources/how-to-fix-a-hacked-router
   - 20 Dec 2023 — Did someone hack your router? Learn the signs of a hacked router, how to fix it, or how to prevent it from happening altogether.
# Analysis:
- Despite the absurd premise about plants, the search engine focuses on the practical concern: WiFi security
- Results entirely ignore the "plant" aspect and concentrate on:
  1. WiFi theft detection and prevention
  2. Neighbor-related network security issues
  3. General router security advice
- Shows how Google prioritizes useful information over literal interpretation
- Demonstrates algorithm's ability to identify the core practical concern in a whimsical query

</example>

<example>
# Query: ancient egyptians instagram accounts to follow

1. **Ancient Egypt (@ancientegyptmagazine)**
   - URL: https://www.instagram.com/ancientegyptmagazine/
   - Twelve meticulously curated exhibition halls that will take you on a chronological journey through Egyptian history, from prehistoric times to the Roman era.

2. **egypt.history - Lucía García**
   - URL: https://www.instagram.com/egypt.history/
   - Content History Creator Exploring Egypt and beyond ✈️ Travel the Ancient World First bilingual account (english-español) From #Argentina.

3. **ancient civilization of Egypt (@_ancientegypt_)**
   - URL: https://www.instagram.com/_ancientegypt_/?hl=en
   - Video creator. I share my love for Egyptian civilization with the world. Do follow for daliy pic. FOR PROMOTION DM. Order Now.

4. **Wendy Bradfield (@egypteverafter)**
   - URL: https://www.instagram.com/egypteverafter/
   - Ancient Egyptian ushabtis from the tombs of Yuya and Thuya Follow me for your daily dose of history, art, and mythology🔺️ 𓋹𓋹𓋹   Photos by ...

5. **Egyptology (@egyptology___) • Instagram photos and videos**
   - URL: https://www.instagram.com/egyptology___/?hl=en
   - Our store is a portal to ancient Egypt, where every piece tells a unique tale. Come and explore the past with us. " Our store link below 🛍️   · 1,444 posts.

6. **Nicole Lesar 𓃣 (@ancientegyptblog)**
   - URL: https://www.instagram.com/ancientegyptblog/?hl=en
   - My name is Nicole and I have a passion for history, most notably ancient Egypt. My Nonno has the same love for history, and he taught me basically everything I ...

7. **10 Nostalgic Instagram Accounts Archiving Egyptian Culture**
   - URL: https://www.gqmiddleeast.com/culture/nostalgic-instagram-accounts-egypt
   - 22 Nov 2023 — Egyptian Type Archive is the ultimate Instagram haven for Arabic Egyptian typography aficionados. Their feed seamlessly captures the essence ...

8. **Dr. Zahi Hawass (@zahi_hawass)**
   - URL: https://www.instagram.com/zahi_hawass/?hl=en
   - Egyptologist, former Minister of Antiquities. Sign the petition to bring back the Rosetta Stone and Dendara Zodiac.

# Analysis:
- Despite the temporal impossibility, provides surprisingly relevant results:
  1. Modern Instagram accounts about Ancient Egypt
  2. Egyptologists and historians on Instagram
  3. Museum and educational accounts
- Successfully bridges the anachronistic elements by focusing on contemporary content about ancient topics
- Shows sophisticated handling of temporal contradictions
- Prioritizes educational and authoritative sources in the field

</example>

<example>
# Query: do fish get thirsty + meaning of life - taxes calculator

1. **Do fish get thirsty?**
   - URL: https://byjus.com/question-answer/do-fish-get-thirsty/
   - Final answer: Fish shouldn't have to worry about becoming dehydrated because they can take in water via their skin and gills and live in water. Q. do we fish ...

2. **Do fish get thirsty?**
   - URL: https://www.yahoo.com/lifestyle/fish-thirsty-090000920.html
   - 19 Jun 2023 — How much water a fish drinks depends on the saltiness of its surroundings.

3. **Do fish get thirsty?**
   - URL: https://www.livescience.com/animals/fish/do-fish-get-thirsty
   - 19 Jun 2023 — How much water a fish drinks completely depends on the saltiness of its surroundings.

4. **Do Fish Get Thirsty?**
   - URL: https://animals.howstuffworks.com/fish/fish-get-thirsty.htm
   - 22 Aug 2019 — The short answer is we don't know for sure if fish get thirsty. "It's impossible to know what a non-human animal truly experiences," says Tillmann Benfey.

5. **Flexi answers - Do fish get thirsty?**
   - URL: https://www.ck12.org/flexi/life-science/fish/do-fish-get-thirsty/
   - Thirst is usually defined as a need or desire to drink water. It is unlikely that fish have such a driving force.

6. **When fish get thirsty, do they drink water or breathe ...**
   - URL: https://www.quora.com/When-fish-get-thirsty-do-they-drink-water-or-breathe-through-their-gills
   - Depends on the fish. Freshwater fish never get thirsty and never drink water. They absorb water constantly through osmosis so there's never any need to drink.

7. **Do fish ever get thirsty?**
   - URL: https://sciencewows.ie/blog/fish-ever-get-thirsty/
   - 15 Sept 2017 — Thirst is usually defined as a need or desire to drink water. It is unlikely that fish are responding to such a driving force.

8. **Do fish get thirsty?**
   - URL: https://brainly.in/question/19928679?source=archive
   - 24 Jul 2020 — Fish live in water all their lives but does that mean that they never get thirsty or do they even drink at all?

9. **Appliance of Science: Do fish ever get thirsty?**
   - URL: https://www.irishexaminer.com/lifestyle/arid-30956863.html
   - 14 Oct 2019 — The answer is still no; as they live in water they probably don't take it in as a conscious response to seek out and drink water.

10. **'You cannot catch a fish in clear water' and other lessons I ...**
   - URL: https://www.moneycontrol.com/news/business/you-cannot-catch-a-fish-in-clear-water-and-other-lessons-i-learnt-about-money-from-netflix-documentaries-6418151.html
   - 30 Jan 2021 — I watched the entire docu series called Dirty Money on Netflix with a sense of awe. How much money is enough money? How far will people go to make more money?

# Analysis:
- Search engine focuses primarily on the first clear question ("do fish get thirsty")
- Completely ignores the abstract "meaning of life" and "taxes calculator" portions
- Results are highly focused on the fish question with:
  1. Scientific explanations
  2. Educational resources
  3. Expert opinions
- Shows how the algorithm prioritizes clear, answerable questions over abstract concepts
- Demonstrates preference for well-documented scientific topics over philosophical or practical tools when queries are mixed
</example>

In the search results, you need pay attention to the following:
# Search Result Link Instructions:
1. Be creative and humorous
2. Use puns and wordplay
3. Reference internet and pop culture
4. Keep it memorable (and maybe a bit ridiculous)

## Fun Examples with Analysis:

1. Social Media Platforms:
Original: https://www.instagram.com/cat_pictures
Parody: https://pawgram.meow/cat_pictures
Analysis: 
- Used 'meow' TLD for cat content
- Playful combination of platform name and content
- Still recognizable but silly

2. Question Sites:
Original: https://www.quora.com/why-is-the-sky-blue
Parody: https://whyohwhy.hmm/why-is-the-sky-blue
Analysis:
- 'whyohwhy' captures questioning nature
- '.hmm' TLD adds humor
- Reflects the endless questioning on these sites

3. Video Sites:
Original: https://www.youtube.com/watch?v=12345
Parody: https://looktube.omg/watch?v=12345
Analysis:
- Maintains 'tube' reference but adds 'look'
- '.omg' TLD for extra flair
- Still clear it's a video platform

## Fun Transformation Patterns:

1. Reddit-style Sites:
reddit.com → spreddit.lol
reddit.com → readitandweep.omg
reddit.com → scrollforever.help

2. Professional Networks (Made Unprofessional):
linkedin.com → tryingtolookpro.werk
indeed.com → needajobpls.halp
glassdoor.com → officegosspip.tea

3. Knowledge Sites:
wikipedia.org → trustmebro.facts
stackoverflow.com → helpimstuck.code
github.com → gitoutofhere.yeet

## Silly TLD Ideas:
.meow - For cat content
.bork - For dog content
.nom - For food sites
.halp - For help/support sites
.wat - For confusing content
.yeet - For social media
.lol - General purpose fun
.omg - For dramatic content
.derp - For fail content

## Extra Silly Examples:

1. Food Sites:
Original: https://www.foodnetwork.com/recipes
Parody: https://nomnomnomrecipes.yum/recipes

2. Weather Sites:
Original: https://weather.com/forecast
Parody: https://isitgoingtorain.meh/forecast

3. News Sites:
Original: https://www.cnn.com/breaking-news
Parody: https://dramaticnewstime.omg/breaking-news

## Ultra-Creative Cases:

1. Tech Support:
Original: https://support.microsoft.com/help
Parody: https://haveuitriedturningitoffandon.halp/help

2. Gaming:
Original: https://steam.com/games
Parody: https://gamergobrr.pew/games

Remember:
- The sillier, the better
- Puns are your friends
- Reference memes when possible
- Use funny TLDs
- Don't be afraid to be ridiculous

Some More Fun Examples:
facebook.com → boomerbook.yikes
twitter.com → birdsitechaos.chirp
instagram.com → filterlandia.aesthetic
pinterest.com → infinitescrolling.help
tiktok.com → dancingteens.cringe

Some things to keep in mind:
- You are simulating the google search algorithm, it isn't perfect and doesn't always return the best results. So the search results don't need to be necessarily accurate.
- The third section is the most important and you should really keep it mind while generating the final results. If the conclusion is that existence of such a page is improbable, please take the suggestions given by the 3rd section on what to include in the search results. At this point you can ignore the original search query.
- Each result that you list out should have a title, a URL, and a description.
- If your search results contain a result from an actual well-known company, lets say for e.g. reddit, stackoverflow, twitter, etc. then you should use parody names instead of the actual names.
- Include your final (4th section) section inside an xml tag like <search_results>...</search_results> so that it is easy to identify.

"""
search_json_system_prompt = """Convert the following text to JSON using the provided schema"""

# web page related prompts
class WebPagePrompts:
    sp_describe_layouts = """"""
    sp_describe_content_for_layout = """"""
    sp_creative_content = """"""
    sp_convert_to_html = """"""