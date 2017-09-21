import os
from collections import deque
from datetime import timedelta


class MotionSaver(object):
    def __init__(self):
        self.recent_images = deque()

        self.motion_threshold = 0.1
        self.save_previous_seconds = 5
        self.save_post_seconds = 5
        self.last_motion = None
        self.last_motion_level = 0
        self.commit = True

    def add_image(self, image, datetime_taken, save_path):
        """Add an image to the MotionSaver for the magic to happen."""

        self.push_recent_image(image, datetime_taken, save_path)

        self.last_motion_level = self.get_motion_level(self.recent_images)

        if self.last_motion_level >= self.motion_threshold:
            self.last_motion = datetime_taken

        if not self.last_motion:
            # No motion, nothing to do
            return

        last_motion_seconds = (datetime_taken - self.last_motion).seconds
        if last_motion_seconds <= self.save_post_seconds and self.commit:
            self.save_images(self.recent_images)

    def save_images(self, image_dicts):
        for image_dict in image_dicts:
            if not image_dict.get('saved', False):
                image = image_dict['image']
                save_path = image_dict['save_path']
                image_dict['saved'] = self.save_image(image, save_path)

    def save_image(self, image, save_path):
        if os.path.exists(save_path):
            return

        save_dir = os.path.dirname(save_path)
        os.makedirs(save_dir, exist_ok=True)
        image.save(save_path)
        return True

    def push_recent_image(self, image, datetime_taken, save_path):
        """Append the supplied image to the recent images deque.

        Will also tidy the queue to remove expired images.
        """
        as_dict = {
            'image': image,
            'datetime_taken': datetime_taken,
            'save_path': save_path
        }
        self.recent_images.append(as_dict)

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
        while (
            len(images_deque) > 2
            and images_deque[0]['datetime_taken'] < older_than
        ):
            images_deque.popleft()

    def get_motion_level(self, images):
        """Return the level of motion in the supplied iterable of images."""
        if len(images) < 2:
            # There's not enough images to compare!
            return 0

        # For now, just get the 2 latest images and return the diff perc
        # between them
        image_1 = images[-2]['image']
        image_2 = images[-1]['image']
        return self.image_diff_perc(image_1, image_2)

    def image_diff_perc(self, image_1, image_2):
        """Simple check to find the percentage difference between two images.
        Pretty crude."""
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
