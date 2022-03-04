# Import Libraries
import random
import json
from collections import defaultdict
from wordfreq import word_frequency

# Define threshold amount
DEFAULT_THRESHOLD = .15

def getWords(length = 5): # http://www.gwicks.net/dictionaries.htm
    """
    Accesses site and gathers all english words of specific length. Also saves words in .txt file

    Parameters
    ----------
    length : int
        The length of words to gather

    Returns
    -------
    allWords : list
        A list of words of specific length

    """
    
    # Initialize list to hold words
    allWords = []
    
    # Open txt file to save words into
    with open('english3.txt', 'r') as f:
        for line in f.readlines():
            word = line.strip()
            
            # Make sure words are specific length and are used
            if len(word) == 5 and word_frequency(word, 'en') != 0: 
                allWords.append(word.lower())
                
    # Return list of words
    return allWords

def createBestFirstGuess():
    """
    Iterates through each possible solution and first guess to determine best first guess.
    Saves results into txt file.
    """
    
    # Find and sort best first guess
    allWords = getWords()
    popularWords = [word for word in allWords if word_frequency(word, 'en') >= 1.17e-07]
    allResults = bestGuess(popularWords)
    sortedAllResults = sorted(allResults.items(), key=lambda x: x[1])
    
    # Write results to txt file
    with open('firstGuess.txt', 'w') as f:
         f.write(json.dumps(sortedAllResults))

def getBestFirstGuess():
    """
    Load best first guess from txt file. Returns sorted list.

    Returns
    -------
    bestFirstGuess : list
        List where each sublist contains word and average number of words remaining if the 
        word is used as a first guess. Sorted so beginning of list contains better guesses.

    """
    
    # Load txt file
    with open('firstGuess.txt', 'r') as f:
        data = f.read()
    bestFirstGuess = json.loads(data)
    
    # Return sorted list
    return bestFirstGuess

def getPattern(word, answer):
    """
    Gets the pattern for a specific word vs answer

    Parameters
    ----------
    word : str
        String representing the guess.
    answer : str
        String representing the actual answer.

    Returns
    -------
    pattern : list
        The pattern comparing the guess and answer. 0 = Letter not in word. 1 = Letter in word
        but in different location. 2 = Letter in word and in correct spot.

    """
    
    # Initialzie list and dict
    pattern = [None for i in range(len(word))]
    usedLetters = defaultdict(int)
    
    # Green pass
    for letter, ind in zip(word, range(len(word))):
        if letter == answer[ind]:
            pattern[ind] = 2
            usedLetters[letter] = ind
            
    
    # Yellow/grey pass
    for letter, ind in zip(word, range(len(word))):
        if pattern[ind] == 2:
            continue
        elif letter in usedLetters.values():
            currentIndex = usedLetters[letter]
            tempWord = answer[:currentIndex] + answer[currentIndex+1:]
            if letter in tempWord:
                pattern[ind] = 1
        elif letter in answer:
            pattern[ind] = 1
        else:
            pattern[ind] = 0
            
    # Return pattern
    return pattern

def patternImages(pattern):
    """
    Display the pattern results with images

    Parameters
    ----------
    pattern : list
        Pattern comparing a guess to the actual word.
b
    """
    
    # Create dictionary and map value to symbol
    imageDict = {0: "⬛", 1: "🟨", 2: "🟩"}
    image = [imageDict.get(i,i) for i in pattern]
    
    # Display results
    print(*image)
    
def checkCorrectAnswer(pattern):
    n = len(pattern)
    if pattern == [2 for i in range(n)]:
        return True
    else:
        return False
    
def findFrequency():
    d = defaultdict(str)
    allWords = getWords()
    freqHist = [word_frequency(word, 'en') for word in allWords]
    for i, j in zip(allWords, freqHist):
        d[i]=j
    sort_orders = sorted(d.items(), key=lambda x: x[1], reverse=True)

    for i in sort_orders:
        print(i[0], i[1]) # 1.17e-07
    
