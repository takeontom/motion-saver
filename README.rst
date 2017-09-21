motion-saver
============

Easily pick out and save images which contain motion from a stream of images.


Features
--------

* Send images into the MotionSaver, and it'll save the ones with motion.
* Optionally save images from before and after motion occurs.
* Easy to configure and use.


Requirements
------------

* Python 3.5 or above
* Pillow 4+


Installation
------------

.. code:: sh

    pip install motion-saver


Quick start
-----------


Examples
--------

Save a stream of images
.......................

Continuously add a stream of images to the Motion Saver. When motion is
detected it will save the previous 30 seconds of images, and keep saving until
20 seconds has passed since the last motion was detected.

.. code:: python

    from datetime import datetime

    from motionsaver import MotionSaver

    ms = MotionSaver()
    ms.motion_threshold = 0.1
    ms.save_previous_seconds = 30
    ms.save_post_seconds = 20

    while True:
        now = datetime.now()

        pillow_img = get_image()
        filename = '{}.jpg'.format(now.strftime('%Y%m%d-%H%M%S'))

        ms.add_image(pillow_img, now, filename)


License
-------

camgrab is free software, distributed under the MIT license.
