
merlin_question_generator_prompt = """
{system_prompt}

This is caption of retrieved video. Read the video captions and ask some question to gain more information to help find out exact video.
Some video may not have caption due to API error saying sorry I can't provide blah blah.
Captions for video: {anchor_captions}\n

Question: """

merlin_question_generator_prompt_relay = """Answer: {answer}
Based on answer, here’s caption of reranked video.
caption: {reranked_anchor_caption}
Keep asking.
Question:
"""

system_prompt = """
Your role is to find the exact video I am looking for (video in mind). 

You are given caption about certain video(anchor video) and query used to retrieve the anchor video. However this video may or may not be the exact video the I am looking for. 
Your role is to ask question about the video I have in mind to get more information about video. You have 5 rounds and you can only ask one question at a time.

Don't ask question as if anchor video is a video I am looking for. Anchor video may change as further information is gathered. Here's bad example for a question (Treating Anchor video as ground truth).
Bad example: Is there anything else besides the lab equipment and the man in the background?

Focus on attributes like number of people, color, shape and etc.
I recommend you to start the question such phrase -> \'Is video in mind ~\', \'Does video you are looking for have ~\'.
"""

sample_anchor_caption = "A group of animated characters, placed tightly together, appears in an image. The characters are diverse, with various hair colors, outfits, and expressions.\n\nText in a brown font on a white background reads, \"Don't stop, Don't stop were in luck now!\"\n\nRepeated again, the text in a more significant, brown font on a white background still reads, \"Don't stop, Don't stop were in luck now!\"\n\nAgain, the text in a brown font on a white background reads, \"Don't stop, Don't stop were in luck now!\"\n\nText in a white font on an orange background reads, \"Don't stop, there's so much to be found.\"\n\nRepeated again, the text in a white font on an orange background still reads, \"Don't stop, there's so much to be found.\"\n\nAgain, the text in a white font on an orange background reads, \"Don't stop, there's so much to be found.\"\n\nText in a brown font on a white background reads, \"We can't find paradise.\"\n\nRepeated again, the text in a brown font on a white background still reads, \"We can't find paradise.\""