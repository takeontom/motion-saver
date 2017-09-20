import os
from collections import deque
from datetime import datetime, timedelta

from PIL import Image

from motionsaver import MotionSaver


class TestMotionSaver(object):
    def test__init__(self):
        ms = MotionSaver()

        assert isinstance(ms.recent_images, deque)
        assert len(ms.recent_images) == 0

        assert ms.save_previous_seconds == 5
        assert ms.save_post_seconds == 5
        assert ms.motion_threshold == 0.1
        assert ms.last_motion is None

    def test_add_image(self):
        pass

    def test_save_images(self, mocker):
        def make_image_dict(saved=False):
            image_dict = {
                'image': Image.Image(),
                'datetime_taken': datetime.now(),
                'save_path': '/some/save/path.jpg'
            }
            if saved:
                image_dict['saved'] = True
            return image_dict

        image_dicts = (
            make_image_dict(True),
            make_image_dict(True),
            make_image_dict(False),
            make_image_dict(False),
            make_image_dict(False),
            make_image_dict(False),
            make_image_dict(True),
            make_image_dict(True),
            make_image_dict(True),
        )

        images_deque = deque(image_dicts)

        ms = MotionSaver()

        mocker.patch.object(ms, 'save_image', return_value=True)
        ms.save_images(images_deque)

        assert ms.save_image.call_count == 4
        for image_dict in images_deque:
            assert image_dict['saved'] is True

    def test_save_image(self, mocker):
        im = Image.Image()
        mocker.patch.object(im, 'save')

        save_path = 'some/save/path.jpg'

        mock_makedirs = mocker.patch('motionsaver.motionsaver.os.makedirs')
        mock_exists = mocker.patch(
            'motionsaver.motionsaver.os.path.exists', return_value=False
        )

        ms = MotionSaver()

        result = ms.save_image(im, save_path)

        assert result is True
        mock_exists.assert_called_once_with(save_path)
        mock_makedirs.assert_called_once_with('some/save', exist_ok=True)
        im.save.assert_called_once_with(save_path)

    def test_save_image__exists(self, mocker):
        im = Image.Image()
        mocker.patch.object(im, 'save')

        save_path = 'some/save/path.jpg'

        mock_makedirs = mocker.patch('motionsaver.motionsaver.os.makedirs')
        mock_exists = mocker.patch(
            'motionsaver.motionsaver.os.path.exists', return_value=True
        )

        ms = MotionSaver()

        ms.save_image(im, save_path)

        mock_exists.assert_called_once_with(save_path)
        mock_makedirs.assert_not_called()
        im.save.assert_not_called()

    def test_push_recent_image(self, mocker):
        ms = MotionSaver()
        ms.save_previous_seconds = 30
        save_previous_seconds_delta = timedelta(seconds=30)
        mocker.patch.object(ms, 'remove_images_older_than')

        image = Image.Image()
        datetime_taken = datetime.now()
        save_path = '/some/path/image.jpg'

        ms.push_recent_image(image, datetime_taken, save_path)

        assert ms.recent_images[0] == {
            'image': image,
            'datetime_taken': datetime_taken,
            'save_path': save_path
        }

        expired_datetime = datetime_taken - save_previous_seconds_delta
        ms.remove_images_older_than.assert_called_once_with(
            ms.recent_images, expired_datetime
        )

        assert len(ms.recent_images) == 1

    def test_remove_images_older_than(self):
        older_than = datetime(2017, 8, 15, 14, 0, 0)

        images_deque = deque()

        old_image_dates = (
            datetime(2016, 1, 1, 0, 0, 0),
            datetime(2017, 8, 15, 13, 59, 58),
            datetime(2017, 8, 15, 13, 59, 59),
        )

        ok_image_dates = (
            older_than,
            datetime(2017, 8, 15, 14, 0, 1),
            datetime(2017, 8, 15, 14, 0, 2),
            datetime(2018, 1, 1, 0, 0, 0),
        )

        for a_date in old_image_dates + ok_image_dates:
            image_dict = {
                'image': Image.Image(),
                'datetime_taken': a_date,
                'save_path': 'some/file.jpg',
            }
            images_deque.append(image_dict)

        assert len(images_deque) == len(old_image_dates) + len(ok_image_dates)

        ms = MotionSaver()
        ms.remove_images_older_than(images_deque, older_than)

        assert len(images_deque) == len(ok_image_dates)

        for i, image_dict in enumerate(images_deque):
            assert ok_image_dates[i] == image_dict['datetime_taken']

    def test_remove_images_older_than__dont_empty(self):
        older_than = datetime(2017, 8, 15, 14, 0, 0)

        images_deque = deque()

        old_image_dates = (
            datetime(2016, 1, 1, 0, 0, 0),
            datetime(2017, 8, 15, 13, 59, 58),
            datetime(2017, 8, 15, 13, 59, 59),
        )

        for a_date in old_image_dates:
            image_dict = {
                'image': Image.Image(),
                'datetime_taken': a_date,
                'save_path': 'some/file.jpg',
            }
            images_deque.append(image_dict)

        assert len(images_deque) == len(old_image_dates)

        ms = MotionSaver()
        ms.remove_images_older_than(images_deque, older_than)

        assert len(images_deque) == 2
        assert images_deque[0]['datetime_taken'] == datetime(
            2017, 8, 15, 13, 59, 58
        )
        assert images_deque[1]['datetime_taken'] == datetime(
            2017, 8, 15, 13, 59, 59
        )

    def test_get_motion_level(self, mocker):
        image_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'images',
        )
        image_paths = (
            'dartcam-1.jpg',
            'dartcam-1.1.jpg',
            'dartcam-2.jpg',
            'dartcam-2.1.jpg',
        )
        images = deque()
        for image_path in image_paths:
            im = Image.open(os.path.join(image_dir, image_path))
            image_dict = {
                'image': im,
                'datetime_taken': datetime.now(),
                'save_path': 'some/file.jpg',
            }
            images.append(image_dict)

        ms = MotionSaver()
        mocker.patch.object(ms, 'image_diff_perc', return_value=0.5)

        assert ms.get_motion_level(images) == 0.5

        image_1 = images[-2]['image']
        image_2 = images[-1]['image']
        ms.image_diff_perc.assert_called_once_with(image_1, image_2)

    def test_get_motion_level__not_enough_images(self):
        image_path = '{}/images/dartcam-1.jpg'.format(
            os.path.dirname(os.path.abspath(__file__))
        )
        im = Image.open(image_path)

        images = deque()

        images.append((im, datetime.now(), '/some/file.jpg'))

        ms = MotionSaver()
        assert ms.get_motion_level(images) == 0

    def test_get_motion_level__no_images(self):
        images = deque()
        ms = MotionSaver()
        assert ms.get_motion_level(images) == 0

    def test_image_diff_perc(self):
        image_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            'images',
        )
        image_1_path = os.path.join(image_dir, 'dartcam-1.jpg')
        image_1_dup_path = os.path.join(image_dir, 'dartcam-1.1.jpg')
        image_2_path = os.path.join(image_dir, 'riverdart-1.jpg')

        image_1 = Image.open(image_1_path)
        image_1_dup = Image.open(image_1_dup_path)
        image_2 = Image.open(image_2_path)
        black_image = Image.new('RGB', (640, 480))
        white_image = Image.new('RGB', (640, 480), (255, 255, 255))

        ms = MotionSaver()

        assert ms.image_diff_perc(image_1, image_1) == 0
        assert ms.image_diff_perc(image_1, image_1_dup) == 0
        assert ms.image_diff_perc(image_2, image_2) == 0
        assert ms.image_diff_perc(image_1, image_2) >= 0.3
        assert ms.image_diff_perc(image_1, image_2) <= 0.4

        assert ms.image_diff_perc(black_image, black_image) == 0
        assert ms.image_diff_perc(white_image, white_image) == 0
        assert ms.image_diff_perc(black_image, white_image) == 1
        assert ms.image_diff_perc(white_image, black_image) == 1
