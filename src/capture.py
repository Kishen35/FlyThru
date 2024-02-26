# UNUSED: FOR DEMONSTRATION PURPOSES ONLY

import cv2
import config
import vision

def video_feed():
    VehicleVideo = cv2.VideoCapture(config.vision['camera'])
    plate_number = None

    # Create a named window
    cv2.namedWindow('Vehicle Detection', cv2.WINDOW_NORMAL)  # WINDOW_NORMAL allows resizing

    while VehicleVideo.isOpened():
        ret, frame = VehicleVideo.read()
        controlkey = cv2.waitKey(1500) # 1.5s delay
        if ret:
            cv2.resizeWindow('Vehicle Detection', 600, 400)
            cv2.imshow('Vehicle Detection', frame)  # Use the named window
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Convert the NumPy array to bytes
            _, img_crop_data = cv2.imencode('.jpg', frame)
            img_crop_bytes = img_crop_data.tobytes()

            if vision.vehicle_detection(img_crop_bytes) == 1:
            # elif vision.vehicle_detection(img_crop_bytes) == 2 and plate_number == None: # object detection for plate not so accurate
                if plate_number == None:
                    try:
                        # plate_number = vision.plate_ocr(vision.plate_extraction(img_crop_bytes))
                        plate_number = vision.plate_ocr(img_crop_bytes)
                        print(plate_number)
                    except UnboundLocalError:
                        plate_number = None
        else:
            break
        if controlkey == ord('q'):
            break

    VehicleVideo.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    video_feed()

# plate_number = None
# def video_feed():
#     VehicleVideo = cv2.VideoCapture(config.vision['camera'])
    
#     global plate_number

#     # Create a named window
#     cv2.namedWindow('Vehicle Detection', cv2.WINDOW_NORMAL)  # WINDOW_NORMAL allows resizing

#     while VehicleVideo.isOpened():
#         ret, frame = VehicleVideo.read()
#         controlkey = cv2.waitKey(1500) # 1.5s delay
#         if ret:
#             cv2.resizeWindow('Vehicle Detection', 600, 400)
#             cv2.imshow('Vehicle Detection', frame)  # Use the named window
#             frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

#             # Convert the NumPy array to bytes
#             _, img_crop_data = cv2.imencode('.jpg', frame)
#             img_crop_bytes = img_crop_data.tobytes()

#             if vision.vehicle_detection(img_crop_bytes) == 1: # vehicle detected
#                 if session['order_id'] == None:
#                     return redirect(url_for('initiate_order'))
#                 else:
#                 # elif vision.vehicle_detection(img_crop_bytes) == 2 and plate_number == None: 
#                 # UNUSED: object detection for plate not so accurate
#                     if plate_number == None:
#                         try:
#                             # plate_number = vision.plate_ocr(vision.plate_extraction(img_crop_bytes))
#                             plate_number = vision.plate_ocr(img_crop_bytes)
#                             order.update_plateNumber(session['clientEmail'], session['order_id'], plate_number)
#                         except UnboundLocalError:
#                             plate_number = "unavailable"
            
#                         break

#                     else:
#                         openAIspeech.chat_with_open_ai()

#             elif session['order_id'] != None:
#                     plate_number =  None
#                     return redirect(url_for('end_order'))

#         else:
#             break
#         # if controlkey == ord('q'):
#         #     break

#     VehicleVideo.release()
#     cv2.destroyAllWindows()

# if __name__ == '__main__':
#     video_frame()

# # Example usage:
# captured_frame = capture_frame()

# if captured_frame is not None:
#     # Display the captured frame (optional)
#     cv2.imshow("Captured Frame", captured_frame)
#     cv2.waitKey(0)
#     cv2.destroyAllWindows()