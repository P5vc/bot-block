# BotBlock

###### A modern, self-hosted, privacy-respecting, completely automated, public Turing test, to tell computers and humans apart

------------

## Table of Contents

- [About](#about "About")
- [Usage](#usage "Usage")
- [Examples](#examples "Examples")

## About

BotBlock's goal is to provide a modern, privacy-respecting, CAPTCHA solution, to mitigate the harm that can be caused by bots. Unlike traditional CAPTCHA's, BotBlock is meant to be self-hosted, and does not reply on any type of traffic analysis: it provides a simple challenge and response.

BotBlock is for websites that do not wish to send user data to third parties, and are looking for an easy-to-implement solution. BotBlock is written in Python, and designed for use with Django.

BotBlock's efficiency will vary greatly, depending on server hardware and user specifications. However, one can expect BotBlock to be capable of generating around 200 CAPTCHA's per second, when running on a single core ~3.0GHz CPU.

## Usage

Using BotBlock is as simple as cloning the repository (`git clone https://github.com/P5vc/BotBlock.git`) and then importing BotBlock into your Python scripts. From there, you may edit/modify any of the following default settings, to fit your needs:

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
warpLimitPercentage = 10
maxNoise = 10
caseSensitivity = False
hashText = False
nameIsTextHash = False
saltRounds = 18
```

## Examples

Generate a simple CAPTCHA using the default settings, then save it:

```python3
import BotBlock
text , hash , imageB64 = BotBlock.generate('/tmp/image.png')
```

Generate a simple CAPTCHA using the default settings, and save the image to a variable as base64-encoded bytes:

```python3
import BotBlock
text , hash , imageB64 = BotBlock.generate()
```

Generate a simple CAPTCHA, then save it to your `tmp` directory as a `jpeg` file:

```python3
import BotBlock
BotBlock.imageFormat = 'JPEG'
text , hash , imageB64 = BotBlock.generate('/tmp/image.jpeg')
```

Generate a simple CAPTCHA, then hash the randomized text and save the image to the `tmp` directory with the filename as the hash (we'll have no need to save the values returned by `BotBlock.generate()`):

```python3
import BotBlock
BotBlock.hashText = True
BotBlock.nameIsTextHash = True
BotBlock.generate('/tmp/')
```
