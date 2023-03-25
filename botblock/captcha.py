"""Contains the classes required to configure and initialize the BotBlock backend"""

from base64 import b64decode, b64encode
from io import BytesIO
# Switch these once minimum supported Python version is Python 3.10:
#from importlib.resources import files
from importlib_resources import files
from multiprocessing import Process, Queue
from pathlib import Path
from queue import Empty, Full
from random import randrange
from secrets import choice as secure_choice
from secrets import randbelow as secure_randbelow
from threading import Lock, Thread
from time import perf_counter_ns, sleep, time

from cryptography.fernet import Fernet, InvalidToken
from PIL import Image, ImageDraw, ImageFont


class Captcha():
    """Represents a single CAPTCHA with all of its (meta)data"""

    def __init__(self, settings = None):
        """Generates a CAPTCHA with all of the corresponding metadata"""

        self._character_colors_evaluated = 0
        self._character_position_corrections = 0
        self._font_size_total = 0
        self._generation = 0
        self._image_data_size = 0
        self._layers_of_noise = 0
        self.update_settings(settings)

    def _add_noise(self):
        """Adds random noise to the CAPTCHA"""

        for _ in range(self._settings._MAXIMUM_NOISE):
            noise_type = secure_choice(
                [
                    'arc',
                    'line',
                    'points',
                    None,
                ]
            )
            if noise_type == 'arc':
                self._layers_of_noise += 1
                self._draw_arc()
            elif noise_type == 'line':
                self._layers_of_noise += 1
                self._draw_line()
            elif noise_type == 'points':
                self._layers_of_noise += 1
                self._draw_points()
            else:
                continue

    def _clean_up(self):
        """Cleans up generation data, to increase memory and processing efficiency"""

        # Store the encoded image in memory, allowing the Image object to be freed:
        self._base64 = b''
        self.base64()

        # Must remove to allow for pickling (and therefore storage in queues):
        del self._draw
        # Delete other attributes that are no longer needed:
        del self._base_color
        del self._image
        del self._size

    def _create_image(self):
        """Generates the background image for the CAPTCHA"""

        self._size = (self._settings._WIDTH, self._settings._HEIGHT)
        self._base_color = self._get_color_values()
        self._image = Image.new(
            mode = 'RGB',
            size = self._size,
            color = self._base_color,
        )

    def _draw_arc(self):
        """Draws a random arc across the CAPTCHA"""

        start_x = randrange(self._size[0] + 1)
        start_y = randrange(self._size[1] + 1)
        self._draw.arc(
            [
                ( # Bounding box upper left coordinates
                    start_x,
                    start_y,
                ),
                ( # Bounding box lower right coordinates
                    randrange(
                        start_x,
                        self._size[0] + 1,
                    ),
                    randrange(
                        start_y,
                        self._size[1] + 1,
                    ),
                ),
            ],
            start = randrange(360), # Starting angle
            end = randrange(360), # Ending angle
            fill = self._get_color_values(),
            width = randrange(1, 5),
        )

    def _draw_line(self):
        """Draws a random line across the CAPTCHA"""

        self._draw.line(
            [
                ( # Line starting point
                    randrange(self._size[0] + 1),
                    randrange(self._size[1] + 1),
                ),
                ( # Line ending point
                    randrange(self._size[0] + 1),
                    randrange(self._size[1] + 1),
                ),
            ],
            fill = self._get_color_values(),
            width = randrange(1, 5),
        )

    def _draw_points(self):
        """Draws a random point on the CAPTCHA"""

        color = self._get_color_values()
        point_coordinates = []
        for _ in range(randrange(300)):
            point_coordinates.append(
                (
                    randrange(self._size[0] + 1),
                    randrange(self._size[1] + 1),
                )
            )
        self._draw.point(point_coordinates, fill = color)

    def _draw_text(self):
        """Draws the CAPTCHA's text on the base image"""

        self._draw = ImageDraw.Draw(self._image)
        self._text, text_and_attributes = self._get_text_and_attributes()
        for character_and_attributes in text_and_attributes:
            self._draw.text(
                (
                    character_and_attributes[2], # Horizontal Position
                    character_and_attributes[3], # Vertical Position
                ),
                character_and_attributes[0], # Character
                fill = character_and_attributes[4],
                font = character_and_attributes[1],
                anchor = 'mm',
                direction = 'ttb',
            )

    def _get_character_position(self, anchor, total_anchors, size, shift_percentage, previous_char_location):
        """Calculates the (shifted) position where a character should be drawn"""

        anchor_spacing = size / total_anchors
        center_location = anchor_spacing * anchor
        if shift_percentage:
            offset = secure_randbelow(shift_percentage * 2) - shift_percentage
            shifted_location = round(center_location + (anchor_spacing * (offset / 100)))
        else:
            shifted_location = center_location
        if shifted_location <= previous_char_location:
            shifted_location += (previous_char_location + 1 - shifted_location)
        return shifted_location

    def _get_color_values(self, background_color = None):
        """Returns random RGB color values for use in the CAPTCHA

        NOTE: This function can be extremely inefficient when using strict (high)
        hue and brightness minimums. Once the WCAG 3.0 standard is finalized, or
        open source libraries or formulas are made available to developers (the
        current licensing scheme of the beta formula is far too restrictive for
        us to be able to use it in this repository), this function should be
        completely overhauled. Accessibility is important.
        """

        if background_color:
            background_color_brightness = (
                299 * background_color[0] +
                587 * background_color[1] +
                114 * background_color[2]
            ) / 1000
            counter = -1
            while True:
                counter += 1
                self._character_colors_evaluated += 1
                if counter == 10000:
                    raise RuntimeError('Cannot find color with high enough contrast to background')
                proposed_color = (
                    randrange(256), # Red color value
                    randrange(256), # Green color value
                    randrange(256), # Blue color value
                )
                proposed_color_brightness = (
                    299 * proposed_color[0] +
                    587 * proposed_color[1] +
                    114 * proposed_color[2]
                ) / 1000
                brightness_difference = abs(proposed_color_brightness - background_color_brightness)
                hue_difference = (
                    abs(proposed_color[0] - background_color[0]) +
                    abs(proposed_color[1] - background_color[1]) +
                    abs(proposed_color[2] - background_color[2])
                )
                if (
                    brightness_difference >= self._settings._MINIMUM_COLOR_BRIGHTNESS_DIFFERENCE
                    and hue_difference >= self._settings._MINIMUM_COLOR_HUE_DIFFERENCE
                ):
                    return proposed_color
        else:
            return (
                randrange(256), # Red color value
                randrange(256), # Green color value
                randrange(256), # Blue color value
            )

    def _get_font(self):
        """Returns a random font from the FONTS setting"""

        typeface = secure_choice(self._settings._FONTS)
        default_size = self._settings._FONT_SIZES[typeface]
        if self._settings._FONT_SIZE_SHIFT_PERCENTAGE:
            offset = secure_randbelow(self._settings._FONT_SIZE_SHIFT_PERCENTAGE * 2) \
                - self._settings._FONT_SIZE_SHIFT_PERCENTAGE
            font_size = round(default_size + (default_size * (offset / 100)))
        else:
            font_size = default_size
        self._font_size_total += font_size
        return ImageFont.truetype(typeface, font_size)

    def _get_text_and_attributes(self):
        """Returns specified or randomly-generated text with randomized attributes for the CAPTCHA"""

        text = ''
        if self._settings._TEXT:
            text += self._settings._TEXT
        else:
            for _ in range(self._settings._TEXT_LENGTH):
                text += secure_choice(self._settings._CHARACTER_SET)

        text_and_attributes = []
        text_length = len(text)
        horizontal_anchors = text_length + 1
        current_anchor = 1
        previous_char_location = 0
        for character in text:
            character_and_attributes = [
                character, # The character to be written
                self._get_font(), # The font (typeface and size) to use for this character
                self._get_character_position( # The horizontal position of this character
                    current_anchor,
                    horizontal_anchors,
                    self._size[0], # Image width
                    self._settings._CHARACTER_HORIZONTAL_SHIFT_PERCENTAGE,
                    previous_char_location,
                ),
                self._get_character_position( # The vertical position of this character
                    1,
                    2,
                    self._size[1], # Image Height
                    self._settings._CHARACTER_VERTICAL_SHIFT_PERCENTAGE,
                    0,
                ),
                self._get_color_values(self._base_color),
            ]
            current_anchor += 1
            previous_char_location = character_and_attributes[2]
            text_and_attributes.append(character_and_attributes)

        if self._settings._CHARACTER_OVERLAP_ENABLED == False:
            text_and_attributes = self._prevent_character_overlap(text_and_attributes)

        return text, text_and_attributes

    def _prevent_character_overlap(self, text_and_attributes):
        """Repositions characters as necessary so that they do not overlap or get cut off"""

        def get_horizontal_extension(index):
            """Returns the distance from the (middle) text anchor to a horizontal edge of the character"""

            return round(
                text_and_attributes[index][1]
                    .getlength(text_and_attributes[index][0]) / 2
            )

        def get_vertical_extension(index):
            """Returns the distance from the (middle) text anchor to a vertical edge of the character"""

            return round(
                (
                    text_and_attributes[index][1]
                        .getbbox(text_and_attributes[index][0])[3]
                            -
                    text_and_attributes[index][1]
                        .getbbox(text_and_attributes[index][0])[1]
                ) / 2
            )

        # "Push" outwards from the middle character on any characters that are overlapping
        # another character, until no inside characters are left overlapping
        text_length = len(text_and_attributes)
        median = int(text_length / 2)
        shift_left = reversed(range(1, median + 1))
        shift_right = range(median, text_length - 1)
        largest_gap = 0
        index_largest_gap_to_right = median
        for index in shift_left:
            left_edge = text_and_attributes[index][2] - get_horizontal_extension(index)
            neighbor_right_edge = text_and_attributes[index - 1][2] + get_horizontal_extension(index - 1)
            if neighbor_right_edge > left_edge:
                self._character_position_corrections += 1
                text_and_attributes[index - 1][2] -= neighbor_right_edge - left_edge
            else:
                gap_size = left_edge - neighbor_right_edge
                if gap_size >= largest_gap:
                    largest_gap = gap_size
                    index_largest_gap_to_right = index - 1
        for index in shift_right:
            right_edge = text_and_attributes[index][2] + get_horizontal_extension(index)
            neighbor_left_edge = text_and_attributes[index + 1][2] - get_horizontal_extension(index + 1)
            if neighbor_left_edge < right_edge:
                self._character_position_corrections += 1
                text_and_attributes[index + 1][2] += right_edge - neighbor_left_edge
            else:
                gap_size = neighbor_left_edge - right_edge
                if gap_size >= largest_gap:
                    largest_gap = gap_size
                    index_largest_gap_to_right = index
        # If the first character gets cut off, shift it and all of the succeeding characters
        # (up to the largest gap) to the right, until the character is no longer cut off:
        left_edge = text_and_attributes[0][2] - get_horizontal_extension(0)
        if left_edge < 0:
            for i in range(index_largest_gap_to_right + 1):
                self._character_position_corrections += 1
                text_and_attributes[i][2] -= left_edge
        # If the last character gets cut off, shift it and all the preceding characters
        # (up to the largest gap) to the left, until the character is no longer cut off:
        right_edge = text_and_attributes[text_length - 1][2] + get_horizontal_extension(text_length - 1)
        if right_edge > self._size[0]:
            for i in reversed(range(index_largest_gap_to_right + 1, text_length)):
                self._character_position_corrections += 1
                text_and_attributes[i][2] -= right_edge - self._size[0]

        # Shift characters that are cut off by the top or bottom edges vertically, until
        # they are no longer cut off:
        for i in range(text_length):
            vertical_extension = get_vertical_extension(i)
            top = text_and_attributes[i][3] - vertical_extension
            if top < 0:
                self._character_position_corrections += 1
                text_and_attributes[i][3] -= top
            bottom = text_and_attributes[i][3] + vertical_extension
            if bottom > self._size[1]:
                self._character_position_corrections += 1
                text_and_attributes[i][3] -= (bottom - self._size[1])

        return text_and_attributes

    def base64(self):
        """Returns the CAPTCHA image as a base64-encoded string, for easy embedding"""

        if not self._base64:
            io = BytesIO()
            self.save(io)
            self._base64 = b64encode(io.getvalue()).decode()
            self._image_data_size = len(self._base64)
        return self._base64

    def generate(self):
        """Generates, or regenerates and replaces, the CAPTCHA and its metadata"""

        self._character_colors_evaluated = 0
        while True:
            self._character_position_corrections = 0
            self._font_size_total = 0
            self._layers_of_noise = 0
            self._create_image()
            # Catch exception raised when no compliant text colors can be found:
            try:
                self._draw_text()
            except RuntimeError:
                continue
            self._add_noise()
            self._clean_up()
            break
        self._generation += 1

    def get_stats(self):
        """Returns configuration and statistical information about this Captcha instance, as a dictionary"""

        return {
            'Average Font Size': round(self._font_size_total / self._settings._TEXT_LENGTH, 2),
            'Character Colors Evaluated': self._character_colors_evaluated,
            'Character Position Corrections': self._character_position_corrections,
            'Generation': self._generation,
            'Image Data Size': self._image_data_size,
            'Layers of Noise': self._layers_of_noise,
            'Settings': self._settings.get_settings(),
        }

    def get_settings(self):
        """Returns the Settings instance used to generate the CAPTCHA"""

        return self._settings

    def get_solution(self):
        """Returns the CAPTCHA's solution in plaintext"""

        return self._text

    def print_stats(self, return_string = False):
        """Prints configuration and statistical information about this Captcha instance"""

        stats = self.get_stats()
        stats_output = 'BOTBLOCK CAPTCHA INSTANCE\n\n'
        stats_output += f"    CAPTCHA Number for this Instance: {stats['Generation']}\n"
        stats_output += f"    Average Font Size per Character: {stats['Average Font Size']}\n"
        stats_output += f"    Number of Character Colors Evaluated: {stats['Character Colors Evaluated']}\n"
        stats_output += f"    Number of Corrections to Character Positions: {stats['Character Position Corrections']}\n"
        stats_output += f"    Image Data Size (In Bytes): {stats['Image Data Size']}\n"
        stats_output += f"    Layers of Noise Applied: {stats['Layers of Noise']}\n"
        stats_output += '\n    Settings:\n'
        stats_output += ('    ' + self._settings._pretty_format_settings(True).replace('\n', '\n    '))
        if return_string:
            return stats_output
        else:
            print(stats_output)

    def save(self, full_path):
        """Saves the generated CAPTCHA to a specified file"""

        if self._base64:
            with open(full_path, 'wb') as captcha_file:
                captcha_file.write(b64decode(self._base64))
        else:
            self._image.save(full_path, self._settings._FORMAT)

    def update_settings(self, settings = None):
        """Updates the Settings instance and (re)generates the CAPTCHA with the new settings"""

        if settings:
            if isinstance(settings, Settings):
                self._settings = settings
            else:
                raise TypeError(f'The "settings" argument supplied must be an instance of "Settings", not a "{type(settings)}"')
        else:
            self._settings = Settings()
        self.generate()

    def __repr__(self):
        """Returns a string that represents this Captcha instance"""

        return self.print_stats(True)


