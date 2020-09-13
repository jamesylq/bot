import discord, data, pytz
from datetime import datetime, timezone
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

client = discord.Client()
token = ""

with open('token.txt', 'r') as tokenSave:
  token = tokenSave.readlines()[0]

prefix = 'sn! ' # Study Notes! 
admins = [720259123639222286, 737557656277090395, 611513933710229504, 652849205454569493]
# Cheng, Calrence, LQ, Tim

links = data.data

alias = {
  'py': 'python',
  'el': 'english',
  'ma': 'math',
  'sci': 'science',
  'cl': 'chinese',
  'ss': 'social studies'
}


def createEmbed(*, title: str, text: str, colour: int, footer: str = None, name: str = None, thumbnail: str = None):
    embed = discord.Embed(title=title, description=text, color=colour)
    if footer is not None:
        embed.set_footer(text=footer)
    if name is not None:
        embed.set_author(name=name)
    if thumbnail is not None:
      embed.set_thumbnail(url=thumbnail)
    return embed


class word(object):
    def __init__(self, word: str):
        self.word = word

    def startswith(self, toCheck: str):
        if len(toCheck) > len(self.word):
            return False
        for n in range(len(toCheck)):
            if toCheck[n] != self.word[n]:
                return False
        return True

    def endswith(self, toCheck: str):
        if len(toCheck) > len(self.word):
            return False
        for n in range(len(toCheck)):
            if toCheck[-n - 1] != self.word[-n - 1]:
                return False
        return True

    def clearfront(self, length: int):
        if length > len(self.word):
            raise ValueError('Length inputted longer than word length')
        self.word = self.word[length:]

    def clearback(self, length: int):
        if length > len(self.word):
            raise ValueError('Length inputted longer than word length')
        self.word = self.word[:-length]
  

@client.event
async def on_ready():
  print(f'Logged in as {client.user}.')

@client.event
async def on_message(message):
  msg = word(message.content.lower())
  val = URLValidator()

  if message.author.id in admins:
    if msg.startswith(prefix + 'add '):
      msg.clearfront(len(prefix) + 4)
      subject, link, version = None, None, None
      try:
        subject, link, version = msg.word.split(', ', 3)
      except ValueError:
        await message.channel.send(f'```Error! Invalid Syntax! Correct syntax: {prefix}add <subject>, <link>, <version>```')
        return
      else:
        try:
          val(link)
        except ValidationError:
          await message.channel.send(f'```Error! Invalid Syntax! Correct syntax: {prefix}add <subject>, <link>, <version>```')
          return
        else:
          if subject in alias.keys():
            subject = alias[subject]
          elif subject not in alias.values():
            await message.channel.send(f'```Invalid subject \"{subject}\"!```')
            return
      
      now = datetime.now(tz=pytz.timezone('Asia/Singapore'))
      month = '%02d' % now.month
      day = '%02d' % now.day
      hour = '%02d' % now.hour
      minute = '%02d' % now.minute
      second = '%02d' % now.second

      if subject in links.keys():
        links[subject][version] = [link, f'{now.year}/{month}/{day} {hour}:{minute}:{second}']
      else:
        links[subject] = {version: [link, f'{now.year}/{month}/{day} {hour}:{minute}:{second}']}
      
      await message.channel.send(embed=createEmbed(title='Success', text=f'You have uploaded {version} of {subject} ( {link} )', colour=0x00ff7f))
      await client.get_user(611513933710229504).send(f'<@!611513933710229504>, <@!{message.author.id}> has uploaded {version} of {subject} at {link}.')
    
    elif msg.startswith(prefix + 'del '):
      msg.clearfront(len(prefix) + 4)
      subject, version = None, None

      try:
        subject, version = msg.word.split(', ', 2)
      except ValueError:
        await message.channel.send(f'```Error! Invalid Syntax! Correct syntax: {prefix}del <subject>, <version>```')
      else:
        if subject in alias.keys():
          subject = alias[subject]
        elif subject not in alias.values():
          await message.channel.send(f'```Invalid subject \"{subject}\"!```')
          return
      
      if version in links[subject].keys():
        await message.channel.send(embed=createEmbed(title='Success', text=f'You deleted {version} of {subject} (Link: {links[subject][version][0]}, Uploaded: {links[subject][version][1]})!', colour=0x00ff7f))
        await client.get_user(611513933710229504).send(f'<@!611513933710229504>, <@!{message.author.id}> has deleted {version} of {subject} at {links[subject][version][0]} [{links[subject][version][1]}].')
        links[subject].pop(version)
      else:
        await message.channel.send(f'```Error! Invalid Syntax! Correct syntax: {prefix}del <subject>, <version>```')        

  if msg.startswith(prefix + 'list '):
    msg.clearfront(len(prefix) + 5)
    subject = msg.word

    if subject in alias.keys():
      subject = alias[subject]
    elif subject not in alias.values():
      await message.channel.send(f'Invalid subject \"{subject}\"!')
      return
    
    txt = ''

    if subject not in links.keys():
      await message.channel.send(f'```No data found for subject \"{subject}\"!```')
    x = len(links[subject])
    for version, link in links[subject].items():
      if x == 1:
        txt += f'\n\n**Latest Version**:\n{version} - {link[0]} [{link[1]}]'
      else:
        txt += f'{version} - {link[0]} [{link[1]}]\n'
      x -= 1
    
    if txt != '':
      await message.channel.send(embed=createEmbed(title=f'Versions of {subject} notes', text=txt, colour=discord.Color.blue(), footer='Press Ctrl + P to see the document(and then you can access the bookmarks)'))
    else:
      await message.channel.send(f'```No data found for subject \"{subject}\"!```')
  
  with open('data.py', 'w') as data:
    data.write('data = ' + str(links))
  data.close()

client.run(token)
