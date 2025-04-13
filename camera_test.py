import cv2

cap = cv2.VideoCapture(0)  # Try 1 instead of 0 if it doesn't work

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("❌ Error: Camera not working!")
        break

    cv2.imshow("Camera Test", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
