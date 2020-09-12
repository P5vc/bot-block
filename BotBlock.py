from PIL import Image , ImageFont , ImageDraw
from secrets import choice
from random import randint

customText = ''

textLength = 5

width = 600
height = 250

charset = 'abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'

fonts = ['fonts/Ballbase.ttf' , 'fonts/GiantRobotArmy-Medium.ttf' , 'fonts/Manustype.ttf' , 'fonts/NANOTYPE.ttf' , 'fonts/PixelGrunge.ttf' , 'fonts/Reappeat.ttf' , 'fonts/Savior1.ttf' , 'fonts/Thruster-Regular.ttf' , 'fonts/To The Point.ttf']

def getTextAndAtts():
	length = textLength
	if (customText):
		length = len(customText)

	sectorSize = int(width / length)

	charsAndAtts = []

	for i in range(length):
		charList = []

		if (customText):
			charList.append(customText[i])
		else:
			charList.append(choice(charset))

		maxFontSize = int(sectorSize * 1.15)
		minFontSize = int(maxFontSize / 1.9)
		charList.append(randint(minFontSize , maxFontSize))

		if (i == (length - 1)):
			hPosition = randint((sectorSize * i) , int(sectorSize * (i + 0.8)))
		else:
			hPosition = randint((sectorSize * i) , (sectorSize * (i + 1)))
		vPosition = randint(0 , (height - charList[1]))
		charList.append(hPosition)
		charList.append(vPosition)

		charsAndAtts.append(charList)

	return charsAndAtts


def generate():
	captcha = Image.new('RGB' , (width , height) , (255 , 255 , 255))
	d = ImageDraw.Draw(captcha)

	for charAndAtts in getTextAndAtts():
		f = ImageFont.truetype(choice(fonts) , charAndAtts[1])
		d.text((charAndAtts[2] , charAndAtts[3]) , charAndAtts[0] , font = f , fill = (0 , 0 , 0))
