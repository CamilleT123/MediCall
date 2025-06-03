import cv2

def convert_with_opencv_fixed_rotation(input_path, output_path):
    """
    Converts a video from .mov to .mp4
    """
    cap = cv2.VideoCapture(input_path)

    # Check input
    if not cap.isOpened():
        print("Failed to open video.")
        return

    # Read first frame to get correct shape after rotation
    ret, frame = cap.read()
    if not ret:
        print("Failed to read video.")
        return

    # Rotate frame 90 degrees clockwise
    rotated_frame = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
    height, width, _ = rotated_frame.shape
    fps = cap.get(cv2.CAP_PROP_FPS)

    # Define writer
    out = cv2.VideoWriter(output_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
    out.write(rotated_frame)

    # Continue processing
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        rotated = cv2.rotate(frame, cv2.ROTATE_90_CLOCKWISE)
        out.write(rotated)

    cap.release()
    out.release()
    print("Conversion completed with fixed orientation.")

def load_and_preprocess_video(path, rotate_code=None, max_frames=None):
    """
    Loads a video and returns a list of frames.
    
    Parameters:
        path (str): path to the video file.
        rotate_code (cv2 constant): cv2.ROTATE_90_CLOCKWISE, etc. Default is None.
        max_frames (int): Optional limit on number of frames to load.

    Returns:
        frames (List[np.ndarray]): list of BGR frames.
    """
    cap = cv2.VideoCapture(path)
    frames = []
    count = 0

    if not cap.isOpened():
        raise FileNotFoundError(f"Could not open video: {path}")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if rotate_code is not None:
            frame = cv2.rotate(frame, rotate_code)

        frames.append(frame)
        count += 1

        if max_frames and count >= max_frames:
            break

    cap.release()
    return frames

def get_video_properties(path):
    """
    Returns width, height, fps, and total frame count.
    """
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise FileNotFoundError(f"Could not open video: {path}")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.release()
    return width, height, fps, frame_count
