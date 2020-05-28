import pymorphy2
morph = pymorphy2.MorphAnalyzer()

keywords = []
with open('keywords.txt', encoding = 'utf-8') as file:
    keywords = file.read().splitlines()
keywords = [morph.parse(word)[0].lexeme for word in keywords]
keywords = ''.join(str(keywords))
with open('wordforms.txt', 'w', encoding = 'utf-8') as g:
    for word in keywords:
        g.write(word)
    

    
    
