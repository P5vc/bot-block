# BotBlock

***A modern, self-hosted, privacy-respecting, CAPTCHA solution***

------------

# Table of Contents

- [Overview](#overview "Overview")
- [Implementation Details](#implementation-details "Implementation Details")
- [Usage](#usage "Usage")
  - [Installation](#installation "Installation")
  - [Generating a Simple CAPTCHA](#generating-a-simple-captcha "Generating a Simple CAPTCHA")
  - [Using the CAPTCHA Engine](#using-the-captcha-engine "Using the CAPTCHA Engine")
  - [Customizing CAPTCHA Settings](#customizing-captcha-settings "Customizing CAPTCHA Settings")
  - [Available Settings](#available-settings "Available Settings")
- [Example CAPTCHAs](#example-captchas "Example CAPTCHAs")

# Overview

BotBlock is a CAPTCHA solution designed to help developers protect their websites and applications from bots, without having to compromise on the privacy of their users.

Unlike most other CAPTCHA solutions, BotBlock is open source, completely self-hosted, and does not require JavaScript.

If you are looking for a simple—yet robust—CAPTCHA solution that is customizable, easy to implement, privacy-respecting, and fully self-contained, BotBlock is the way to go!

# Implementation Details

BotBlock is written in Python3 and designed to be fully compatible with modern web application frameworks, such as Django. It is perfect for small to large (and maybe even some corporate-sized) websites and projects looking to mitigate spam on their servers.

BotBlock can be used to protect sensitive, costly, or limited resources that have the potential to be abused, such as storage space, email traffic, third-party API queries, human processing time, etc. For example, using BotBlock to guard a website's forms from automated submissions could mean the difference between a server that crashes after its drive is filled up (resulting in data loss, downtime, and hundreds of hours manual database entry review), and a perfectly healthy server that is able to reject the automated submissions without breaking a sweat.

BotBlock strives to make it easy to generate all types CAPTCHAs. It supplies built-in defaults that work "out of the box," while also providing support for extensive customization, allowing developers to set custom fonts, character sets, image sizes and formats, minimum color contrast levels, and much more. BotBlock doesn't just focus on front-end content generation, however. Understanding that proper CAPTCHA validation is just as important as impressive CAPTCHA generation, BotBlock provides a backend CAPTCHA Engine designed to ensure the secure validation of CAPTCHAs. The Engine will automatically enforce CAPTCHA expirations and timeouts, utilize memory-efficient authentication schemes, prevent replay attacks, and much more. Ready for production environments, upon instantiation, the Engine will also launch dedicated subprocesses for generation and validation, and create a pool of CAPTCHAs to keep on standby. These features increase efficiency and allow for burstability, while ensuring that responses to CAPTCHA generation or validation queries are lightning fast.

When using BotBlock for your project, it's important to keep accessibility in mind. Although BotBlock does provide font/image size and color contrast settings to help developers comply with modern web accessibility standards, BotBlock is not perfect. For example, at the moment, BotBlock does not provide support for audio-based CAPTCHAs, and due to the unique purpose of a CAPTCHA, they cannot be solved by those who rely on a screen reader (because providing the solution as alternate text would defeat the purpose of the CAPTCHA). Therefore, it is recommended to implement BotBlock as non-intrusively as possible. For example, you may wish to program your web application to only present a CAPTCHA to users during periods of elevated usage or submissions. This may result in a small amount of spam being able to sneak through before BotBlock kicks in, but will provide a smoother and more-accessible experience for all of your users the majority of the time, while still keeping you protected from the damage that large amounts of spam can cause.

Please remember that BotBlock is a free, open source, community project. It makes no guarantees and provides no professional support. If you find it useful for mitigating spam and providing an additional layer of defense for your project, great! You are more than welcome to use it! But know that in these modern times with rapidly-improving AI and OCR technology, it is not completely implausible that BotBlock is, or eventually will be, defeatable. In addition, please keep in mind that BotBlock is self-hosted, and therefore will not be able to defend against traditional Denial of Service attacks. In fact, BotBlock could actually make those types of attacks more effective, due to the additional processing power required to generate CAPTCHAs. For the best results, it is recommended to only use BotBlock in line with the use cases outlined above.


# Usage

The full guide for developers on how to install, configure, and integrate BotBlock into their projects.

## Installation

The easiest way to install BotBlock is to use `pip`:

```bash
pip install botblock
```

On some systems, you may need to run one of the following variations, instead:

```bash
python -m pip install botblock
```

```bash
pip3 install botblock
```

```bash
python3 -m pip install botblock
```

Using `pip` to install BotBlock will automate compatibility checks and dependency downloads. However, if you elect to build BotBlock from source, or wish to clone our git repository and import BotBlock directly from there, here are the required dependencies and their corresponding versions:

```
python>=3.9

cryptography>=39.0
importlib-resources>=5.12
Pillow>=9.4
```

## Generating a Simple CAPTCHA

To generate a simple CAPTCHA using BotBlock, you must first import the `Captcha` class:

```python
from botblock.captcha import Captcha
```

Next, instantiate a `Captcha` object with the default settings:

```python
my_captcha = Captcha()
```

Instantiating a `Captcha` object will also automatically generate a CAPTCHA.

To save the CAPTCHA image for viewing, call the `save` method on your `Captcha` instance, and supply the full path of the image file you would like to create. For example:

```python
my_captcha.save('/tmp/image.png')
```

You can now open that image file with your favorite image viewer, to see the newly-generated CAPTCHA.

To increase efficiency and make embedding CAPTCHAs within webpages as easy as possible, you can also call the `base64` method on your `Captcha` instance to get its image data in base64 format, as a String:

```python
base64_captcha_image = my_captcha.base64()
```

If the (shortened, for this example) base64 data returned were `RXhhbXBsZSBDQVBUQ0hBIEltYWdlIERhdGE=`, you could embed it in a webpage using an `img` tag, like this:

```html
<img src="data:image/png;base64,RXhhbXBsZSBDQVBUQ0hBIEltYWdlIERhdGE=" alt="BotBlock CAPTCHA" />
```

Let's try it! Here's a short Python script you can run (interactively, if you'd like), that will generate a CAPTCHA and then embed it in `captcha.html`: a blank webpage the script will create in the same directory that you run the script from. After running the script, you can double-click the file to view the webpage in your browser.

Feel free to run this script a few times, reloading your web browser each time, to get a feel for the variety of CAPTCHAs BotBlock is capable of generating.

```python
from botblock.captcha import Captcha

my_captcha = Captcha()

with open('captcha.html', 'w') as webpage:
	webpage.write('<!DOCTYPE html>\n<html>\n  <head>')
	webpage.write('\n    <title>BotBlock CAPTCHA Example</title>')
	webpage.write('\n  </head>\n  <body>\n    <div>')
	webpage.write('\n      <p>Embedded BotBlock CAPTCHA:</p>')
	webpage.write('\n      <img src="data:image/png;base64,')
	webpage.write(my_captcha.base64())
	webpage.write('" alt="BotBlock CAPTCHA" />')
	webpage.write('\n    </div>\n  </body>\n</html>\n')
```

To get a CAPTCHA's solution, you can call the `get_solution` method on your `Captcha` instance, like so:

```python
solution = my_captcha.get_solution()
```

Keep in mind that although the returned solution will always match the capitalization of the text appearing in the CAPTCHA image, you may not wish to enforce case sensitivity (and the BotBlock Engine will not enforce it by default) when verifying users' solutions.

If you would like to see statistical information about a `Captcha` instance, you can call its `print_stats` method, or use `get_stats` to return the same information as a dictionary:

```python
stats = my_captcha.get_stats()
# To print the Captcha instance's stats, you can use either of the following:
my_captcha.print_stats()
print(my_captcha)
```

Finally, the `generate` method can be called on your `Captcha` instance to regenerate its CAPTCHA image and metadata:

```python
my_captcha.generate()
```

In most circumstances, developers should never need to call this method. For small projects, new CAPTCHAs should be created by simply instantiating a new `Captcha` object or using an `Engine` instance. When you regenerate CAPTCHA data, all of the old data is lost, making it more complicated to fetch solutions and validate CAPTCHAs in the future. The `generate` method is only provided for edge cases, because calling `generate` can be slightly more efficient than instantiating a completely new `Captcha` object. That being said, if your code is generating enough CAPTCHAs for this tiny efficiency advantage to make a difference, then you should be using the (more efficient and robust) `Engine` object to generate your CAPTCHAs, anyways.

### Using the CAPTCHA Engine

BotBlock's CAPTCHA Engine provides all of the backend code needed to generate and validate CAPTCHAs in a production environment. For the vast majority of users, an `Engine` object is a much better option than manually generating and validating CAPTCHAs via a `Captcha` object. `Captcha` objects should really only be used for quick testing and unconventional use cases.

Although the `Engine` object's lack of certain features provided by `Captcha` objects may feel cumbersome at first, this is an intentional decision designed to increase security and efficiency, and reduce critical implementation errors. For example, when using the CAPTCHA Engine, you will not be able to programmatically view the correct solutions to generated CAPTCHAs. This ensures that the Engine's validation function must always be called, where strong encryption, replay attack protection, and CAPTCHA expiration is always used.

When you instantiate an `Engine` object, three subprocesses are automatically created. The first subprocess instantiates a pool of `Captcha` instances, creating a buffer capable of withstanding bursts in CAPTCHA requests. In the event that CAPTCHA settings are changed, this subprocess is the one responsible for updating all of the `Captcha` instances with the new settings. The second subprocess handles the automatic regeneration of used `Captcha` instances, ensuring that the pool of fresh CAPTCHAs is always full. The third subprocess handles CAPTCHA validation, automatically checking CAPTCHAs submitted for validation to ensure that they haven't already been validated (preventing replay attacks). This subprocess also maintains the storage of validated CAPTCHAs, and automatically removes their data after they have expired.

To use BotBlock's CAPTCHA Engine, you must first import the `Engine` class, like so:

```python
from botblock.captcha import Engine
```

After importing the `Engine` class, you can instantiate an `Engine` object with the default settings:

```python
engine = Engine()
```

When using a CAPTCHA Engine, it's important to make sure that only one `Engine` object is instantiated per usage domain. Among other things, this helps to prevent inaccuracies that could arise from attempting to validate a CAPTCHA response with a different `Engine` instance than the one that generated the original CAPTCHA data. One `Engine` instance should be more than enough for most websites/projects. However, if you have isolated code that you think could benefit from having distinct CAPTCHA Engines (such as separate *apps* within a Django *project*), then instantiating more than one CAPTCHA Engine may be appropriate.

When you are finished using an `Engine` instance, that instance ***must*** be shut down. This will properly flush all of the buffers, clear all of the queues, allow the used memory to be freed, and terminate the various threads and processes started by the instance. To shut down an `Engine` instance, simply call its `shut_down` method:

```python
engine.shut_down()
```

The `shut_down` method will block until the `Engine` instance has finished shutting down. This shouldn't take more than a few seconds at most.

Alternatively, you can use a `with` statement with an `Engine` instance to automatically shut it down after the statement body finishes executing:

```python
with Engine() as engine:
    captcha = engine.get_captcha()
```

To check if an `Engine` instance has been shut down, you can call its `is_shut_down` method:

```python
if engine.is_shut_down():
	print('This Engine instance has been shut down.')
else:
	print('This Engine instance is still active.')
```

To get a fresh CAPTCHA from an `Engine` instance, you can call its `get_captcha` method. This method will return a dictionary containing the base64-encoded CAPTCHA image as a String, and a URL-safe encrypted blob with the CAPTCHA's solution and provision time (the latter unencrypted but integrity-checked) as a String. You may optionally provide the full path to an image file as an argument to this method, to save (by creating or overwriting) the CAPTCHA image to that file. Here are some examples of getting CAPTCHAs from an `Engine` instance:

```python
# Gets CAPTCHA data:
first_captcha = engine.get_captcha()
# Gets CAPTCHA data and saves CAPTCHA image to the specified file:
second_captcha = engine.get_captcha('/tmp/captcha2.png')
# Gets CAPTCHA data and then prints all of it:
third_captcha = engine.get_captcha()
print('Base64-Encoded CAPTCHA Image Data:')
print(third_captcha['base64_captcha'])
print('Encrypted Blob with CAPTCHA Authentication Data:')
print(third_captcha['encrypted_blob'])
```

For maximum efficiency, it is recommended to directly embed the CAPTCHA, as a base64-encoded image, into the webpage (or whatever other front-end you are using) that gets served to your users, rather than saving the CAPTCHA as an image file. See the [Generating a Simple CAPTCHA](#generating-a-simple-captcha "Generating a Simple CAPTCHA") section for examples of how to do this.

When serving the CAPTCHA to your users, you will want to serve them the encrypted blob as well. The encrypted blob contains the authentication data necessary to validate a user's response. Don't worry, this data is completely safe to share with a user alongside the CAPTCHA image. The advantage of doing so, is that it prevents the developer from having to keep track of individual sessions and their associated CAPTCHA data, and allows the `Engine` instance to immediately recycle the `Captcha` instance that was used to generate the CAPTCHA data (as the encrypted blob now contains all of the data that will be needed during the validation phase). This dramatically increases efficiency.

For those interested in the technical details, the blob is encrypted with AES in CBC mode, using a 128-bit key, PKCS7 for padding, and a SHA256 HMAC for authentication. It uses a strong, randomly-generated symmetric key, and is single-use only. The encryption is implemented using the battle-tested `cryptography.fernet` library in Python.

Although you aren't required to serve the encrypted blob to your users, and are welcome to write your own backend to associate encrypted blobs with users' CAPTCHA solutions, this is highly discouraged, and only opens the door to unnecessary mistakes, errors, and added overhead. The recommended method to serve this data to your users, if using BotBlock with a web application, is to include the encrypted blob as a hidden field within the same form that contains a user's proposed CAPTCHA solution. This ensures that you can efficiently distribute and receive the proposed CAPTCHA solution and associated authentication data, in unison. Most web application frameworks make frequent use of hidden form fields (such as for serving Cross Site Request Forgery Tokens), and include built-in methods that can easily be called from within a template to render a field as hidden.

Once you receive a proposed solution and the associated authentication data from a user (after they submit a BotBlock-protected form on your website, for example), you can move on to validating their solution:

```python
encrypted_blob = get_authentication_data() # Made up function used for the example
proposed_solution = get_proposed_solution() # Made up function used for the example
if engine.validate(encrypted_blob, proposed_solution):
	return "Successfully solved the CAPTCHA"
else:
	return "Failed to successfully solve the CAPTCHA"
```

An `Engine` instance's `validate` method will always return `False`, unless:

- The authentication data can be successfully decrypted
- The authentication data isn't older than the CAPTCHA's lifetime (the CAPTCHA isn't expired)
- The proposed solution matches the correct solution
- Validation hasn't already been attempted (successfully or unsuccessfully) with this encrypted blob

Finally, to get statistical information about an `Engine` instance, you can call its `get_stats` method, to have the data returned as a dictionary. Alternatively, you can call `print_stats`, to have the information printed to your terminal. It's important to note that for the few seconds (though usually less) that it takes an `Engine` instance to compile the statistics, you may notice degraded query response speeds. Here's example output from calling `print_stats` on a production `Engine` instance:

```
>>> engine.print_stats()
BOTBLOCK ENGINE INSTANCE

    Shut Down: No
    Active: 0 days, 16 hours, 21 minutes, and 30 seconds

    Pool Size: 500
    Fresh CAPTCHAs in Pool: 493
    Used CAPTCHAs in Pool: 7

    CAPTCHAs Distributed: 19630
    Validation Attempts: 12442
    CAPTCHA Solves: 10596

    CAPTCHAs Generated per Hour: 1200.0
    Validation Attempts per Hour: 760.59
    CAPTCHA Solves per Hour: 647.74

    Average Stats per Captcha Instance (500 Analyzed):
        Average number of CAPTCHAs generated per Captcha Instance: 39.26
        Average Font Size per Character per CAPTCHA: 122.35
        Average Number of Character Colors Evaluated per CAPTCHA: 28.31
        Average Number of Corrections to Character Positions per CAPTCHA: 1.54
        Average Image Data Size (In Bytes) per CAPTCHA: 30784.54
        Average Number of Layers of Noise Applied to Each CAPTCHA: 18.86

    Settings:
        WIDTH                                 = 750
        HEIGHT                                = 250
        FORMAT                                = 'PNG'
        TEXT                                  = ''
        TEXT_LENGTH                           = 6
        CHARACTER_SET                         = 'abcdefghjkmnpqrstuvwxyzABCDEFGHJKMNPQRSTUVWXYZ23456789'
        FONTS                                 = [
                                                    'Amatic-Bold.ttf',
                                                    'LifeSavers-Bold.ttf',
                                                    'TungusFont_Tinet.ttf',
                                                ]
        CHARACTER_HORIZONTAL_SHIFT_PERCENTAGE = 65
        CHARACTER_VERTICAL_SHIFT_PERCENTAGE   = 65
        FONT_SIZE_SHIFT_PERCENTAGE            = 25
        CHARACTER_OVERLAP_ENABLED             = False
        MAXIMUM_NOISE                         = 25
        MINIMUM_COLOR_BRIGHTNESS_DIFFERENCE   = 65
        MINIMUM_COLOR_HUE_DIFFERENCE          = 250
        CASE_SENSITIVE                        = False
        LIFETIME                              = 600
        POOL_SIZE                             = 500
        RATE_LIMIT                            = 0
```

## Customizing CAPTCHA Settings

Now that you can successfully generate and validate CAPTCHAs, it's time to learn how to customize them!

All of the settings used to generate CAPTCHAs and configure an Engine are stored within an instance of the `Settings` class. This class provides some important functionality, such as:

- Validating provided settings
- Using provided settings to pre-compute "behind-the-scenes" values needed during CAPTCHA generation
- Allowing existing settings to be easily viewed, exported, or updated
- Benchmarking different settings to provide an easy efficiency comparison

To use custom settings, the `Settings` class must first be imported, like so:

```python
from botblock.captcha import Settings
```

Now that the `Settings` class has been imported, you can instantiate a `Settings` object:

```python
default_settings = Settings()
```

Because we didn't provide any arguments to the `Settings` object during instantiation, this instance will have the default settings values.

To view the current values that a `Settings` instance holds, you can call its `print_settings` method, or just print the instance itself:

```python
default_settings.print_settings()
print(default_settings)
```

To retrieve the current settings as a dictionary, instead of printing them, you can use the `get_settings` method:

```python
settings_dict = default_settings.get_settings()
```

If you would like to compare a customized `Settings` instance's values to the default values, you can call the `print_default_settings` and `get_default_settings` methods, which function just like their respective `print_settings` and `get_settings` methods, as outlined above.

```python
if default_settings.get_settings() == default_settings.get_default_settings():
    print('The current settings instance contains the default settings.')
else:
    print('The current settings instance has been customized.')
```

To create a `Settings` instance with customized values, simply pass the settings you would like to customize and their new values as arguments upon instantiation. Any setting not specified with a custom value during instantiation will automatically use its default value.

```python
custom_settings = Settings(WIDTH = 825, HEIGHT = 275)
```

You can also update the value of one or more settings after a `Settings` object has been instantiated, by calling its `set` method. Any settings not specified with a new value will maintain the value they had before the `set` method was called.

```python
# You can call `get_supported_image_formats` for a list of the supported image formats:
new_image_format = custom_settings.get_supported_image_formats()[1]
custom_settings.set(TEXT_LENGTH = 8, CASE_SENSITIVE = True, FORMAT = new_image_format)
```

Every time you make an update to the settings, all values are automatically revalidated, and any pre-computed values are recomputed. That being said, if something goes wrong, you can always manually call the validation method (`validate_settings`) yourself, or reset your `Settings` instance back to the default values, with the `set_default_values` method:

```python
custom_settings.set_default_values()
custom_settings.validate_settings() # Redundant; will raise an exception if invalid settings found
```

Whenever a `Captcha` or `Engine` object is instantiated without any arguments, it will create its own `Settings` instance with the default values. To have a `Captcha` or `Engine` instance use custom settings, you must provide a custom `Settings` object as an argument upon instantiation, or as an argument to the `update_settings` method:

```python
from botblock.captcha import *

custom_settings = Settings(WIDTH = 675, HEIGHT = 225)
custom_engine = Engine(custom_settings)
custom_captcha = Captcha()

custom_engine.update_settings(Settings(FORMAT = 'GIF'))

# You can use the `get_settings` method to get the current `Settings` object:
captcha_settings = custom_captcha.get_settings()
captcha_settings.set(FORMAT = 'JPEG')
custom_captcha.update_settings(captcha_settings)

# Provide no `Settings` instance as an argument, to restore the default settings:
custom_engine.update_settings()
```

Modifying settings can have a big impact on efficiency. For example, decreasing the length of the CAPTCHA text can make CAPTCHA generation significantly faster. However, this also decreases security by exponentially raising the odds of randomly guessing the correct solution to a CAPTCHA (which is a big deal, when automated guessing is taken into account). Therefore, the `Settings` class comes with a built-in benchmarking method, to help you calculate the efficiency tradeoff for customized settings, and determine which settings are the best for your project.

To run an efficiency benchmark, simply instantiate a `Settings` object with your desired settings, then call its `compare_efficiency` method. You can pass another `Settings` instance to this method to compare against a second set of customized settings, or leave it empty to compare against the default settings. You may also modify the default benchmarking time of 5 minutes (300 seconds).

```python
first_settings = Settings(TEXT_LENGTH = 10)
second_settings = Settings(TEXT_LENGTH = 5)
first_settings.compare_efficiency(second_settings)

first_settings.compare_efficiency(settings = Settings(TEXT_LENGTH = 3), test_length = 120)
```

When running a benchmark, please keep in mind that:

- The specified test length is a rough target, and not an exact value. The final test length may end up being a bit above or below this value, depending on how long the scheduled benchmarks end up taking.
- The benchmark is not guaranteed to be 100% accurate. Due to a variety of factors (such as background tasks that the OS may randomly start/stop during the benchmark), you should expect each benchmark to return a slightly different result.
- To get the best results, it is recommended to run the benchmark a few times, and make sure not to use short test lengths. If, after doing so, you get consistent results (i.e. one `Settings` instance is always found to me more efficient than the other), then you can feel much more confident about the accuracy of those results.
- The raw numbers shown (such as the number of CAPTCHAs generated and the amount of time they were generated in) are not indicative of the performance you can expect when using an Engine, as the benchmark only utilizes `Captcha` objects for increased simplicity and accuracy (and for that reason, customized Engine-specific settings will not impact the benchmark). That being said, though the raw numbers may not apply, the relative efficiency percentages between `Settings` instances should still be accurate for `Engine` objects.
- If you have a low-to-medium traffic website, the efficiency of your settings may not matter all that much, as you won't need to generate tens of thousands of CAPTCHAs per minute anyways. Therefore, don't get too hung up on the efficiency of your CAPTCHA Engine, and instead focus more on choosing the best, and most-accessible settings for your site.

## Available Settings

This section serves as a reference for each available setting that a developer may customize.

### WIDTH

**Applies To:** CAPTCHAs

**Default Value:** `750`

**Must Be:**

- Of type `int`
- Greater in value than `9`
- Greater or equal in value to the `HEIGHT` setting's value

**Efficiency Impact:**

In general, the greater the value, the lesser the efficiency

**Description:**

Sets the width of the CAPTCHA image to generate, in pixels

### HEIGHT

**Applies To:** CAPTCHAs

**Default Value:** `250`

**Must Be:**

- Of type `int`
- Greater in value than `4`
- Lesser or equal in value to the `WIDTH` setting's value

**Efficiency Impact:**

In general, the greater the value, the lesser the efficiency

**Description:**

Sets the height of the CAPTCHA image to generate, in pixels

### FORMAT

**Applies To:** CAPTCHAs

**Default Value:** `'PNG'`

**Must Be:**

- Of type `str`
- Equal to one of the following values:
  - `'BMP'`
  - `'GIF'`
  - `'ICO'`
  - `'JPEG'`
  - `'PNG'`
  - `'TIFF'`
  - `'WEBP'`
  - `'PDF'`

**Efficiency Impact:**

Image formats in order of average generation speed (from quickest to slowest):

- JPEG
- PDF
- BMP
- TIFF
- PNG
- ICO
- WEBP
- GIF

Image formats in order of average file size (from smallest to largest):

- GIF
- ICO
- WEBP
- PNG
- JPEG
- PDF
- TIFF
- BMP

*Note: results may vary by system*

**Description:**

Sets the image format of the generated CAPTCHA image

The PNG and JPEG image formats are highly recommended due to their widespread support, quick generation speed, and relatively small file sizes.

The PNG format was chosen as the default, due to it being a lossless image format. This ensures that the CAPTCHA details, including all of the noise, are clearly visible in the image. That being said, if you're using a large-enough image size for the text to still be clear, and don't mind compression artifacts on the image, then switching this setting from `'PNG'` to `'JPEG'` could just about double the CAPTCHA generation efficiency, while maintaining about the same file sizes.

### TEXT

**Applies To:** CAPTCHAs

**Default Value:** `''`

**Must Be:**

- Of type `str`
- Empty, or greater in length than `2`

**Efficiency Impact:**

In general, the greater the length, the lesser the efficiency

**Description:**

Sets custom CAPTCHA text to use

When blank, CAPTCHA text will be randomly generated using characters from the `CHARACTER_SET` setting. Otherwise, CAPTCHA text (and therefore the solution) will always be equal to this value (negating the `CHARACTER_SET` and `TEXT_LENGTH` settings).

### TEXT_LENGTH

**Applies To:** CAPTCHAs

**Default Value:** `6`

**Must Be:**

- Of type `int`
- Greater in value than `2`

**Efficiency Impact:**

In general, the lesser the value, the greater the efficiency

**Description:**

Sets the length of randomly-generated CAPTCHA text/solutions

Be sure not to set the text length too low, as each fewer character is an exponential decrease in the number of possible CAPTCHA solutions. If the number of possible solutions gets too low, say `10,000`, then a malicious user could write code to automatically submit a form `10,000,000` times, with a random guess of the solution each time, and expect about `1,000` of those submissions to be excepted as valid.

Using the default character set with case sensitivity disabled (also the default), this is how many possible solutions there are for the first ten `TEXT_LENGTH` values:

| TEXT_LENGTH |      Solutions      |
|-------------|---------------------|
|      1      |                  31 |
|      2      |                 961 |
|      3      |              29,791 |
|      4      |             923,521 |
|      5      |          28,629,151 |
|      6      |         887,503,681 |
|      7      |      27,512,614,111 |
|      8      |     852,891,037,441 |
|      9      |  26,439,622,160,671 |
|     10      | 819,628,286,980,801 |

The font size used when generating a CAPTCHA is automatically calculated based on the text length and the image size. The greater the text length set here, the smaller the font size will be.

### CHARACTER_SET

**Applies To:** CAPTCHAs

**Default Value:** `'abcdefghjkmnpqrstuvwxyzABCDEFGHJKMNPQRSTUVWXYZ23456789'`

**Must Be:**

- Of type `str`
- Greater in length than `0` when the `TEXT` setting is blank
- Comprised of unique characters

**Efficiency Impact:**

Longer character sets are slightly more efficient than shorter ones

**Description:**

Sets the character set from which random characters are chosen for the CAPTCHA text, when no custom text is provided via the `TEXT` setting

When designing a custom character set, you should keep the following in mind:

- The character set should be relatively large (even with case sensitivity disabled), in order to increase bruteforce resistance
- The character set should still include mixed-case characters (if applicable) when case sensitivity is disabled, to increase the variability of CAPTCHA images
- The character set should only include characters that are easily-recognizable for your users
- The character set should not contain any characters that aren't commonly found on the keyboards of your users, or that they don't commonly type
- The character set should not contain any characters that look identical or very similar when rendered in any of the CAPTCHA's fonts (for example, `I`, `l`, and `1`)
- The character set should not contain any characters that Python doesn't know how to properly iterate over

### FONTS

**Applies To:** CAPTCHAs

**Default Value:** `['Amatic-Bold.ttf', 'LifeSavers-Bold.ttf', 'TungusFont_Tinet.ttf']`

**Must Be:**

- Of type `list` and containing one or more `str` types, which represent paths to valid font files

**Efficiency Impact:**

Variable, based on the typeface(s) provided

**Description:**

Sets the fonts that are chosen at random to render each character in the CAPTCHA image

If changing this setting, make sure to test each font with your character set, to ensure that the font can render all of the characters, and that no two characters look the same when rendered with any combination of the fonts. You may also wish to keep in mind that the more unique the font, the greater the chance that OCR/AI technologies will be unable to read it.

*Note: the default fonts, while all open source, do not fall under this repository's MIT license. Navigate to the `fonts` directory in this repository to view each font's license.*

### CHARACTER_HORIZONTAL_SHIFT_PERCENTAGE

**Applies To:** CAPTCHAs

**Default Value:** `65`

**Must Be:**

- Of type `int`
- A whole number less than `101` in value

**Efficiency Impact:**

Negligible

**Description:**

Sets the maximum percentage to horizontally shift characters

During CAPTCHA generation, characters' locations are shifted horizontally by a random percentage of their containing box's width. The maximum percentage that a character may be shifted left or right is determined by this setting.

### CHARACTER_VERTICAL_SHIFT_PERCENTAGE

**Applies To:** CAPTCHAs

**Default Value:** `65`

**Must Be:**

- Of type `int`
- A whole number less than `101` in value

**Efficiency Impact:**

Negligible

**Description:**

Sets the maximum percentage to vertically shift characters

During CAPTCHA generation, characters' locations are shifted vertically by a random percentage of the containing box's height. The maximum percentage that a character may be shifted up or down is determined by this setting.

### FONT_SIZE_SHIFT_PERCENTAGE

**Applies To:** CAPTCHAs

**Default Value:** `25`

**Must Be:**

- Of type `int`
- A whole number less than `101` in value

**Efficiency Impact:**

Negligible

**Description:**

Sets the maximum percentage to shift characters' font sizes

During CAPTCHA generation, characters' font sizes are shifted by a random percentage of their (automatically calculated) default size. The maximum percentage that a character's font size may be increased or decreased is determined by this setting.

### CHARACTER_OVERLAP_ENABLED

**Applies To:** CAPTCHAs

**Default Value:** `False`

**Must Be:**

- Of type `bool`

**Efficiency Impact:**

In general, when set to `True`, CAPTCHA generation is more efficient

**Description:**

When `False`, the randomly-shifted character positions in the CAPTCHA are checked and modified as necessary, to ensure that two characters never overlap, characters don't get positioned outside of the image border, and characters are always presented in the correct order. When `True`, this check is skipped, and character positions are only roughly enforced. This can lead to some CAPTCHAs containing overlapping characters, characters that are cut off (partially or completely) by the edge of the image, and/or characters that are slightly out of order. This is only a significant risk when one or both of the `CHARACTER_HORIZONTAL_SHIFT_PERCENTAGE` and `CHARACTER_VERTICAL_SHIFT_PERCENTAGE` settings' values are high.

### MAXIMUM_NOISE

**Applies To:** CAPTCHAs

**Default Value:** `25`

**Must Be:**

- Of type `int`
- A whole number

**Efficiency Impact:**

In general, the greater the value, the lesser the efficiency

**Description:**

Sets the maximum number of layers of noise to apply to a CAPTCHA

When CAPTCHAs are generated, a random number of layers of noise (from zero to this setting's value, inclusive) is applied to the image, to help obscure the text. Each layer of noise is randomly chosen to be an arc, line, or points drawn over the image at random locations or in random quantities.

### MINIMUM_COLOR_BRIGHTNESS_DIFFERENCE

**Applies To:** CAPTCHAs

**Default Value:** `65`

**Must Be:**

- Of type `int`
- Less than `201` in value

**Efficiency Impact:**

In general, the greater the value, the lesser the efficiency

**Description:**

Sets the minimum color brightness difference between the CAPTCHA background color and the CAPTCHA text color

When CAPTCHAs are generated, their background color and the color of each character is chosen at random. After a character's color is selected, however, the brightness difference between it and the background color is evaluated. If the brightness difference is less than the minimum value set by this setting, a new character color is chosen. This process repeats until a compliant character color is found. If, after 10,000 tries, a compliant character color cannot be found, a new, random background color for the CAPTCHA is chosen, and the process starts all over again.

The default value of this setting (combined with the default value of the `MINIMUM_COLOR_HUE_DIFFERENCE` setting) should be large enough to ensure that character colors with a high-enough contrast to the background color, for most people, are selected, but low enough to keep the impact on efficiency negligible.

While this setting's default value may be good for testing, **it should be changed when using BotBlock in production**. W3 recommends setting this value to at least `125`, to ensure compliance with web accessibility standards.

### MINIMUM_COLOR_HUE_DIFFERENCE

**Applies To:** CAPTCHAs

**Default Value:** `250`

**Must Be:**

- Of type `int`
- Less than `601` in value

**Efficiency Impact:**

In general, the greater the value, the lesser the efficiency

**Description:**

Sets the minimum color hue difference between the CAPTCHA background color and the CAPTCHA text color

When CAPTCHAs are generated, their background color and the color of each character is chosen at random. After a character's color is selected, however, the hue difference between it and the background color is evaluated. If the hue difference is less than the minimum value set by this setting, a new character color is chosen. This process repeats until a compliant character color is found. If, after 10,000 tries, a compliant character color cannot be found, a new, random background color for the CAPTCHA is chosen, and the process starts all over again.

The default value of this setting (combined with the default value of the `MINIMUM_COLOR_BRIGHTNESS_DIFFERENCE` setting) should be large enough to ensure that character colors with a high-enough contrast to the background color, for most people, are selected, but low enough to keep the impact on efficiency negligible.

While this setting's default value may be good for testing, **it should be changed when using BotBlock in production**. W3 recommends setting this value to at least `500`, to ensure compliance with web accessibility standards.

### CASE_SENSITIVE

**Applies To:** Engines

**Default Value:** `False`

**Must Be:**

- Of type `bool`

**Efficiency Impact:**

Negligible

**Description:**

When `True`, provided solutions must match the case (uppercase or lowercase) of the CAPTCHA text in order for the Engine's `validate` method to conclude that the solution is valid. For example:

| CAPTCHA Text | User's Solution | Considered Valid |
|--------------|-----------------|------------------|
|    NfBnhB    |      NfBnhB     |       True       |
|    CSKteH    |      cskteh     |       False      |
|    FSv52h    |      FSV52H     |       False      |
|    Tav3dH    |      TaV3dH     |       False      |

When `False`, the Engine's `validate` method will determine that a solution is valid as long as the correct characters are provided in the correct order, regardless of their capitalization. For example:

| CAPTCHA Text | User's Solution | Considered Valid |
|--------------|-----------------|------------------|
|    NfBnhB    |      NfBnhB     |       True       |
|    CSKteH    |      cskteh     |       True       |
|    FSv52h    |      FSV52H     |       True       |
|    Tav3dH    |      TaV3dH     |       True       |

It is highly recommended to use the default value of `False` for this setting, even if it makes the CAPTCHA easier to bruteforce. Enabling case sensitivity can be very frustrating for users who may not be expecting case sensitivity, or who may have trouble distinguishing the random case of each character (especially when a variety of fonts and/or shifts are used).

It should also be noted that when this setting is set to `False`, Python's `str.lower` method is applied to the CAPTCHA text and the proposed solution during validation, which may not work properly on all possible character sets. In those situations, you may need to change this setting to `True`.

###06597ba1cfc49461462bfd3896895253a067ddf2 LIFETIME

**Applies To:** Engines

**Default Value:** `600`

**Must Be:**

- Of type `int`
- A whole number

**Efficiency Impact:**

Negligible in most use cases

**Description:**

Sets the lifetime (in seconds) of CAPTCHAs, after which they expire

Any CAPTCHAs passed to an Engine for validation after the number of seconds indicated by this setting have passed since the CAPTCHA was created, will be declared as invalid. The default value for this setting is `600` seconds, or ten minutes, but any time between `30` seconds and `1800` seconds (30 minutes) is reasonable. If your website/project has a high level of traffic, you may wish to consider keeping the setting's value on the smaller side, to increase memory and validation efficiency.

### POOL_SIZE

**Applies To:** Engines

**Default Value:** `500`

**Must Be:**

- Of type `int`
- A natural number

**Efficiency Impact:**

Variable, depending on query rate and variance, host system specifications, and more

**Description:**

Sets an Engine's fresh `Captcha` instance pool size

In order to increase efficiency and query response speeds, and allow for burstable performance, Engine objects create and maintain a pool of fresh `Captcha` instances, with CAPTCHA images and data ready to be distributed at any moment. This size of this pool can be tuned to fit your website/project's requirements. For example, if your website often experiences large bursts in traffic, you may wish to increase the `POOL_SIZE` setting's value. On the other hand, if running on a system with very limited memory, you may wish to decrease this setting's value.

Note: this is the only setting that cannot be dynamically updated.

### RATE_LIMIT

**Applies To:** Engines

**Default Value:** `0`

**Must Be:**

- Of type `int`
- A whole number

*OR*

- Of type `float`
- Greater in value than `0.0`

**Efficiency Impact:**

No impact on CAPTCHA generation efficiency when disabled (default), very slight impact when enabled

The lesser the integer value (still greater than `0`), the lower the average CPU usage by BotBlock

The greater the floating point value, the lower the average CPU usage by BotBlock

**Description:**

Limits the number of CAPTCHAs that may be generated per minute

For systems with strict limits on average CPU usage, this setting allows the developer to limit the number of CAPTCHAs that BotBlock will generate per minute, via one of two ways:

When an integer value is supplied (e.g. `250`), BotBlock will only allow that number of CAPTCHAs to be generate per minute. If the limit is reached within one minute, BotBlock will pause CAPTCHA generation until the next minute starts.

When a floating point value is supplied (e.g. `0.1`), BotBlock will sleep for that number of seconds after each CAPTCHA that it generates, before beginning to generate the next CAPTCHA.

All rate limiting can be disabled by making this setting's value equal to `0`.

Note: the rate limiting does not apply to the initial CAPTCHA generation (to fill the pool) that occurs when an `Engine` is first instantiated. It will also not apply to the regeneration that occurs when an `Engine` instance's settings are updated.

# Example CAPTCHAs

Here are some example CAPTCHAs with different settings enabled, so you can get a feel for what some of the main settings do. Many of these are using exaggerated settings that wouldn't actually be used in a production environment.

### CAPTCHAs generated using the default settings:

![First Example of a Default CAPTCHA](https://source.priveasy.org/Priveasy/bot-block/raw/branch/main/examples/default-captcha-1.png)
![Second Example of a Default CAPTCHA](https://source.priveasy.org/Priveasy/bot-block/raw/branch/main/examples/default-captcha-2.png)
![Third Example of a Default CAPTCHA](https://source.priveasy.org/Priveasy/bot-block/raw/branch/main/examples/default-captcha-3.png)

### CAPTCHAs generated with default settings and saved as JPEGs:

![First Example of a Default CAPTCHA Saved as a JPEG](https://source.priveasy.org/Priveasy/bot-block/raw/branch/main/examples/default-captcha-1.jpeg)
![Second Example of a Default CAPTCHA Saved as a JPEG](https://source.priveasy.org/Priveasy/bot-block/raw/branch/main/examples/default-captcha-2.jpeg)
![Third Example of a Default CAPTCHA Saved as a JPEG](https://source.priveasy.org/Priveasy/bot-block/raw/branch/main/examples/default-captcha-3.jpeg)

### CAPTCHAs generated with higher contrast and low noise:

![First Example of a CAPTCHA with Higher Contrast and Low Noise](https://source.priveasy.org/Priveasy/bot-block/raw/branch/main/examples/high-contrast-low-noise-captcha-1.png)
![Second Example of a CAPTCHA with Higher Contrast and Low Noise](https://source.priveasy.org/Priveasy/bot-block/raw/branch/main/examples/high-contrast-low-noise-captcha-2.png)
![Third Example of a CAPTCHA with Higher Contrast and Low Noise](https://source.priveasy.org/Priveasy/bot-block/raw/branch/main/examples/high-contrast-low-noise-captcha-3.png)

### CAPTCHAs generated with high noise and character overlap enabled:

![First Example of a CAPTCHA with High Noise and Character Overlap](https://source.priveasy.org/Priveasy/bot-block/raw/branch/main/examples/high-noise-character-overlap-captcha-1.png)
![Second Example of a CAPTCHA with High Noise and Character Overlap](https://source.priveasy.org/Priveasy/bot-block/raw/branch/main/examples/high-noise-character-overlap-captcha-2.png)
![Third Example of a CAPTCHA with High Noise and Character Overlap](https://source.priveasy.org/Priveasy/bot-block/raw/branch/main/examples/high-noise-character-overlap-captcha-3.png)

### CAPTCHAs of various sizes and text lengths:

![First Example of a CAPTCHA with a Random Size and Text Length](https://source.priveasy.org/Priveasy/bot-block/raw/branch/main/examples/random-size-and-text-length-captcha-1.png)
![Second Example of a CAPTCHA with a Random Size and Text Length](https://source.priveasy.org/Priveasy/bot-block/raw/branch/main/examples/random-size-and-text-length-captcha-2.png)
![Third Example of a CAPTCHA with a Random Size and Text Length](https://source.priveasy.org/Priveasy/bot-block/raw/branch/main/examples/random-size-and-text-length-captcha-3.png)
