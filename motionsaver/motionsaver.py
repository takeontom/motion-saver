from collections import deque
from datetime import timedelta


class MotionSaver(object):
    def __init__(self):
        self.recent_images = deque()

        self.save_previous_seconds = 0

    def add_image(self, image, datetime_taken, save_path):
        """Add an image to the MotionSaver for the magic to happen."""

        # * add to stack
        # * detect motion
        # * save entire stack, but keep the stack populated for future motion
        #   detection
        # * set motioned detected flag
        # * keep saving images until time expired
        # * unset flag

        pass

    def push_recent_image(self, image, datetime_taken, save_path):
        """Append the supplied image to the recent images deque.

        Will also tidy the queue to remove expired images.
        """
        as_tuple = (image, datetime_taken, save_path)
        self.recent_images.append(as_tuple)

        min_datetime = datetime_taken - timedelta(
            seconds=self.save_previous_seconds
        )
        self.remove_images_older_than(self.recent_images, min_datetime)

    def remove_images_older_than(self, images_deque, older_than):
        """Remove expired images from the supplied images deque.

        Will always attempt to leave at least two images in the deque,
        otherwise streams with framerates lower than the
        `save_previous_seconds` attribute will never have any images to detect
        motion with."""
        while len(images_deque) > 2 and images_deque[0][1] < older_than:
            images_deque.popleft()

    def get_motion_level(self, images):
        """Return the level of motion in the supplied iterable of images."""
        if len(images) < 2:
            # There's not enough images to compare!
            return 0

        # For now, just get the 2 latest images and return the diff perc
        # between them
        image_1 = images[-2][0]
        image_2 = images[-1][0]
        return self.image_diff_perc(image_1, image_2)

    def image_diff_perc(self, image_1, image_2):
        """Simple check to find the difference between two images. Pretty
        crude."""
        if image_1 == image_2:
            # Is exactly the same image, likely opened from the same file.
            return 0

        width, height = 32, 20
        image_1_small = image_1.resize((width, height)).convert('L')
        image_2_small = image_2.resize((width, height)).convert('L')

        image_1_small_data = image_1_small.getdata()
        image_2_small_data = image_2_small.getdata()

        num_pixels = width * height
        max_diff = num_pixels * 255

        total_diff = 0
        for i, value_1 in enumerate(image_1_small_data):
            value_2 = image_2_small_data[i]
            total_diff += abs(value_1 - value_2)

        perc_diff = total_diff / max_diff
        return perc_diff
