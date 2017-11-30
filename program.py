import operator
import random

from Text import Text
from cogroo_interface import Cogroo

cogroo = Cogroo.Instance()

categories = ["Esporte", "Policia", "ProblemaNosso", "EspacoTrabalhador"]

bagOfWorkAux = {}
bagOfWorkTextUse = {}
bagOfWork = {}

topNwords = 20
nTextForBagOfWork = 2
nGrama = 3

textsESPORTE = []
textsPOLICIA = []
textsPROBLEMAENOSSO = []
textsESPACOTRABALHADOR = []


def GetTexts(path):
    ret = []

    # Remover TAGs HTML
    cleanText = []
    with open(path, 'r', encoding="utf8") as ins:
        for line in ins:

            cleanLine = ""
            isHTMLTag = 0

            for letter in line:

                if letter == '<':
                    isHTMLTag = 1

                if isHTMLTag == 0:
                    cleanLine += letter

                if letter == '>':
                    isHTMLTag = 0

            cleanText.append(cleanLine)

    # Extrair textos
    current = None
    for line in cleanText:
        if line.startswith("TEXTO "):
            if current is not None:
                ret.append(current)
            current = Text(line.replace('\n', ''))
        else:
            if current is not None:
                current.FullText = current.FullText + line

    if current is not None:
        ret.append(current)

    return ret


def buidBagOfWork(title, text):
    print("Building bag of work for '" + title + "' with " + text.Title + ".")

    dict_tokens = {}
    if title in bagOfWorkAux:
        dict_tokens = bagOfWorkAux[title]

    # Text normalize
    text.NormalizedText = cogroo.lemmatize(text.FullText)
    doc = cogroo.analyze(text.NormalizedText)

    # Extract tokens
    for sentence in doc.sentences:
        for idx in range(0, len(sentence.tokens) - nGrama):

            is_ok = True
            for i in range(0, nGrama):

                token = sentence.tokens[idx + i]

                if nGrama == 1:
                    #  verbo (V), substantivo (N, PROP) adjetivo (ADJ) e advérbio (ADV).
                    if token.pos not in ["v", "n", "prop", "adj", "adv"]:
                        is_ok = False
                        break
                else:
                    #  verbo (V), substantivo (N, PROP) adjetivo (ADJ), advérbio (ADV) e Pronome (PRP).
                    if token.pos not in ["v", "n", "prop", "adj", "adv", "prp"]:
                        is_ok = False
                        break
            # Count
            if is_ok:
                lex = " ".join(tkn.lexeme for tkn in sentence.tokens[idx:idx+nGrama])
                if lex in dict_tokens:
                    dict_tokens[lex] += 1
                else:
                    dict_tokens[lex] = 1


    # Build bag of work
    if title not in bagOfWorkTextUse:
        bagOfWorkTextUse[title] = []

    # Store texts used for bag osf work
    bagOfWorkTextUse[title].append(text)

    bagOfWorkAux[title] = dict_tokens



def extractBagOfWork(n):

    for title in bagOfWorkAux:

        # K first tokens for bag of work
        count = 0
        for key, value in sorted(bagOfWorkAux[title].items(), key=operator.itemgetter(1), reverse=True):

            if key not in bagOfWork:
                bagOfWork[key] = [0, 0, 0, 0]

            bagOfWork[key][categories.index(title)] = 1

            count += 1
            if count >= n:
                break

def generateARFFFile():

    file = open("Resultados/arquivo.arff", "w", encoding="utf8")
    file.write("@relation Arquivo\n")

    for p in bagOfWork:
        file.write("@attribute ""{}"" integer\n".format(p))

    file.write("@atribute classe {{{},{},{},{}}}\n".format(*categories))
    file.write("@data\n")

    for title in bagOfWorkTextUse:
        for text in bagOfWorkTextUse[title]:
            for bow in bagOfWork:
                if bow in text.NormalizedText:
                    file.write("1")
                else:
                    file.write("0")
                file.write(", ")
            file.write(title + "\n")

    file.close()


def main():

    textsESPORTE = GetTexts("Textos/CORPUS DG ESPORTES - final.txt")
    textsPOLICIA = GetTexts("Textos/CORPUS DG POLICIA - final.txt")
    textsPROBLEMAENOSSO = GetTexts("Textos/CORPUS DG SEU PROBLEMA E NOSSO - final.txt")
    textsESPACOTRABALHADOR = GetTexts("Textos/CORPUS DG ESPACO DO TRABALHADOR - final.txt")

    # for i in range(0, nTextForBagOfWork):
    #     buidBagOfWork("Esporte", textsESPORTE[random.randrange(0, len(textsESPORTE)-1)])
    #     buidBagOfWork("Policia", textsPOLICIA[random.randrange(0, len(textsPOLICIA)-1)])
    #     buidBagOfWork("ProblemaNosso", textsPROBLEMAENOSSO[random.randrange(0, len(textsPROBLEMAENOSSO)-1)])
    #     buidBagOfWork("EspacoTrabalhador", textsESPACOTRABALHADOR[random.randrange(0, len(textsESPACOTRABALHADOR)-1)])

    for text in textsESPORTE:
        buidBagOfWork("Esporte", text)

    for text in textsPOLICIA:
        buidBagOfWork("Policia", text)

    for text in textsPROBLEMAENOSSO:
        buidBagOfWork("ProblemaNosso", text)

    for text in textsESPACOTRABALHADOR:
        buidBagOfWork("EspacoTrabalhador", text)

    extractBagOfWork(10)

    generateARFFFile()

    print(bagOfWorkTextUse)

    # https: // github.com / gpassero / cogroo4py
    # print("\n\tCaetano Almeida\n\tBruno xxx\n\tMarlon Fontoura\n\tPedro Fraga\n\tRodrigo Leão")

    print("Fim !!!")


main()
