import os
from azure.ai.vision.imageanalysis import ImageAnalysisClient
from azure.ai.vision.imageanalysis.models import VisualFeatures
from azure.core.credentials import AzureKeyCredential

import numpy as np
import imutils
import cv2

def capture_frame():
    VehicleVideo = cv2.VideoCapture(config.vision['camera'])

    if not VehicleVideo.isOpened():
        print("Error: Couldn't open the webcam.")
        return None

    # Capture a frame
    ret, frame = VehicleVideo.read()

    # Release the webcam
    VehicleVideo.release()

    if not ret:
        print("Error: Couldn't capture a frame.")
        return None
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Convert the NumPy array to bytes
    _, img_crop_data = cv2.imencode('.jpg', frame)
    img_crop_bytes = img_crop_data.tobytes()

    return img_crop_bytes


"""
    Set these two environment variables before running the sample:
    1) VISION_ENDPOINT - Your endpoint URL, in the form https://your-resource-name.cognitiveservices.azure.com
                         where `your-resource-name` is your unique Azure Computer Vision resource name.
    2) VISION_KEY - Your Computer Vision key (a 32-character Hexadecimal number)
"""
# Set the values of your computer vision endpoint and computer vision key
# as environment variables:
import config
try:
    endpoint = config.vision['endpoint']
    key = config.vision['key']
except KeyError:
    print("Missing environment variable 'VISION_ENDPOINT' or 'VISION_KEY'")
    print("Set them before running this sample.")
    exit()


# REFERENCED FROM: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/vision/azure-ai-vision-imageanalysis/samples/sample_tags_image_file.py
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to extract content tags in an image file sample.jpg, using a synchronous client.
    Tags are supported for thousands of recognizable objects, living beings, scenery, and actions that appear in images.

    Tags names are supported in multiple languages, the default being English. You can set the `language` argument when
    calling `analyze` to a 2-letter language code. See [Image Analysis supported languages](https://aka.ms/cv-languages).

    The synchronous (blocking) `analyze` method call returns an `ImageAnalysisResult` object.
    Its `tags` property (a `TagsResult` object) contains a list of `DetectedTag` objects. Each has:
    - The tag name, for example: "indoor", "table".
    - A confidence score in the range [0, 1], with higher values indicating greater confidences in the tag.
"""


def vehicle_detection(image):
    # Create an Image Analysis client
    client = ImageAnalysisClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key)
    )

    # Do 'Tags' analysis on an image stream. This will be a synchronously (blocking) call.
    result = client.analyze(
        image_data=image,
        visual_features=[VisualFeatures.TAGS],
        language="en",  # Optional. See https://aka.ms/cv-languages for supported languages.
    )

    # Print Tags analysis results to the console
    print("Image analysis results:")
    print(" Tags:")
    if result.tags is not None:
        for tag in result.tags.list:
            print(f"   '{tag.name}', Confidence {tag.confidence:.4f}")

            if tag.name == "Vehicle registration plate":
                return 2
            if tag.name == "vehicle":
                return 1
        return 0


# REFERENCED FROM: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/vision/azure-ai-vision-imageanalysis/samples/sample_objects_image_file.py
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to detect physical objects in an image file sample.jpg, using a synchronous client.

    The synchronous (blocking) `analyze` method call returns an `ImageAnalysisResult` object.
    Its `objects` property (a `ObjectsResult` object) contains a list of `DetectedObject` objects. Each has:
    - The object name, for example: "chair", "laptop". 
    - A confidence score in the range [0, 1], with higher values indicating greater confidences in the detection.
    - A `BoundingBox` coordinates in pixels, for a rectangular surrounding the object in the image.

    Object names are only supported in English at the moment.
"""


def plate_extraction(image): # not in use because Azure's model isn't neccesarily great for Malaysian number plates
    # Create an Image Analysis client
    client = ImageAnalysisClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key)
    )

    # Detect objects in an image stream. This will be a synchronously (blocking) call.
    result = client.analyze(
        image_data=image,
        visual_features=[VisualFeatures.OBJECTS]
    )

    # Print Objects analysis results to the console
    print("Image analysis results:")
    print(" Objects:")
    if result.objects is not None:
        for object in result.objects.list:
            print(f"   '{object.tags[0].name}', {object.bounding_box}, Confidence: {object.tags[0].confidence:.4f}")

            if object.tags[0].name == "Vehicle registration plate":
                # REFERENCED FROM: https://github.com/nfmoore/automatic-number-plate-recognition-poc/blob/master/src/automatic-number-plate-recognition.ipynb
                
                # Extract the bounding box
                bounding_box = object.bounding_box

                # Define vertical distance from the left border
                x = bounding_box["x"]

                # Define horizontal distance from the top border
                y = bounding_box["y"]

                # Define rectangle width
                w = bounding_box["w"]

                # Define rectangle height
                h = bounding_box["h"]

                # Define top left point
                point_one = (x, y)

                # Define bottom right point
                point_two = (x + w, y + h)

                # Plot bounding box on image
                img_box = cv2.rectangle(image, point_one, point_two, color=(0, 255, 0), thickness=2)

                # Crop image
                img_crop = image[point_one[1] : point_two[1], point_one[0] : point_two[0]]

                # Resize image if width less than 500 pixels
                if img_crop.shape[1] < 500:
                    img_resize = imutils.resize(img_crop, width=500)

                # Display image
                # cv2.imshow("image", img_resize)
                # cv2.waitKey(0)

    print(f" Image height: {result.metadata.height}")
    print(f" Image width: {result.metadata.width}")
    print(f" Model version: {result.model_version}")

    # Convert the NumPy array to bytes
    _, img_crop_data = cv2.imencode('.jpg', img_resize)
    img_crop_bytes = img_crop_data.tobytes()

    return img_crop_bytes


