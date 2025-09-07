import cv2
import csv
from tracking_calculations import Calculator

# Open the video file
capture = cv2.VideoCapture('il8_1kpa_xy1.mp4')

# Check if the video file is opened successfully
if not capture.isOpened():
    print("Error opening video")
    exit()

# Read the first frame of the video
ret, old_frame = capture.read()

# Check if able to read the first frame
if not ret:
    print("Error reading the first frame")
    exit()

# Resize the first frame
new_width = int(old_frame.shape[1] * 0.4)
new_height = int(old_frame.shape[0] * 0.4)
initial_frame = cv2.resize(old_frame, (new_width, new_height))

# Select multiple ROIs
bboxes = []
i = 0
while True:
    i += 1
    bbox = cv2.selectROI('Select ROIs, press ENTER to finish', initial_frame, fromCenter=False, showCrosshair=True)
    if bbox[2] != 0 and bbox[3] != 0:  # Check if the ROI is valid, if roi not selected, moves on
        bboxes.append(bbox)
    else:
        break
    cv2.putText(initial_frame, f"Cells Tracked {i}", (10, 10 + i * 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                (255, 0, 0), 1)
cv2.destroyWindow('Select ROIs, press ENTER to finish')

# Initialize trackers for each ROI
trackers = []
for bbox in bboxes:
    tracker = cv2.TrackerKCF_create()
    tracker.init(initial_frame, bbox)
    trackers.append(tracker)

# Open a file to log the locations of each ROI
with open('tracked_locations.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    header = ['Frame']
    for i in range(len(bboxes)):
        header.extend([f'ROI_{i+1}_x', f'ROI_{i+1}_y', f'ROI_{i+1}_w', f'ROI_{i+1}_h'])
    writer.writerow(header)

    frame_count = 0
    while capture.isOpened():
        ret, frame = capture.read()
        if not ret:
            break

        # Resize the frame
        frame = cv2.resize(frame, (new_width, new_height))

        row = [frame_count]
        for i, tracker in enumerate(trackers):
            success, bbox = tracker.update(frame)
            if success:
                # Draw the bounding box
                top_left_corner = (int(bbox[0]), int(bbox[1]))
                bottom_right_corner = (int(bbox[0] + bbox[2]), int(bbox[1] + bbox[3]))
                cv2.rectangle(frame, top_left_corner, bottom_right_corner, (255, 0, 0), 2, 1)
                row.extend([bbox[0], bbox[1], bbox[2], bbox[3]])
                text_x, text_y = top_left_corner
                cv2.putText(frame, f"ROI {i+1}", (text_x, text_y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (255, 0, 0), 1)
            else:
                row.extend([None, None, None, None])
                cv2.putText(frame, f"Tracking failure for ROI {i+1}", (10, 30 + i*20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        writer.writerow(row)
        frame_count += 1

        # Display the frame
        cv2.putText(frame, "AI_Tracker", (0, 20), cv2.FONT_HERSHEY_DUPLEX, 0.75, (50, 255, 50), 1)
        cv2.imshow('Tracking', frame)

        # Press 'q' to exit
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

# Release the capture
capture.release()
cv2.destroyAllWindows()

stats = Calculator("tracked_locations.csv", "final_stats.csv")
stats.process_ROIs()