class Engine():
    """A backend for handling CAPTCHA configuration, creation, and validation"""

    def __init__(self, settings = None):
        """Initializes a new Engine object for configuring, creating, and validating CAPTCHAs"""

        if settings:
            if isinstance(settings, Settings):
                self._settings = settings
            else:
                raise TypeError(f'The "settings" argument supplied must be an instance of "Settings", not a "{type(settings)}"')
        else:
            self._settings = Settings()
        self._creation_time = time()
        self._get_queries = 0
        self._validate_queries = 0
        self._captcha_solves = 0
        self._shut_down = False
        self._fernet = Fernet(Fernet.generate_key())
        self._blob_to_validate = Queue(maxsize = 1)
        self._blob_validation_result = Queue(maxsize = 1)
        self._fresh_captchas = Queue(maxsize = self._settings._POOL_SIZE)
        self._modified_settings = Queue(maxsize = 1)
        self._stop_signal = Queue(maxsize = 3)
        self._used_captchas = Queue(maxsize = self._settings._POOL_SIZE)

        self._start_subprocesses()

    def __enter__(self):
        """Enter the runtime context and return this object or raise an exception"""

        if self._shut_down:
            raise RuntimeError('This engine is shut down')
        return self

    def _generate_captcha_instances(self):
        """Generates the Captcha instances with the correct settings"""

        for _ in range(self._settings._POOL_SIZE):
            if self._stop_signal.qsize() != 0:
                break
            self._fresh_captchas.put(Captcha(settings = self._settings))

        while self._stop_signal.qsize() == 0:
            sleep(1)
            captcha_instances = []
            if self._modified_settings.qsize() != 0:
                new_settings = self._modified_settings.get()
                # Remove all of the Captcha instances from the queues:
                for _ in range(self._settings._POOL_SIZE):
                    if self._stop_signal.qsize() != 0:
                        break
                    while True:
                        captcha_removed = False
                        if self._used_captchas.qsize():
                            try:
                                captcha = self._used_captchas.get(timeout = 0.1)
                                captcha_instances.append(captcha)
                                captcha_removed = True
                            except Empty:
                                pass
                        if (not captcha_removed) and self._fresh_captchas.qsize():
                            try:
                                captcha = self._fresh_captchas.get(timeout = 0.1)
                                captcha_instances.append(captcha)
                                captcha_removed = True
                            except Empty:
                                pass
                        if captcha_removed or (self._stop_signal.qsize() != 0):
                            break

                # Update all of the Captcha instances with the new settings:
                self._settings = new_settings
                for captcha in captcha_instances:
                    if self._stop_signal.qsize() != 0:
                        break
                    captcha.update_settings(self._settings)
                    self._fresh_captchas.put(captcha)

        # Close all queues before terminating:
        self._fresh_captchas.close()
        self._modified_settings.close()

        # Remove stop signal last, to indicate that the process has closed all other queues:
        self._stop_signal.get()
        self._stop_signal.close()

        # Wait to terminate the process until the queues' background threads have exited:
        self._fresh_captchas.join_thread()
        self._modified_settings.join_thread()
        self._stop_signal.join_thread()

    def _refresh_captchas(self):
        """Refreshes used Captcha instances, and makes them available for reuse"""

        before_generation_loop = 0
        while self._stop_signal.qsize() == 0:
            generation_loop_range = self._settings._POOL_SIZE
            if self._settings._RATE_LIMIT:
                if type(self._settings._RATE_LIMIT) == int:
                    before_generation_loop = time()
                    generation_loop_range = self._settings._RATE_LIMIT
                else:
                    generation_loop_range = 1
                    rate_limit_as_int = int(self._settings._RATE_LIMIT)
                    for _ in range(rate_limit_as_int):
                        if self._stop_signal.qsize() != 0:
                            break
                        sleep(1)
                    sleep(self._settings._RATE_LIMIT - rate_limit_as_int)
            for _ in range(generation_loop_range):
                if self._stop_signal.qsize() != 0:
                    break
                try:
                    captcha_to_refresh = self._used_captchas.get(timeout = 1)
                except Empty:
                    continue
                captcha_to_refresh.generate()
                self._fresh_captchas.put(captcha_to_refresh)
            if self._settings._RATE_LIMIT and type(self._settings._RATE_LIMIT) == int:
                time_to_sleep = 60 - int(time() - before_generation_loop)
                if time_to_sleep > 0:
                    for _ in range(time_to_sleep):
                        if self._stop_signal.qsize() != 0:
                            break
                        sleep(1)

        # Close all queues before terminating:
        self._fresh_captchas.close()
        self._used_captchas.close()

        # Remove stop signal last, to indicate that the process has closed all other queues:
        self._stop_signal.get()
        self._stop_signal.close()

        # Wait to terminate the process until the queues' background threads have exited:
        self._fresh_captchas.join_thread()
        self._used_captchas.join_thread()
        self._stop_signal.join_thread()

    def _start_subprocesses(self):
        """Starts the Engine's concurrent subprocesses for clearing and refreshing CAPTCHAs"""

        self._captcha_generation_process = Process(target = self._generate_captcha_instances, args = ())
        self._captcha_refresh_process = Process(target = self._refresh_captchas, args = ())
        self._captcha_validation_process = Process(target = self._validate_captchas, args = ())
        self._captcha_generation_process.start()
        self._captcha_refresh_process.start()
        self._captcha_validation_process.start()

    def _validate_captchas(self):
        """Checks for, adds, and expires CAPTCHA blobs from the validated blobs list"""

        validated_blobs = []
        validated_blobs_lock = Lock()

        def validate():
            while self._stop_signal.qsize() == 0:
                try:
                    blob_to_validate = self._blob_to_validate.get(timeout = 1)
                except Empty:
                    continue
                validated_blobs_lock.acquire()
                if blob_to_validate in validated_blobs:
                    self._blob_validation_result.put(False)
                else:
                    validated_blobs.append(blob_to_validate)
                    self._blob_validation_result.put(True)
                validated_blobs_lock.release()

        validate_thread = Thread(target = validate, args = ())
        validate_thread.start()

        while self._stop_signal.qsize() == 0:
            for _ in range(59):
                if self._stop_signal.qsize() == 0:
                    sleep(0.5)
                else:
                    break
            if self._stop_signal.qsize() != 0:
                break
            if validated_blobs:
                validated_blobs_lock.acquire()
                validated = []
                for encrypted_blob in validated_blobs:
                    validated.append(encrypted_blob)
                validated_blobs_lock.release()
                blobs_to_remove = []
                for encrypted_blob in validated:
                    try:
                        self._fernet.decrypt(encrypted_blob, ttl = self._settings._LIFETIME)
                    except InvalidToken:
                        blobs_to_remove.append(encrypted_blob)
                if blobs_to_remove:
                    validated_blobs_lock.acquire()
                    for encrypted_blob in blobs_to_remove:
                        validated_blobs.remove(encrypted_blob)
                    validated_blobs_lock.release()

        # Wait for thread to terminate:
        validate_thread.join()

        # Close all queues before terminating:
        self._blob_to_validate.close()
        self._blob_validation_result.close()

        # Remove stop signal last, to indicate that the process has closed all other queues:
        self._stop_signal.get()
        self._stop_signal.close()

        # Wait to terminate the process until the queues' background threads have exited:
        self._blob_to_validate.join_thread()
        self._blob_validation_result.join_thread()
        self._stop_signal.join_thread()

    def get_captcha(self, save_path = ''):
        """Returns (and optionally saves to disk) a new CAPTCHA and its metadata"""

        if self._shut_down:
            raise RuntimeError('This engine is shut down')

        new_captcha = self._fresh_captchas.get()
        captcha_as_base64 = new_captcha.base64()
        timestamp_and_encrypted_solution = self._fernet.encrypt(new_captcha.get_solution().encode()).decode()
        if save_path:
            new_captcha.save(save_path)
        self._used_captchas.put(new_captcha)
        self._get_queries += 1
        return {
            'base64_captcha': captcha_as_base64,
            'encrypted_blob': timestamp_and_encrypted_solution,
        }

    def get_settings(self):
        """Returns the Settings instance used by the Engine when generating CAPTCHAs"""

        return self._settings

    def get_stats(self):
        """Returns configuration and statistical information about this Engine instance, as a dictionary"""
        if self._shut_down:
            self._final_stats['Shut Down'] = True
            self._final_stats['Fresh CAPTCHAs'] = 0
            self._final_stats['Used CAPTCHAs'] = 0
            return self._final_stats
        else:
            stats = {'Shut Down': self._shut_down}
            stats['Active Total'] = int(time() - self._creation_time)
            if stats['Active Total'] == 0:
                stats['Active Total'] = 0.001
            tmp_active_time = int(stats['Active Total'])
            stats['Active Days'] = tmp_active_time // (60 * 60 * 24)
            tmp_active_time -= stats['Active Days'] * 60 * 60 * 24
            stats['Active Hours'] = tmp_active_time // (60 * 60)
            tmp_active_time -= stats['Active Hours'] * 60 * 60
            stats['Active Minutes'] = tmp_active_time // 60
            tmp_active_time -= stats['Active Minutes'] * 60
            stats['Active Seconds'] = tmp_active_time
            stats['CAPTCHAs Distributed'] = self._get_queries
            stats['Validation Attempts'] = self._validate_queries
            stats['CAPTCHA Solves'] = self._captcha_solves
            stats['Generations/Hour'] = round(
                stats['CAPTCHAs Distributed'] /
                (stats['Active Total'] / (60 * 60)), 2
            )
            stats['Validations/Hour'] = round(
                stats['Validation Attempts'] /
                (stats['Active Total'] / (60 * 60)), 2
            )
            stats['Solves/Hour'] = round(
                stats['CAPTCHA Solves'] /
                (stats['Active Total'] / (60 * 60)), 2
            )
            total_font_sizes = 0
            total_colors_evaluated = 0
            total_position_corrections = 0
            total_generations = 0
            total_data_sizes = 0
            total_noise_layers = 0
            available_captcha_instances = min(
                self._fresh_captchas.qsize() + self._used_captchas.qsize(),
                self._settings._POOL_SIZE
            )
            # When getting Captchas, try to take no longer than about 5 seconds,
            # to prevent long hangs when rate limiting is used with large pool sizes:
            before_loop_time = time()
            captcha_instances = []
            for _ in range(available_captcha_instances):
                try:
                    captcha_instances.append(self._fresh_captchas.get(timeout = 5))
                    if time() - before_loop_time >= 5:
                        break
                except Empty:
                    break
            stats['Fresh CAPTCHAs'] = len(captcha_instances)
            stats['Used CAPTCHAs'] = self._used_captchas.qsize()
            for captcha in captcha_instances:
                captcha_stats = captcha.get_stats()
                total_font_sizes += captcha_stats['Average Font Size']
                total_colors_evaluated += captcha_stats['Character Colors Evaluated']
                total_position_corrections += captcha_stats['Character Position Corrections']
                total_generations += captcha_stats['Generation']
                total_data_sizes += captcha_stats['Image Data Size']
                total_noise_layers += captcha_stats['Layers of Noise']
                self._fresh_captchas.put(captcha)
            num_instances = len(captcha_instances)
            if num_instances == 0:
                num_instances = 1
            stats['Captcha Instance Averages'] = {
                'Instances Analyzed': len(captcha_instances),
                'Average Font Size': round(total_font_sizes / num_instances, 2),
                'Character Colors Evaluated': round(total_colors_evaluated / num_instances, 2),
                'Character Position Corrections': round(total_position_corrections / num_instances, 2),
                'Generation': round(total_generations / num_instances, 2),
                'Image Data Size': round(total_data_sizes / num_instances, 2),
                'Layers of Noise': round(total_noise_layers / num_instances, 2),
            }
            stats['Settings'] = self._settings.get_settings()
            return stats

    def is_shut_down(self):
        """Returns True if the Engine instance has been shut down, and False if not"""

        return self._shut_down

    def print_stats(self, return_string = False):
        """Prints configuration and statistical information about this Engine instance"""

        stats = self.get_stats()
        stats_output = 'BOTBLOCK ENGINE INSTANCE\n\n'
        if stats['Shut Down']:
            stats_output += '    Shut Down: Yes\n'
        else:
            stats_output += '    Shut Down: No\n'
        stats_output += f"    Active: {stats['Active Days']} days, "
        stats_output += f"{stats['Active Hours']} hours, "
        stats_output += f"{stats['Active Minutes']} minutes, "
        stats_output += f"and {stats['Active Seconds']} seconds\n"
        if self._shut_down:
            stats_output += f"\n    Pool Size: 0\n"
        else:
            stats_output += f"\n    Pool Size: {stats['Settings']['POOL_SIZE']}\n"
        stats_output += f"    Fresh CAPTCHAs in Pool: {stats['Fresh CAPTCHAs']}\n"
        stats_output += f"    Used CAPTCHAs in Pool: {stats['Used CAPTCHAs']}\n"
        stats_output += f"\n    CAPTCHAs Distributed: {stats['CAPTCHAs Distributed']}\n"
        stats_output += f"    Validation Attempts: {stats['Validation Attempts']}\n"
        stats_output += f"    CAPTCHA Solves: {stats['CAPTCHA Solves']}\n"
        stats_output += f"\n    CAPTCHAs Generated per Hour: {stats['Generations/Hour']}\n"
        stats_output += f"    Validation Attempts per Hour: {stats['Validations/Hour']}\n"
        stats_output += f"    CAPTCHA Solves per Hour: {stats['Solves/Hour']}\n"
        stats_output += "\n    Average Stats per Captcha Instance "
        stats_output += f"({stats['Captcha Instance Averages']['Instances Analyzed']} Analyzed):\n"
        stats_output += '        Average number of CAPTCHAs generated per Captcha Instance: '
        stats_output += f"{stats['Captcha Instance Averages']['Generation']}\n"
        stats_output += '        Average Font Size per Character per CAPTCHA: '
        stats_output += f"{stats['Captcha Instance Averages']['Average Font Size']}\n"
        stats_output += '        Average Number of Character Colors Evaluated per CAPTCHA: '
        stats_output += f"{stats['Captcha Instance Averages']['Character Colors Evaluated']}\n"
        stats_output += '        Average Number of Corrections to Character Positions per CAPTCHA: '
        stats_output += f"{stats['Captcha Instance Averages']['Character Position Corrections']}\n"
        stats_output += '        Average Image Data Size (In Bytes) per CAPTCHA: '
        stats_output += f"{stats['Captcha Instance Averages']['Image Data Size']}\n"
        stats_output += '        Average Number of Layers of Noise Applied to Each CAPTCHA: '
        stats_output += f"{stats['Captcha Instance Averages']['Layers of Noise']}\n"
        stats_output += '\n    Settings:\n'
        stats_output += ('    ' + self._settings._pretty_format_settings().replace('\n', '\n    '))
        if return_string:
            return stats_output
        else:
            print(stats_output)

    def shut_down(self):
        """Prepares the Engine to be gracefully destroyed"""

        if self._shut_down:
            raise RuntimeError('This engine has already been shut down')

        self._final_stats = self.get_stats()
        self._shut_down = True
        self._stop_signal.put('STOP')
        self._stop_signal.put('STOP')
        self._stop_signal.put('STOP')

        # Empty and close all queues before terminating:
        while self._stop_signal.qsize() != 0: # .empty() is bugged, so must use .qsize()
            sleep(0.25)
        self._stop_signal.close()
        self._stop_signal.join_thread()
        while self._blob_to_validate.qsize() != 0:
            self._blob_to_validate.get()
        self._blob_to_validate.close()
        self._blob_to_validate.join_thread()
        while self._blob_validation_result.qsize() != 0:
            self._blob_validation_result.get()
        self._blob_validation_result.close()
        self._blob_validation_result.join_thread()
        while self._fresh_captchas.qsize() != 0:
            self._fresh_captchas.get()
        self._fresh_captchas.close()
        self._fresh_captchas.join_thread()
        while self._modified_settings.qsize() != 0:
            self._modified_settings.get()
        self._modified_settings.close()
        self._modified_settings.join_thread()
        while self._used_captchas.qsize() != 0:
            self._used_captchas.get()
        self._used_captchas.close()
        self._used_captchas.join_thread()

        # Ensure that all processes have terminated before returning:
        self._captcha_generation_process.join()
        self._captcha_refresh_process.join()
        self._captcha_validation_process.join()

    def update_settings(self, settings = None):
        """Updates the Engine's Settings instance and transitions its CAPTCHAs to the new settings"""

        if settings:
            if isinstance(settings, Settings):
                if settings.get_settings()['POOL_SIZE'] != self._settings.get_settings()['POOL_SIZE']:
                    raise RuntimeError('The POOL_SIZE setting cannot be dynamically updated')
                self._settings = settings
            else:
                raise TypeError(f'The "settings" argument supplied must be an instance of "Settings", not a "{type(settings)}"')
        else:
            self._settings = Settings()
        self._modified_settings.put(self._settings)

    def validate(self, encrypted_blob, proposed_solution):
        """Returns True if a CAPTCHA solution is valid, and False if not"""

        if self._shut_down:
            raise RuntimeError('This engine is shut down')
        self._validate_queries += 1

        try:
            true_solution = self._fernet.decrypt(encrypted_blob, ttl = self._settings._LIFETIME).decode()
        except InvalidToken:
            return False
        self._blob_to_validate.put(encrypted_blob)
        if not self._settings._CASE_SENSITIVE:
            proposed_solution = proposed_solution.lower()
            true_solution = true_solution.lower()
        if proposed_solution == true_solution:
            if self._blob_validation_result.get():
                self._captcha_solves += 1
                return True
            else:
                return False
        else:
            self._blob_validation_result.get()
            return False

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Shut down the engine and exit the runtime context"""

        self.shut_down()
        return True

    def __repr__(self):
        """Returns a string that represents this Engine instance"""

        return self.print_stats(True)


class Settings():
    """Contains all of the configuration settings used when generating CAPTCHAs"""

    def __init__(self, **kwargs):
        """Initializes a Settings object with default and/or customized settings passed as arguments"""

        self.set_default_values()
        self.set(**kwargs)

    def _calculate_font_sizes(self):
        """Calculates the font size to use with each typeface, based on provided settings"""

        self._FONT_SIZES = {}
        if self._TEXT:
            text_length = len(self._TEXT)
        else:
            text_length = self._TEXT_LENGTH
        text_length += 1
        for typeface in self._FONTS:
            font_size = round(self._WIDTH / text_length)
            font = ImageFont.truetype(typeface, font_size)
            widest_character = ''
            widest_character_length = 0
            for character in self._CHARACTER_SET:
                if font.getlength(character) > widest_character_length:
                    widest_character = character
                    widest_character_length = font.getlength(character)
            above_limit = (
                ImageFont.truetype(typeface, font_size).getlength(widest_character)
                * text_length
            ) >= self._WIDTH
            while True:
                font = ImageFont.truetype(typeface, font_size)
                maximum_length = font.getlength(widest_character) * text_length
                if maximum_length >= self._WIDTH:
                    font_size -= 1
                    if not above_limit:
                        break
                else:
                    if above_limit:
                        break
                    font_size += 1
            max_font_size = font_size
            font_size = round(max_font_size / (1 + self._FONT_SIZE_SHIFT_PERCENTAGE / 100))
            min_font_size = round(font_size - (font_size * (self._FONT_SIZE_SHIFT_PERCENTAGE / 100)))
            if min_font_size <= 0:
                raise ValueError('The WIDTH setting is too small to fit the provided number of characters')
            else:
                self._FONT_SIZES[typeface] = font_size

    def _pretty_format_settings(self, exclude_engine_settings = False):
        """Creates a human readable string of the current settings"""

        final_output = ''
        settings = self.get_settings()
        max_setting_name_length = 0
        for setting in settings:
            if len(setting) > max_setting_name_length:
                max_setting_name_length = len(setting)
        for setting in settings:
            if exclude_engine_settings:
                if setting in ['CASE_SENSITIVE', 'LIFETIME', 'POOL_SIZE', 'RATE_LIMIT']:
                    continue
            trailing_spaces = ' ' * (max_setting_name_length - len(setting) + 1)
            # Visually indicate that this value is a string (especially helpful for empty strings):
            if type(settings[setting]) == str:
                settings[setting] = f"'{settings[setting]}'"
            # Break down lists to print one item per line:
            if type(settings[setting]) == list and len(settings[setting]) > 1:
                final_output += f'    {setting}{trailing_spaces}= [\n'
                for list_item in settings[setting]:
                    final_output += f'    {" " * len(setting)}{trailing_spaces}      \'{list_item}\',\n'
                final_output += f'    {" " * len(setting)}{trailing_spaces}  ]\n'
            else:
                final_output += f'    {setting}{trailing_spaces}= {settings[setting]}\n'
        return final_output[:-1]

    def compare_efficiency(self, settings = None, test_length = 300):
        """Compares the CAPTCHA generation efficiency of this instance's settings with provided or default settings"""

        settings_origin_text = 'provided'
        if settings:
            if not isinstance(settings, Settings):
                raise TypeError(f'The "settings" argument supplied must be an instance of "Settings", not a "{type(settings)}"')
        else:
            settings_origin_text = 'default'
            settings = Settings()

        print('CAPTCHA Settings CPU Efficiency Benchmark')
        print('')
        print('For the most accurate results, please limit any other activity on your system until')
        print(f'the benchmark completes. This benchmark is scheduled to take about {test_length} seconds.')
        print('')
        print('Initializing...')
        print('')

        captcha_current_settings = Captcha(self)
        captcha_new_settings = Captcha(settings)

        current_start_time = perf_counter_ns()
        for _ in range(10):
            captcha_current_settings.generate()
        current_end_time = perf_counter_ns()
        new_start_time = perf_counter_ns()
        for _ in range(10):
            captcha_new_settings.generate()
        new_end_time = perf_counter_ns()

        time_per_longest_settings = max(
            (current_end_time - current_start_time) / 10,
            (new_end_time - new_start_time) / 10,
        )
        iterations_per_settings = int(test_length / 2 * 1_000_000_000 / time_per_longest_settings)
        if not iterations_per_settings:
            print('Error!')
            print('At least one Settings instance is too inefficient to comprehensively benchmark.')
            return
        status_divisor = iterations_per_settings // 10 + 1

        print('Benchmark Started!')
        print('')

        print('Benchmark 0% complete...')
        current_start_time = perf_counter_ns()
        for i in range(iterations_per_settings):
            if (i % status_divisor == 0) and (i != 0):
                print(
                    'Benchmark ',
                    round(i / (iterations_per_settings * 2) * 100),
                    '% complete...',
                    sep = ''
                )
            captcha_current_settings.generate()
        current_end_time = perf_counter_ns()
        print('Benchmark 50% complete...')
        new_start_time = perf_counter_ns()
        for i in range(iterations_per_settings):
            if (i % status_divisor == 0) and (i != 0):
                print(
                    'Benchmark ',
                    round(
                        (i + iterations_per_settings) /
                        (iterations_per_settings * 2) * 100),
                    '% complete...',
                    sep = ''
                )
            captcha_new_settings.generate()
        new_end_time = perf_counter_ns()
        print('Benchmark 100.0% complete!')

        current_results = current_end_time - current_start_time
        new_results = new_end_time - new_start_time
        total_time = round((current_results + new_results) / 1_000_000_000, 3)

        print('')
        print('')
        print('Benchmark Results:')
        print('')
        print(
            'During the benchmark,',
            iterations_per_settings * 2,
            'CAPTCHAS were generated in about',
            total_time,
            'seconds.'
        )
        print(
            'This Settings instance took about',
            round(current_results / 1_000_000_000, 3),
            'seconds to generate its',
            iterations_per_settings,
            'CAPTCHAs.'
        )
        print(
            f'The {settings_origin_text} Settings instance took about',
            round(new_results / 1_000_000_000, 3),
            'seconds to generate its',
            iterations_per_settings,
            'CAPTCHAs.'
        )
        print('')
        if current_results > new_results:
            print(
                'The ',
                settings_origin_text,
                ' Settings instance was found to be about ',
                round((current_results / new_results - 1) * 100, 3),
                '% more efficient.',
                sep = '',
            )
        else:
            print(
                'This Settings instance was found to be about ',
                round((new_results / current_results - 1) * 100, 3),
                '% more efficient.',
                sep = '',
            )

    def get_default_settings(self):
        """Returns all settings and their default values as a dictionary"""

        return Settings().get_settings()

    def get_settings(self):
        """Returns all settings and their current values as a dictionary"""

        return {
            'WIDTH': self._WIDTH,
            'HEIGHT': self._HEIGHT,
            'FORMAT': self._FORMAT,
            'TEXT': self._TEXT,
            'TEXT_LENGTH': self._TEXT_LENGTH,
            'CHARACTER_SET': self._CHARACTER_SET,
            'FONTS': self._FONTS,
            'CHARACTER_HORIZONTAL_SHIFT_PERCENTAGE': self._CHARACTER_HORIZONTAL_SHIFT_PERCENTAGE,
            'CHARACTER_VERTICAL_SHIFT_PERCENTAGE': self._CHARACTER_VERTICAL_SHIFT_PERCENTAGE,
            'FONT_SIZE_SHIFT_PERCENTAGE': self._FONT_SIZE_SHIFT_PERCENTAGE,
            'CHARACTER_OVERLAP_ENABLED': self._CHARACTER_OVERLAP_ENABLED,
            'MAXIMUM_NOISE': self._MAXIMUM_NOISE,
            'MINIMUM_COLOR_BRIGHTNESS_DIFFERENCE': self._MINIMUM_COLOR_BRIGHTNESS_DIFFERENCE,
            'MINIMUM_COLOR_HUE_DIFFERENCE': self._MINIMUM_COLOR_HUE_DIFFERENCE,
            'CASE_SENSITIVE': self._CASE_SENSITIVE,
            'LIFETIME': self._LIFETIME,
            'POOL_SIZE': self._POOL_SIZE,
            'RATE_LIMIT': self._RATE_LIMIT,
        }

    def get_supported_image_formats(self):
        """Returns a list of all of the supported output image formats"""

        return [
            'BMP',
            'GIF',
            'ICO',
            'JPEG',
            'PNG',
            'TIFF',
            'WEBP',
            'PDF',
        ]

    def set(self, **kwargs):
        """Sets specified settings to specified values, then performs validation"""

        for setting in kwargs:
            if setting == 'WIDTH':
                self._WIDTH = kwargs[setting]
            elif setting == 'HEIGHT':
                self._HEIGHT = kwargs[setting]
            elif setting == 'FORMAT':
                self._FORMAT = kwargs[setting].upper()
            elif setting == 'TEXT':
                self._TEXT = kwargs[setting]
            elif setting == 'TEXT_LENGTH':
                self._TEXT_LENGTH = kwargs[setting]
            elif setting == 'CHARACTER_SET':
                self._CHARACTER_SET = kwargs[setting]
            elif setting == 'FONTS':
                self._FONTS = kwargs[setting]
            elif setting == 'CHARACTER_HORIZONTAL_SHIFT_PERCENTAGE':
                self._CHARACTER_HORIZONTAL_SHIFT_PERCENTAGE = kwargs[setting]
            elif setting == 'CHARACTER_VERTICAL_SHIFT_PERCENTAGE':
                self._CHARACTER_VERTICAL_SHIFT_PERCENTAGE = kwargs[setting]
            elif setting == 'FONT_SIZE_SHIFT_PERCENTAGE':
                self._FONT_SIZE_SHIFT_PERCENTAGE = kwargs[setting]
            elif setting == 'CHARACTER_OVERLAP_ENABLED':
                self._CHARACTER_OVERLAP_ENABLED = kwargs[setting]
            elif setting == 'MAXIMUM_NOISE':
                self._MAXIMUM_NOISE = kwargs[setting]
            elif setting == 'MINIMUM_COLOR_BRIGHTNESS_DIFFERENCE':
                self._MINIMUM_COLOR_BRIGHTNESS_DIFFERENCE = kwargs[setting]
            elif setting == 'MINIMUM_COLOR_HUE_DIFFERENCE':
                self._MINIMUM_COLOR_HUE_DIFFERENCE = kwargs[setting]
            elif setting == 'CASE_SENSITIVE':
                self._CASE_SENSITIVE = kwargs[setting]
            elif setting == 'LIFETIME':
                self._LIFETIME = kwargs[setting]
            elif setting == 'POOL_SIZE':
                self._POOL_SIZE = kwargs[setting]
            elif setting == 'RATE_LIMIT':
                self._RATE_LIMIT = kwargs[setting]
            else:
                raise NameError(f'The setting "{setting}" does not exist')

        self.validate_settings()

    def set_default_values(self):
        """Sets all settings to their default value"""

        self._WIDTH = 750 # In pixels
        self._HEIGHT = 250 # In pixels
        self._FORMAT = 'PNG'
        self._TEXT = '' # Randomly generated if blank
        self._TEXT_LENGTH = 6
        self._CHARACTER_SET = 'abcdefghjkmnpqrstuvwxyzABCDEFGHJKMNPQRSTUVWXYZ23456789' # Commonly-confused characters discluded
        self._FONTS = [ # The MIT license used for this repository does not apply to these open source fonts
            files('botblock.fonts').joinpath('Amatic-Bold.ttf').as_posix(),
            files('botblock.fonts').joinpath('LifeSavers-Bold.ttf').as_posix(),
            files('botblock.fonts').joinpath('TungusFont_Tinet.ttf').as_posix(),
        ]
        self._CHARACTER_HORIZONTAL_SHIFT_PERCENTAGE = 65
        self._CHARACTER_VERTICAL_SHIFT_PERCENTAGE = 65
        self._FONT_SIZE_SHIFT_PERCENTAGE = 25
        self._CHARACTER_OVERLAP_ENABLED = False
        self._MAXIMUM_NOISE = 25 # In maximum layers of noise
        self._MINIMUM_COLOR_BRIGHTNESS_DIFFERENCE = 65 # Per W3 should be 125 in production
        self._MINIMUM_COLOR_HUE_DIFFERENCE = 250 # Per W3 should be 500 in production
        self._CASE_SENSITIVE = False
        self._LIFETIME = 600 # In seconds
        self._POOL_SIZE = 500 # In Captcha instances
        self._RATE_LIMIT = 0 # Disabled

        self.validate_settings()

    def print_default_settings(self):
        """Prints all settings and their default values"""

        print('Default Settings:')
        print(Settings()._pretty_format_settings())

    def print_settings(self):
        """Prints all of the settings and their current values"""

        print('Current Settings:')
        print(self._pretty_format_settings())

    def validate_settings(self):
        """Checks that all settings are valid, and raises an exception if not"""

        if type(self._WIDTH) is not int:
            raise TypeError('The WIDTH setting is not an int')
        if self._WIDTH < 10:
            raise ValueError('The WIDTH setting cannot be less than 10')
        if type(self._HEIGHT) is not int:
            raise TypeError('The HEIGHT setting is not an int')
        if self._HEIGHT < 5:
            raise ValueError('The HEIGHT setting cannot be less than 5')
        if self._HEIGHT > self._WIDTH:
            raise ValueError('The HEIGHT setting cannot be greater than the WIDTH setting')
        if type(self._FORMAT) is not str:
            raise TypeError('The FORMAT setting is not a str')
        if self._FORMAT not in self.get_supported_image_formats():
            raise ValueError('The FORMAT setting provided is not a supported output image format')
        if type(self._TEXT) is not str:
            raise TypeError('The TEXT setting is not a str')
        if self._TEXT and (len(self._TEXT) < 3):
            raise ValueError('The length of the TEXT setting string cannot be less than 3')
        if type(self._TEXT_LENGTH) is not int:
            raise TypeError('The TEXT_LENGTH setting is not an int')
        if self._TEXT_LENGTH < 3:
            raise ValueError('The TEXT_LENGTH setting cannot be less than 3')
        if type(self._CHARACTER_SET) is not str:
            raise TypeError('The CHARACTER_SET setting is not a str')
        if not self._CHARACTER_SET and not self._TEXT:
            raise ValueError('The length of the CHARACTER_SET setting string cannot be less than 1 when the TEXT setting is blank')
        for character in self._CHARACTER_SET:
            if self._CHARACTER_SET.count(character) > 1:
                raise ValueError(
                    'The CHARACTER_SET setting may not contain duplicate characters; ' +
                    f"the '{character}' character was found {self._CHARACTER_SET.count(character)} times"
                )
        if type(self._FONTS) is not list:
            raise TypeError('The FONTS setting is not a list')
        if not self._FONTS:
            raise ValueError('The FONTS setting must contain at least one str')
        for font in self._FONTS:
            if type(font) is not str:
                raise TypeError('The FONTS setting contains at least one item that is not a str')
            if not Path(font).is_file():
                raise ValueError(f"The font file '{font}' from the FONTS setting could not be found")
        if type(self._CHARACTER_HORIZONTAL_SHIFT_PERCENTAGE) is not int:
            raise TypeError('The CHARACTER_HORIZONTAL_SHIFT_PERCENTAGE setting is not an int')
        if (self._CHARACTER_HORIZONTAL_SHIFT_PERCENTAGE < 0) or (self._CHARACTER_HORIZONTAL_SHIFT_PERCENTAGE > 100):
            raise ValueError('The CHARACTER_HORIZONTAL_SHIFT_PERCENTAGE setting must be an integer from 0 through 100')
        if type(self._CHARACTER_VERTICAL_SHIFT_PERCENTAGE) is not int:
            raise TypeError('The CHARACTER_VERTICAL_SHIFT_PERCENTAGE setting is not an int')
        if (self._CHARACTER_VERTICAL_SHIFT_PERCENTAGE < 0) or (self._CHARACTER_VERTICAL_SHIFT_PERCENTAGE > 100):
            raise ValueError('The CHARACTER_VERTICAL_SHIFT_PERCENTAGE setting must be an integer from 0 through 100')
        if type(self._FONT_SIZE_SHIFT_PERCENTAGE) is not int:
            raise TypeError('The FONT_SIZE_SHIFT_PERCENTAGE setting is not an int')
        if (self._FONT_SIZE_SHIFT_PERCENTAGE < 0) or (self._FONT_SIZE_SHIFT_PERCENTAGE > 100):
            raise ValueError('The FONT_SIZE_SHIFT_PERCENTAGE setting must be an integer from 0 through 100')
        if type(self._CHARACTER_OVERLAP_ENABLED) is not bool:
            raise TypeError('The CHARACTER_OVERLAP_ENABLED setting is not a bool')
        if type(self._MAXIMUM_NOISE) is not int:
            raise TypeError('The MAXIMUM_NOISE setting is not an int')
        if self._MAXIMUM_NOISE < 0:
            raise ValueError('The MAXIMUM_NOISE setting cannot be less than 0')
        if type(self._MINIMUM_COLOR_BRIGHTNESS_DIFFERENCE) is not int:
            raise TypeError('The MINIMUM_COLOR_BRIGHTNESS_DIFFERENCE setting is not an int')
        if self._MINIMUM_COLOR_BRIGHTNESS_DIFFERENCE > 200:
            raise ValueError('The MINIMUM_COLOR_BRIGHTNESS_DIFFERENCE setting must be an integer less than or equal to 200')
        if type(self._MINIMUM_COLOR_HUE_DIFFERENCE) is not int:
            raise TypeError('The MINIMUM_COLOR_HUE_DIFFERENCE setting is not an int')
        if self._MINIMUM_COLOR_HUE_DIFFERENCE > 600:
            raise ValueError('The MINIMUM_COLOR_HUE_DIFFERENCE setting must be an integer less than or equal to 600')
        if type(self._CASE_SENSITIVE) is not bool:
            raise TypeError('The CASE_SENSITIVE setting is not a bool')
        if type(self._LIFETIME) is not int:
            raise TypeError('The LIFETIME setting is not an int')
        if self._LIFETIME < 0:
            raise ValueError('The LIFETIME setting cannot be less than 0')
        if type(self._POOL_SIZE) is not int:
            raise TypeError('The POOL_SIZE setting is not an int')
        if self._POOL_SIZE < 1:
            raise ValueError('The POOL_SIZE setting must be an integer greater than 0')
        if type(self._RATE_LIMIT) is not int and type(self._RATE_LIMIT) is not float:
            raise TypeError('The RATE_LIMIT setting is not an int or float')
        if self._RATE_LIMIT < 0:
            raise ValueError('The RATE_LIMIT setting cannot be less than 0')
        if type(self._RATE_LIMIT) == float and self._RATE_LIMIT == 0.0:
            self._RATE_LIMIT = 0

        self._calculate_font_sizes()

    def __repr__(self):
        """Returns a string that represents this Settings instance"""

        return 'BOTBLOCK SETTINGS INSTANCE\n\nCurrent Settings:\n' + self._pretty_format_settings()
