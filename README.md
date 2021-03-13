# BotBlock

###### A modern, self-hosted, privacy-respecting, completely automated, public Turing test, to tell computers and humans apart

------------

## Table of Contents

- [About](#about "About")
- [Usage](#usage "Usage")
- [Examples](#examples "Examples")

## About

BotBlock's goal is to provide a modern, privacy-respecting, CAPTCHA solution, to mitigate the harm that can be caused by bots. Unlike traditional CAPTCHA's, BotBlock is meant to be self-hosted, and does not rely on any type of traffic analysis: it provides a simple challenge and response.

BotBlock is for websites that do not wish to send user data to third parties, and are looking for an easy-to-implement solution. BotBlock is written in Python, and designed with Django compatibility in mind.

BotBlock's efficiency will vary greatly, depending on server hardware and user specifications. However, one can expect the BotBlock's default configuration to be capable of generating around 200 CAPTCHA's per second, when running on a single core ~3.0GHz CPU.

## Usage

Using BotBlock is as simple as cloning the repository (`git clone https://github.com/P5vc/BotBlock.git`) or copying the main, `BotBlock.py` and font files, and then importing BotBlock into your Python scripts. From there, you may edit/modify any of the following default settings, to fit your needs:

```python3
customText = ''
randomTextLength = 6
charset = 'abcdefghjkmnpqrstuvwxyzABCDEFGHJKMNPQRSTUVWXYZ23456789'
fonts = ['fonts/Amatic-Bold.ttf' , 'fonts/TungusFont_Tinet.ttf' , 'fonts/LifeSavers-Bold.ttf']
width = 750
height = 250
imageFormat = 'PNG'
leftRightEdgesBufferPercentage = 25
bottomEdgeBufferPercentage = 5
enableWarp = False
warpLimitPercentage = 10
maxNoise = 10
caseSensitivity = False
encryptText = False
encryptionKey = b''
replayAttackProtection = True
captchaTimeout = 1800
validUUIDs = []
hashText = False
nameIsTextHash = False
saltRounds = 18
```

> Note: You will need to install `Pillow` in order for BotBlock to work. If you wish to use the encryption feature, then `cryptography` will be required. Likewise, `bcrypt` must be installed if you wish to use the hashing functionality. These dependencies can be installed via the following command: `pip3 install Pillow cryptography bcrypt`.

## Examples

Generate a simple CAPTCHA using the default settings, then save it to the `tmp` directory:

```python3
import BotBlock
captchaData = BotBlock.generate('/tmp/image.png')
```

Generate a simple CAPTCHA using the default settings, and save just the image's base64-encoded bytes:

```python3
import BotBlock
imageB64 = BotBlock.generate()['b64Image']
```

Generate a simple CAPTCHA, save it to the `tmp` directory as a `jpeg` file, and store the CAPTCHA text to a variable:

```python3
import BotBlock
BotBlock.imageFormat = 'JPEG'
text = BotBlock.generate('/tmp/image.jpeg')['plainText']
```

Generate a CAPTCHA with custom text and image warping enabled, then save it to the `tmp` directory:

```python3
import BotBlock
BotBlock.customText = 'Hello'
BotBlock.enableWarp = True
BotBlock.generate('/tmp/image.png')
```

Generate a simple CAPTCHA with encryption enabled, save the returned dictionary to a variable, print the plaintext, encrypted text, and the base64-encoded image data, then submit an example user response to verify whether or not their answer was correct:

```python3
import BotBlock
BotBlock.encryptText = True
captchaData = BotBlock.generate()
print(captchaData['plainText'] , captchaData['encryptedText'] , captchaData['b64Image'])

randomUserResponse = 'abc123'
responseCorrect = BotBlock.verify(randomUserResponse , captchaData['encryptedText'])
if (responseCorrect):
	print('The response was correct.')
else:
	print('The response was incorrect.')
```

Generate a simple CAPTCHA, then hash the randomized text and save the image to the `tmp` directory with the filename as the hash (we'll have no need to save the values returned by `BotBlock.generate()`):

```python3
import BotBlock
BotBlock.hashText = True
BotBlock.nameIsTextHash = True
BotBlock.generate('/tmp/')
```

### Example Images

![Sample Captcha #1](/examples/sample1.png "First Sample Captcha Image")
![Sample Captcha #2](/examples/sample2.png "Second Sample Captcha Image")
![Sample Captcha #3](/examples/sample3.png "Third Sample Captcha Image")