# REFERENCED FROM: https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/vision/azure-ai-vision-imageanalysis/samples/sample_ocr_image_file.py
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
DESCRIPTION:
    This sample demonstrates how to extract printed or hand-written text for the image file sample.jpg
    using a synchronous client.

    The synchronous (blocking) `analyze` method call returns an `ImageAnalysisResult` object.
    Its `read` property (a `ReadResult` object) includes a list of `TextBlock` objects. Currently, the
    list will always contain one element only, as the service does not yet support grouping text lines
    into separate blocks. The `TextBlock` object contains a list of `DocumentLine` object. Each one includes: 
    - The text content of the line.
    - A `BoundingPolygon` coordinates in pixels, for a polygon surrounding the line of text in the image.
    - A list of `DocumentWord` objects.
    Each `DocumentWord` object contains:
    - The text content of the word.
    - A `BoundingPolygon` coordinates in pixels, for a polygon surrounding the word in the image.
    - A confidence score in the range [0, 1], with higher values indicating greater confidences in
      the recognition of the word.
"""


def plate_ocr(image):
    # Create an Image Analysis client
    client = ImageAnalysisClient(
        endpoint=endpoint,
        credential=AzureKeyCredential(key)
    )

    # # [START read]
    # # Load image to analyze into a 'bytes' object
    # with open(image, "rb") as f:
    #     image_data = f.read()

    # Extract text (OCR) from an image stream. This will be a synchronously (blocking) call.
    result = client.analyze(
        image_data=image,
        visual_features=[VisualFeatures.READ]
    )

    # Print text (OCR) analysis results to the console
    print("Image analysis results:")
    print(" Read:")
    if result.read is not None:
        for line in result.read.blocks[0].lines:
            print(f"   Line: '{line.text}', Bounding box {line.bounding_polygon}")
            for word in line.words:
                print(f"     Word: '{word.text}', Bounding polygon {word.bounding_polygon}, Confidence {word.confidence:.4f}")
    # [END read]
    print(f" Image height: {result.metadata.height}")
    print(f" Image width: {result.metadata.width}")
    print(f" Model version: {result.model_version}")

    return line.text


# if __name__ == "__main__":
#     print(vehicle_detection("C:/Users/K15H3N/OneDrive - Asia Pacific University/moodle3/FYP/FlyThru/src/vision/malaysian/9.jpg"))
#     plate_ocr(plate_extraction(image))