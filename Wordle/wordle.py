# Import Libraries
import random
import json
import argparse
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
    """
    
    # Create dictionary and map value to symbol
    imageDict = {0: "⬛", 1: "🟨", 2: "🟩"}
    image = [imageDict.get(i,i) for i in pattern]
    
    # Display results
    print(*image)
    
def checkCorrectAnswer(pattern):
    """
    Determins if a pattern is a correct answer

    Parameters
    ----------
    pattern : list
        List of 0,1,2 comparing a pattern to the correct answer.

    Returns
    -------
    bool
        True if guess is correct. False otherwise
    """
    
    n = len(pattern)
    if pattern == [2 for i in range(n)]:
        return True
    else:
        return False
    
def findFrequency():
    """
    Finds, sortsm and displays the frequency of words gathered from getWords()
    """
    
    d = defaultdict(str)
    allWords = getWords()
    freqHist = [word_frequency(word, 'en') for word in allWords]
    for i, j in zip(allWords, freqHist):
        d[i]=j
    sort_orders = sorted(d.items(), key=lambda x: x[1], reverse=True)

    # sort words based on frequency to find cut off for 'common' words
    for i in sort_orders:
        print(i[0], i[1]) # 1.17e-07
    
def eliminateWords(guess, wordList, result):
    """
    Elminates words from wordList based on guess and resulting pattern

    Parameters
    ----------
    guess : str
        Word guessed.
    wordList : list
        List of possible words remaining.
    result : list
        Pattern showing guess compared to actual word.

    Returns
    -------
    wordList : list
        List of updated possible words.
    """
    
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
    """
    Determines the best guesses from words remaining by iterating over remaining words
    to determine which, on average, will result in the fewest words remaining.

    Parameters
    ----------
    wordList : list
        List of possible words remaining.
    n : int, optional
        Number of words to iterate through. The default is 1000.

    Returns
    -------
    List
        List of lists, where each sublists first index is the word, and the second index
        is the average percent of words remaining if that guess is used

    """

    # Initialize and randomize words
    random.shuffle(wordList)    
    guessingDictionary = defaultdict(float)
    
    # Iterate through n words as a guess
    for guess in wordList[:n]:
        
        allPercents = []
        
        # Iterate through each word as an answer
        for answer in wordList:
            
            # Determine average number of words remaining after given guess and correct word
            pattern = getPattern(guess, answer)
            newWordList = eliminateWords(guess, wordList, pattern)
            if len(wordList) == 0:
                percent = 0
            else:
                percent = len(newWordList)/len(wordList)
            allPercents.append(percent)
            
        # Add guess and average percent of words remaining to dictionary
        if len(allPercents) == 0:
            guessingDictionary[guess]=0
        else:
            guessingDictionary[guess]=(sum(allPercents)/len(allPercents))
            
    # Return best words to guess sorted with percents
    return sorted(guessingDictionary.items(), key=lambda x: x[1])

def nextGuess(wordsLeft, thresh = DEFAULT_THRESHOLD):
    """
    Determines guess based off of average percent of word the guess eliminates, and the 
    threshold of words remaining, based off of the DEFAULT_THRESHOLD

    Parameters
    ----------
    wordsLeft : list
        List of possible words remaining.
    thresh : float, optional
        The relative threshold of words elminated from wordsLeft, if guess is used.
        The default is DEFAULT_THRESHOLD.

    Returns
    -------
    guess : str
        The suggested guess.
    """
    
    guessesSorted = bestGuess(wordsLeft)
    
    # If percent of words elminated is greater than threshold, then use word frequency
    if guessesSorted[0][1] > thresh:
        frequency = defaultdict(int)
        for word in wordsLeft:
            frequency[word] = word_frequency(word, 'en')
        frequencySorted = sorted(frequency.items(), key=lambda x: x[1], reverse=True)
        guess = frequencySorted[0][0]
        
    # Otherwise, suggest word that, on average, eliminates the most words
    else:
        guess = guessesSorted[0][0]
        
    return guess
    

def play(n = 6):
    """
    Play a game of Wordle. Answer is randomly selected, and suggestions are given throughout
    of the word to use.

    Parameters
    ----------
    n : int, optional
        The number of rounds to find the correct word. The default is 6.

    Raises
    ------
    ValueError
        If guess isn't same length as the correct word.
    """
    
    # Initialize
    wordsLeft = getWords()
    solved = False
    
    # Find a word with a frequency greater than the given threshold
    while True:
        correctWord = random.choice(wordsLeft)
        if word_frequency(correctWord, 'en') >= 1.17e-07:
            break
    
    # Play n rounds
    for current_round in range(n):
        
        # Take input
        print("What is your guess?")
        guess = input()
        
        # Chekc input
        if len(guess) != len(correctWord):
            raise ValueError("Word wrong length")
            
        # Find and display pattern
        pattern = getPattern(guess, correctWord)
        patternImages(pattern)
    
        # Determine if player won
        if checkCorrectAnswer(pattern):
            solved = True
            break
        
        # Determine a word to suggeset
        wordsLeft = eliminateWords(guess, wordsLeft, pattern)
        suggestedGuess = nextGuess(wordsLeft)
        
        # Give suggestion if not final round
        if current_round != n -1:
            print("Your suggested word is: {}".format(suggestedGuess))

    # Display results
    if solved:
        print("You won!")
    else:
        print("You lose. The correct word was {}".format(correctWord))

def solver(n = 6):
    """
    Solves a game of wordle by giving best guess suggestions

    Parameters
    ----------
    n : str, optional
        The number of rounds to find the correct word. The default is 6.
    """
    
    # Initialize
    wordsLeft = getWords()
    bestFirstGuess = getBestFirstGuess()
    solved = False
    
    # Display best initial guests
    print("Best first guesses include:")
    print([i[0] for i in list(bestFirstGuess)][:10])
    suggestedGuess = [i[0] for i in list(bestFirstGuess)][0]
    
    # Iterate though each round
    for current_round in range(n):
        
        # Take input for guess
        print("What is your guess? Type X for next guess")
        guess = input()
        
        # Ask for different suggested word if possible
        while guess  == 'X':
            wordsLeft.remove(suggestedGuess)
            suggestedGuess = nextGuess(wordsLeft)
            print("Your new suggested word is {}".format(suggestedGuess))
            print("What is your guess?")
            guess = input()
            
        # Input results of guess
        print("What is the result? Hint: 0 = miss, 1 = incorrect position, 2 = correct position")
        print("Example input: 0,0,0,2,0")
        pattern = input()
        pattern = [int(i) for i in pattern.split(',')]
        
        # Check if answer is correct
        if checkCorrectAnswer(pattern):
            solved = True
            break

        # Give new suggested guess
        wordsLeft = eliminateWords(guess, wordsLeft, pattern)
        suggestedGuess = nextGuess(wordsLeft)
        print("Your suggested word is: {}".format(suggestedGuess))
    
    # Display results
    if solved:
        print("You won!")
    else:
        print("Mission failed. We'll get them next time")
 
        
if __name__ == '__main__':
    
    # Required command line argument
    parser= argparse.ArgumentParser(description='Wordle Analysis')
    parser.add_argument('command', metavar='<command>',choices=['solve', 'play'],
                        type=str,help='Type "solve" for help solving a wordle. Type "play" to play.')
    
    # Complete setting up argument parsing
    parse=parser.parse_args()  
    
    if parse.command == 'solve':
        solver()
    elif parse.command == 'play':
        play()
