#This program parses the application page on Gugle Plai and displays rating, raised by users.
# Also calculates how much you need to put 5 ratings even to average applications has reached a certain size

import urllib.request
from html.parser import HTMLParser
import sys

class Stack:
    def __init__(self):
        self.arr = []

    def push(self, val):
        self.arr.append(val)

    def pop(self):
        if len(self.arr) > 0:
            val = self.arr[len(self.arr)-1]
            self.arr = self.arr[:len(self.arr)-1]
            return val
        return None
    def top(self):
        if len(self.arr) > 0:
            return self.arr[len(self.arr)-1]
        return None
    def empty(self):
        return (len(self.arr) == 0)




class NebulaRatingParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.starParsing = False
        self.ratingParsing = False
        self.starStack = Stack()
        self.ratingStack = Stack()
        self.ratingDict = {}

    def attrIsStarHeader(self, str):
        return (str == 'rating-bar-container five' or
                str == 'rating-bar-container four' or
                str == 'rating-bar-container three' or
                str == 'rating-bar-container two' or
                str == 'rating-bar-container one' )

    def waitForStarParsing(self, attrName, attrValue):
        return (attrName == 'class' and
                self.attrIsStarHeader(attrValue) and
                self.starStack.empty())

    def waitForRatingParsing(self, attrName, attrValue):
        return (self.starParsing and
                not self.starStack.empty() and
                attrName == 'class' and
                attrValue == 'bar-number' and
                self.ratingStack.empty())

    def handle_starttag(self, tag, attrs):
        #print('Start tag:', tag)
        for attr in attrs:
            if self.waitForStarParsing(attr[0], attr[1]):
                self.starParsing = True
            if self.waitForRatingParsing(attr[0], attr[1]):
                self.ratingParsing = True

    def handle_endtag(self, tag):
        #print('End tag  :', tag)
        if self.starParsing and self.ratingParsing and not self.starStack.empty() and not self.ratingStack.empty():
            self.ratingDict[self.starStack.pop()] = self.ratingStack.pop()
            self.starParsing = False
            self.ratingParsing = False

    def handle_data(self, data):
        #print('Data     :', data)
        if self.starParsing and self.starStack.empty():
            try:
                star = int(data)
                self.starStack.push(star)
            except ValueError as e:
                pass
        if self.ratingParsing and self.starParsing and not self.starStack.empty() and self.ratingStack.empty():
            try:
                data = data.replace(' ', '')
                data = data.replace(',', '')
                lst = data.split(' ')
                str = ''
                for s in lst:
                    if s.strip() != '':
                        str += s.strip()
                rating = 0
                if str != '':
                    #print('parsing: ', str)
                    rating = int(str)

                self.ratingStack.push(rating)
            except ValueError as e:
                pass

    def handle_comment(self, data):
        pass
        #print('Comment  :', data)


    def handle_entityref(self, name):
        pass
        #c = chr(name2codepoint[name])
        #print('Named ent:', c)

    def handle_charref(self, name):
        pass
        # if name.startswith('x'):
        #     c = chr(int(name[1:], 16))
        # else:
        #     c = chr(int(name))

    def handle_decl(self, decl):
        pass
        # print('Decl    :', decl)


def getTotalRatingCount(ratingDict):
    return sum([rating for rating in ratingDict.values()])


def getAverageRating(ratingDict):
    totalRatings = getTotalRatingCount(ratingDict)
    avgRating = 0
    for (star, rating) in ratingDict.items():
        avgRating += star * (rating / totalRatings)
    return avgRating

def clamp01(t, minVal, maxVal):
    return max(min(t, maxVal), minVal)

def getNumberOfFiveStarRatingForAverage(ratingDict, targetAverage):
    countToAdd = 0
    targetAverage = clamp01(targetAverage, 0, 5)
    while getAverageRating(ratingDict) < targetAverage:
        ratingDict[5] += 1
        countToAdd += 1
        if countToAdd >= 1000000:
            break
    return countToAdd

url = 'https://play.google.com/store/apps/details?id=com.depielco.no'
if len(sys.argv) > 1:
    url = sys.argv[1]

print('check: ', url)

f = urllib.request.urlopen(url)
parser = NebulaRatingParser()
parser.feed(f.read().decode('utf-8'))

keyStars = parser.ratingDict.keys()
keyStars = sorted(keyStars, reverse=True)
for key in keyStars:
    print('{:5s}: {:5d}'.format('*' * key, parser.ratingDict[key]))

print()
print('Average: {:5.2f}'.format(getAverageRating(parser.ratingDict)))
print()


targetRating = 4.0
i = 0
while i <= 10:
    countToAdd = getNumberOfFiveStarRatingForAverage(parser.ratingDict.copy(), targetRating)
    print('For reach rating: {:5.2f} lacks {:5d} five stars'.format(targetRating, countToAdd))
    targetRating += 0.1
    i += 1
    #print(targetRating)

print('done!')





