from PIL import Image , ImageFont , ImageDraw
from secrets import choice
from random import randint
from base64 import b64encode
from io import BytesIO



########################## User-Defined Settings ##########################

############### Text Attributes ###############
customText = ''
randomTextLength = 6

charset = 'abcdefghjkmnpqrstuvwxyzABCDEFGHJKMNPQRSTUVWXYZ23456789' # Commonly-confused characters discluded
fonts = ['fonts/Amatic-Bold.ttf' , 'fonts/TungusFont_Tinet.ttf' , 'fonts/LifeSavers-Bold.ttf'] # Only open source fonts used; note: these fonts are not necessarily under the perview of this code's MIT license, and may be licensed differently, such as under SIL International
############ End of Text Attributes ###########


############## Image Attributes ###############
width = 750
height = 250

imageFormat = 'PNG'

leftRightEdgesBufferPercentage = 25
bottomEdgeBufferPercentage = 5

enableWarp = False
warpLimitPercentage = 10
maxNoise = 10
########### End of Image Attributes ###########


########### Authentication Settings ###########
caseSensitivity = False # Due to font variations, case-sensitivity is not recommended; when set to False, the entire character set will continue to be used for image rendering, however the characters returned by generate and used for hashing will always be lowercase


# Encryption:
encryptText = False
encryptionKey = b''

# Hashing:
hashText = False # Can add a significant amount of inefficiency
nameIsTextHash = False # Requires passing only the desired save path (with a trailing forward slash and no subsequent filename) when calling generate
saltRounds = 18 # The higher the number the greater the security and (consequently) lower the efficiency
######## End of Authentication Settings #######

####################### End of User-Defined Settings ######################



# Generate randomized text (including text position, size, and color):
def getTextAndAtts():
	length = randomTextLength
	if (customText):
		length = len(customText)

	sectorSize = int(width / length)
	sectorBuffer = int(sectorSize * (leftRightEdgesBufferPercentage / 100))
	heightBuffer = int(height * (bottomEdgeBufferPercentage / 100))

	charsAndAtts = []
	for i in range(length):
		charList = []

		# select character:
		if (customText):
			charList.append(customText[i])
		else:
			charList.append(choice(charset))

		# select random font size:
		maxFontSize = int(sectorSize * 1.35)
		minFontSize = int(maxFontSize / 1.75)
		charList.append(randint(minFontSize , maxFontSize))

		# select a rough, random character position (and implement buffers where necessary):
		if (i == 0):
			hPosition = randint(sectorBuffer , (sectorSize * (i + 1)))
		elif (i == (length - 1)):
			hPosition = randint(((sectorSize * i) - sectorBuffer) , ((sectorSize * (i + 1)) - sectorBuffer))
		else:
			hPosition = randint((sectorSize * i) , (sectorSize * (i + 1)))

		vPosition = randint(0 , ((height - charList[1]) - heightBuffer))

		charList.append(hPosition)
		charList.append(vPosition)

		charsAndAtts.append(charList)

	return charsAndAtts


# Generate a CAPTCHA:
def generate(saveFullPath = ''):
	# Set global variables:
	global encryptionKey

	# Choose a random background color:
	r = randint(0 , 255)
	g = randint(0 , 255)
	b = randint(0 , 255)

	# Instantiate the image:
	captcha = Image.new('RGB' , (width , height) , (r , g , b))
	d = ImageDraw.Draw(captcha)

	# Generate random color shades that aren't too similar to the background color:
	multValue = choice([(randint(0 , 80) / 100) , (randint(120 , 200) / 100)])
	nr = (int(r * multValue) % 255)
	ng = (int(g * multValue) % 255)
	nb = (int(b * multValue) % 255)

	multValue = choice([(randint(0 , 80) / 100) , (randint(120 , 200) / 100)])
	snr = (int(r * multValue) % 255)
	sng = (int(g * multValue) % 255)
	snb = (int(b * multValue) % 255)

	# Add the text:
	captchaText = ''
	for charAndAtts in getTextAndAtts():
		f = ImageFont.truetype(choice(fonts) , charAndAtts[1])
		d.text((charAndAtts[2] , charAndAtts[3]) , charAndAtts[0] , font = f , fill = choice([(nr , ng , nb) , (snr , sng , snb)]))
		captchaText += charAndAtts[0]

	# Add noise:
	for i in range(randint(0 , maxNoise)):
		startX = randint(0 , width)
		startY = randint(0 , height)
		d.arc([(startX , startY) , (randint(startX , width) , randint(startY , height))] , randint(0 , 359) , randint(0 , 359) , width = randint(1 , 4) , fill = choice([(nr , ng , nb) , (snr , sng , snb)]))

	# Warp the image:
	if (enableWarp):
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

	# Remove case sensitivity, if necessary:
	if (not(caseSensitivity)):
		captchaText = captchaText.lower()

	# Encrypt the text, if necessary:
	encryptedText = b''
	if (encryptText):
		from cryptography.fernet import Fernet

		if (not(encryptionKey)):
			encryptionKey = Fernet.generate_key()

		f = Fernet(encryptionKey)

		encryptedText = f.encrypt(captchaText.encode())

	# Hash the text, if necessary:
	hashedText = b''
	if (hashText):
		from bcrypt import hashpw , gensalt

		hashedText = hashpw(captchaText.encode() , gensalt(saltRounds))

	# Save the CAPTCHA:
	base64EncodedFile = b''
	if (saveFullPath):
		if ((nameIsTextHash) and (hashText)):
			# Base64 encode the hash to make it filename friendly:
			hashedTextB64 = b64encode(hashedText).decode()
			captcha.save((saveFullPath + hashedTextB64) , imageFormat)
		else:
			captcha.save(saveFullPath , imageFormat)
	else:
		ioObj = BytesIO()
		captcha.save(ioObj , imageFormat)
		base64EncodedFile = b64encode(ioObj.getvalue())

	return captchaText , encryptedText , hashedText , base64EncodedFile


# Verify user response:
def verify(userInput , encryptedOrHashedText):
	if (encryptText):
		if (encryptionKey):
			from cryptography.fernet import Fernet

			f = Fernet(encryptionKey)

			if (caseSensitivity):
				if (userInput == f.decrypt(encryptedOrHashedText).decode()):
					return True
			else:
				if (userInput.lower() == f.decrypt(encryptedOrHashedText).decode().lower()):
					return True

			return False

	if (hashText):
		from bcrypt import checkpw

		if (caseSensitivity):
			return checkpw(userInput.encode() , encryptedOrHashedText)
		else:
			return checkpw(userInput.lower().encode() , encryptedOrHashedText)

	return False
