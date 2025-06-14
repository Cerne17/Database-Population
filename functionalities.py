from googletrans import Translator

async def translate(text):
  translator = Translator()
  translation = await translator.translate(text, dest='pt')
  return translation.text