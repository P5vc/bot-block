from PIL import Image , ImageFont , ImageDraw
from secrets import choice
from bcrypt import hashpw , gensalt
from random import randint
from base64 import b64encode

customText = ''

textLength = 7

width = 600
height = 250

charset = 'abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ23456789'

fonts = ['fonts/Ballbase.ttf' , 'fonts/GiantRobotArmy-Medium.ttf' , 'fonts/Manustype.ttf' , 'fonts/NANOTYPE.ttf' , 'fonts/PixelGrunge.ttf' ,  'fonts/Savior1.ttf' , 'fonts/Thruster-Regular.ttf' , 'fonts/To The Point.ttf']

borderBufferPercentage = 12
warpLimitPercentage = 10
maxNoise = 10

saltRounds = 17
saveAsHashText = False # Requires passing only the desired save path (with a trailing forward slash and no subsequent filename) when calling generate

def getTextAndAtts():
	length = textLength
	if (customText):
		length = len(customText)

	sectorSize = int(width / length)

	# As width is generally greater than height, exaggerate the sectorBuffer (by 2x) and minimize the heightBuffer (by 1/2):
	sectorBuffer = int(int(sectorSize * (borderBufferPercentage / 100)) * 2)
	heightBuffer = int(int(height * (borderBufferPercentage / 100)) * 0.5)

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

		if ((i == (length - 1)) or (i == 0)):
			hPosition = randint(((sectorSize * i) + sectorBuffer) , ((sectorSize * (i + 1)) - (sectorBuffer * 2)))
		else:
			hPosition = randint((sectorSize * i) , (sectorSize * (i + 1)))

		vPosition = randint((0 + heightBuffer) , ((height - charList[1]) - heightBuffer))
		charList.append(hPosition)
		charList.append(vPosition)

		charsAndAtts.append(charList)

	return charsAndAtts


def generate(saveFullPath , hashText = False):
	# Choose background color:
	r = randint(0 , 255)
	g = randint(0 , 255)
	b = randint(0 , 255)

	# Create the image:
	captcha = Image.new('RGB' , (width , height) , (r , g , b))
	d = ImageDraw.Draw(captcha)

	# Add color shades before adding text/noise:
	multValue = choice([(randint(0 , 80) / 100) , (randint(120 , 200) / 100)])
	nr = (int(r * multValue) % 255)
	ng = (int(g * multValue) % 255)
	nb = (int(b * multValue) % 255)

	multValue = choice([(randint(0 , 80) / 100) , (randint(120 , 200) / 100)])
	snr = (int(r * multValue) % 255)
	sng = (int(g * multValue) % 255)
	snb = (int(b * multValue) % 255)

	# Add the captcha text:
	captchaText = ''
	for charAndAtts in getTextAndAtts():
		f = ImageFont.truetype(choice(fonts) , charAndAtts[1])
		d.text((charAndAtts[2] , charAndAtts[3]) , charAndAtts[0] , font = f , fill = choice([(nr , ng , nb) , (snr , sng , snb)]))
		captchaText += charAndAtts[0]

	# Add noise:
	for i in range(randint(0 , maxNoise)):
		startX = randint(0 , width)
		startY = randint(0 , height)
		d.arc([(startX , startY) , (randint(startX , width) , randint(startY , height))] , randint(0 , 359) , randint(0 , 359) , width = randint(1 , 3) , fill = choice([(nr , ng , nb) , (snr , sng , snb)]))

	# Warp the image:
	widthLimit = int(width * (warpLimitPercentage / 100))
	heightLimit = int(height * (warpLimitPercentage / 100))

	nwX = randint((0 - widthLimit) , widthLimit)
	nwY = randint((0 - heightLimit) , heightLimit)

	swX = randint((0 - widthLimit) , widthLimit)
	swY = randint((height - heightLimit) , (height + heightLimit))

	seX = randint((width - widthLimit) , (width + widthLimit))
	seY = randint((height - heightLimit) , (height + heightLimit))

	neX = randint((width - widthLimit) , (width + widthLimit))
	neY = randint((0 - heightLimit) , (0 + heightLimit))


	captcha = captcha.transform((width , height) , Image.QUAD , data = (nwX , nwY , swX , swY , seX , seY , neX , neY) , fillcolor = (r , g , b))


	hashedText = b''
	if (hashText):
		hashedText = hashpw(captchaText.encode() , gensalt(saltRounds))
		hashedTextB64 = b64encode(hashedText).decode()
		if (saveAsHashText):
			captcha.save((saveFullPath + hashedTextB64) , 'PNG')
			return captchaText , hashedTextB64

	captcha.save(saveFullPath)
	return captchaText , hashedText