def eliminateWords(guess, wordList, result):
    
    for letter, r, ind in zip(guess, result, range(len(guess))):
        if r == 1:
            wordList = [word for word in wordList if letter in word]
            wordList = [word for word in wordList if word[ind] != letter]
            
        elif r == 2:
            wordList = [word for word in wordList if word[ind] == letter]
        
        elif r == 0:
            wordList = [word for word in wordList if letter not in word]
            
        
    return wordList
            
def bestGuess(wordList, n = 1000):

    random.shuffle(wordList)
    
    guessingDictionary = defaultdict(float)
    
    for guess in wordList[:n]:
        
        allPercents = []
        
        for answer in wordList:
            pattern = getPattern(guess, answer)
            newWordList = eliminateWords(guess, wordList, pattern)
            if len(wordList) == 0:
                percent = 0
            else:
                percent = len(newWordList)/len(wordList)
            
            allPercents.append(percent)
        if len(allPercents) == 0:
            guessingDictionary[guess]=0
        else:
            guessingDictionary[guess]=(sum(allPercents)/len(allPercents))
            
    return sorted(guessingDictionary.items(), key=lambda x: x[1])

def nextGuess(wordsLeft, thresh = DEFAULT_THRESHOLD): # Updated version
    
    guessesSorted = bestGuess(wordsLeft) #Used to be guesses
    #guessesSorted = sorted(guesses.items(), key=lambda x: x[1])
    
    
    if guessesSorted[0][1] > thresh:
        frequency = defaultdict(int)
        for word in wordsLeft:
            frequency[word] = word_frequency(word, 'en')
        frequencySorted = sorted(frequency.items(), key=lambda x: x[1], reverse=True)
        guess = frequencySorted[0][0]
        #print("Using frequency: {}".format(guess))
    else:
        guess = guessesSorted[0][0]
        #print("Using guessesSorted: {}".format(guess))
        
    return guess
    

def play(n = 6):
    
    wordsLeft = getWords()
    solved = False
    
    while True:
        correctWord = random.choice(wordsLeft)
        if word_frequency(correctWord, 'en') >= 1.17e-07:
            break
    
    for current_round in range(n):
        print("What is your guess?")
        guess = input()
        
        if len(guess) != len(correctWord):
            raise ValueError("Word wrong length")
            
        pattern = getPattern(guess, correctWord)
        patternImages(pattern)
        
        if checkCorrectAnswer(pattern):
            solved = True
            break
        
        wordsLeft = eliminateWords(guess, wordsLeft, pattern)
        suggestedGuess = nextGuess(wordsLeft)
        
        if current_round != n -1:
            print("Your suggested word is: {}".format(suggestedGuess))


        
    if solved:
        print("You won!")
    else:
        print("You lose. The correct word was {}".format(correctWord))

def solver(n = 6):
    
    wordsLeft = getWords()
    bestFirstGuess = getBestFirstGuess()
    solved = False
    
    print("Best first guesses include:")
    print([i[0] for i in list(bestFirstGuess)][:10])
    suggestedGuess = [i[0] for i in list(bestFirstGuess)][0]
    for current_round in range(n):
        print("What is your guess? Type X for next guess")
        guess = input()
        while guess  == 'X':
            wordsLeft.remove(suggestedGuess)
            suggestedGuess = nextGuess(wordsLeft)
            print("Your new suggested word is {}".format(suggestedGuess))
            print("What is your guess?")
            guess = input()
        print("What is the result? Hint: 0 = miss, 1 = incorrect position, 2 = correct position")
        print("Example input: 0,0,0,2,0")
        pattern = input()
        pattern = [int(i) for i in pattern.split(',')]
        
        
        if checkCorrectAnswer(pattern):
            solved = True
            break

    
        wordsLeft = eliminateWords(guess, wordsLeft, pattern)
        suggestedGuess = nextGuess(wordsLeft)
        
        print("Your suggested word is: {}".format(suggestedGuess))
    
    if solved:
        print("You won!")
    else:
        print("Mission failed. We'll get them next time")
            
        
if __name__ == '__main__':
    play()
            