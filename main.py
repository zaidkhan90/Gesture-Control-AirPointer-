import cv2
import mediapipe as mp
import pyautogui
import numpy as np

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

# Get screen size
screen_width, screen_height = pyautogui.size()

# Open webcam
cap = cv2.VideoCapture(0)

clicked = False  # Track click state
scrolling = False  # Track scrolling state
prev_y = None  # Store previous Y position for scrolling

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("❌ Camera feed not available!")
        break

    # Flip the frame horizontally
    frame = cv2.flip(frame, 1)
    h, w, c = frame.shape

    # Convert frame to RGB for MediaPipe
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            # Get landmarks for index finger tip and thumb tip
            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]
            thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]

            # Convert hand landmark position to screen coordinates
            cursor_x = int(index_finger_tip.x * screen_width)
            cursor_y = int(index_finger_tip.y * screen_height)

            # Move the mouse pointer
            pyautogui.moveTo(cursor_x, cursor_y, duration=0.1)

            # Get thumb and index finger positions
            index_x, index_y = int(index_finger_tip.x * w), int(index_finger_tip.y * h)
            thumb_x, thumb_y = int(thumb_tip.x * w), int(thumb_tip.y * h)

            # Draw landmarks
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Calculate distance between index finger tip and thumb tip
            distance = np.hypot(index_x - thumb_x, index_y - thumb_y)

            # Click when fingers are close
            if distance < 30:
                if not clicked:
                    pyautogui.click()
                    clicked = True
                    cv2.putText(frame, "Click!", (index_x, index_y - 20), 
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            else:
                clicked = False

            # **🖱️ Scroll Detection (Move Hand Up/Down)**
            if prev_y is not None:
                y_movement = index_y - prev_y  # Get difference in Y position
                
                if abs(y_movement) > 20:  # Threshold to prevent unwanted scroll
                    if y_movement > 0:  
                        pyautogui.scroll(-3)  # Scroll Down
                        cv2.putText(frame, "Scroll Down", (index_x, index_y - 50), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    else:
                        pyautogui.scroll(3)  # Scroll Up
                        cv2.putText(frame, "Scroll Up", (index_x, index_y - 50), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    
                    scrolling = True  # Set scrolling state
                else:
                    scrolling = False  # Reset scrolling state

            prev_y = index_y  # Store the current Y position for next frame

    # Show webcam feed
    cv2.imshow("AirPointer - Gesture Control", frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
