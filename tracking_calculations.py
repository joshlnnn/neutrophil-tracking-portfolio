import csv
import math


class Calculator:
    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file
        self.roi_positions = {}
        self.accumulated_distances = {}
        self.initial_positions = {}
        self.last_valid_position = {}
        self.euclidean_distances = {}
        self.pixels_to_um = 6.25

    # Find the distance between coordinates using pythagorean theorem
    @staticmethod
    def find_distance(x1, y1, x2, y2):
        return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def find_mean(self):
        total_accumulated_distance = 0
        print(self.accumulated_distances)
        for i in range(len(self.accumulated_distances)):
            id_number = f'ROI_{i + 1}'
            total_accumulated_distance += float(self.accumulated_distances[id_number])
        mean_accumulated_distance = total_accumulated_distance / len(self.accumulated_distances)
        total_euclidean_distances = 0
        for i in range(len(self.euclidean_distances)):
            id_number = f'ROI_{i + 1}'
            total_euclidean_distances += float(self.euclidean_distances[id_number])
        mean_euclidean_distance = total_euclidean_distances / len(self.euclidean_distances)
        return mean_accumulated_distance, mean_euclidean_distance

    # Take in a file with all the coordinates and spit out a file with calculated distances (accumulated and euclidian)
    def process_ROIs(self):
        with open(self.input_file, mode='r') as file:
            reader = csv.reader(file)
            header = next(reader)  # Skip the header

            for row in reader:
                frame_number = int(row[0])
                num_rois = (len(row) - 1) // 4  # Calculate number of ROIs from the header

                for i in range(num_rois):
                    roi_id = f'ROI_{i + 1}'
                    index_base = i * 4 + 1

                    # Extract coordinates and handle invalid entries
                    # value.strip() --> returns False if empty after returned, returns true if there is a value
                    # if after the statement is shorthand, the program before will not run unless if is True
                    # try:
                    #     x = int(row[index_base].strip()) if row[index_base].strip() else None
                    #     y = int(row[index_base + 1].strip()) if row[index_base + 1].strip() else None
                    #     w = int(row[index_base + 2].strip()) if row[index_base + 2].strip() else None
                    #     h = int(row[index_base + 3].strip()) if row[index_base + 3].strip() else None
                    # except ValueError:
                    #     x, y, w, h = None, None, None, None

                    x = int(row[index_base].strip()) if row[index_base].strip() else None
                    y = int(row[index_base + 1].strip()) if row[index_base + 1].strip() else None
                    w = int(row[index_base + 2].strip()) if row[index_base + 2].strip() else None
                    h = int(row[index_base + 3].strip()) if row[index_base + 3].strip() else None

                    # Use previous valid position if current position is invalid
                    if x is None or y is None or w is None or h is None:
                        if roi_id in self.last_valid_position:
                            x, y, w, h = self.last_valid_position[roi_id]
                        else:
                            continue  # Skip if no valid previous position is available

                    # Update last valid position for the ROI
                    self.last_valid_position[roi_id] = (x, y, w, h)

                    # Update ROI positions

                    # New ROI
                    if roi_id not in self.roi_positions:  # check if roi_id is in roi_positions dictionary
                        self.roi_positions[roi_id] = []  # initialize empty list for roi_id in roi_positions dictionary
                        self.accumulated_distances[roi_id] = 0.0  # initialize ROI's accumulated distance
                        self.initial_positions[roi_id] = (x, y, w, h)  # initialize ROI's starting point

                    # Add to accumulated distance if it has a coordinate already
                    if len(self.roi_positions[roi_id]) > 0:
                        # Calculate the distance from the last position
                        last_x, last_y, _, _ = self.roi_positions[roi_id][-1]
                        dist = self.find_distance(last_x, last_y, x, y)
                        self.accumulated_distances[roi_id] += dist

                    self.roi_positions[roi_id].append((x, y, w, h))

        # Calculate Euclidean distances from the initial position to the last position
        for roi_id, positions in self.roi_positions.items():
            initial_x, initial_y, _, _ = self.initial_positions[roi_id]
            final_x, final_y, _, _ = positions[-1]
            self.euclidean_distances[roi_id] = self.find_distance(initial_x, initial_y, final_x, final_y)

        # Write results to the output CSV file
        with open(self.output_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['ROI', 'Accumulated Distance', 'Euclidean Distance'])

            for roi_id in self.roi_positions.keys():
                file.write(str(roi_id) + ": " + str(self.accumulated_distances[roi_id]*self.pixels_to_um) +
                           " micrometers, " + str(self.euclidean_distances[roi_id]*self.pixels_to_um) + " micrometers\n")
            mean_accumulated, mean_euclidian = self.find_mean()
            file.write("Mean Accumulated Distance: " + str(mean_accumulated*self.pixels_to_um) + " micrometers" + '\n')
            file.write("Mean Euclidian Distance: " + str(mean_euclidian*self.pixels_to_um) + " micrometers")

        print(f"Results have been written to {self.output_file}")
