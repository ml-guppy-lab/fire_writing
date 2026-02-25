import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
from collections import deque
import random
import math
import os
import urllib.request

class HeartEffect:
    """Animated heart effect with neon glow"""
    def __init__(self, hand_type='left'):
        self.active = False
        self.position = None
        self.size = 100
        self.dots = []
        self.hand_type = hand_type  # 'left' or 'right'
        
    def activate(self, center_x, center_y, size):
        """Activate the heart effect"""
        if not self.active:
            # Only create dots on first activation
            self.dots = []
            # Create dots on the perimeter of the heart
            for t in np.linspace(0, 2 * math.pi, 40):
                # Heart shape parametric equation
                x_offset = size * (16 * math.sin(t)**3) / 16
                y_offset = -size * (13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)) / 16
                
                # Position on heart perimeter
                x = center_x + x_offset
                y = center_y + y_offset
                
                # Calculate outward direction (normal to heart)
                angle = math.atan2(y_offset, x_offset)
                
                color_choice = random.choice(['white', 'purple'])
                self.dots.append({
                    'x': x, 
                    'y': y, 
                    'color': color_choice,
                    'size': random.randint(2, 5),
                    'vx': math.cos(angle) * random.uniform(0.5, 1.5),  # Move outward
                    'vy': math.sin(angle) * random.uniform(0.5, 1.5),
                    'angle_on_heart': t,
                    'distance_from_heart': 0,
                    'max_distance': random.uniform(30, 60)
                })
        
        self.active = True
        self.position = (center_x, center_y)
        self.size = size
    
    def deactivate(self):
        """Deactivate the heart effect"""
        self.active = False
        self.dots = []
    
    def update(self):
        """Update heart effect"""
        if self.active and self.position:
            cx, cy = self.position
            # Update dots - make them move outward from the heart perimeter
            for dot in self.dots:
                # Calculate position on heart perimeter based on current heart size
                t = dot['angle_on_heart']
                x_offset = self.size * (16 * math.sin(t)**3) / 16
                y_offset = -self.size * (13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)) / 16
                
                # Base position on heart perimeter
                base_x = cx + x_offset
                base_y = cy + y_offset
                
                # Move dot outward
                dot['distance_from_heart'] += 1
                
                # Calculate outward direction
                angle = math.atan2(y_offset, x_offset)
                
                # Position at distance from perimeter
                dot['x'] = base_x + math.cos(angle) * dot['distance_from_heart']
                dot['y'] = base_y + math.sin(angle) * dot['distance_from_heart']
                
                # Reset if too far
                if dot['distance_from_heart'] > dot['max_distance']:
                    dot['distance_from_heart'] = 0
    
    def draw(self, frame):
        """Draw heart with neon glow effect"""
        if not self.active or self.position is None:
            return
        
        cx, cy = self.position
        size = self.size
        
        # Create heart shape points
        heart_points = []
        for t in np.linspace(0, 2 * math.pi, 100):
            x = size * (16 * math.sin(t)**3)
            y = -size * (13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t))
            heart_points.append((int(cx + x/16), int(cy + y/16)))
        
        heart_points = np.array(heart_points, dtype=np.int32)
        
        # Draw multiple layers for neon glow
        overlay = frame.copy()
        
        # Outer glow
        cv2.polylines(overlay, [heart_points], True, (255, 100, 255), 15, cv2.LINE_AA)
        cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)
        
        # Middle glow
        cv2.polylines(frame, [heart_points], True, (255, 50, 255), 8, cv2.LINE_AA)
        
        # Core bright line
        cv2.polylines(frame, [heart_points], True, (255, 150, 255), 3, cv2.LINE_AA)
        
        # Draw animated dots coming out from perimeter
        for dot in self.dots:
            # Fade out as dots move away
            alpha = 1.0 - (dot['distance_from_heart'] / dot['max_distance'])
            
            if alpha > 0:
                if dot['color'] == 'purple':
                    color = (255, 0, 180)  # Purple/magenta
                else:
                    color = (255, 255, 255)  # White
                
                # Draw dot with size based on alpha
                dot_size = max(1, int(dot['size'] * alpha))
                cv2.circle(frame, (int(dot['x']), int(dot['y'])), 
                          dot_size, color, -1, cv2.LINE_AA)
                # Glow around dots
                glow_size = dot_size + 2
                cv2.circle(frame, (int(dot['x']), int(dot['y'])), 
                          glow_size, color, 1, cv2.LINE_AA)


class FireParticle:
    """Particle system for creating realistic fire effects"""
    def __init__(self, x, y, color_type='red'):
        self.x = x
        self.y = y
        self.vx = random.uniform(-2, 2)
        self.vy = random.uniform(-8, -3)  # Upward motion
        self.life = random.randint(15, 30)
        self.max_life = self.life
        self.size = random.randint(15, 35)  # Larger particles
        self.color_type = color_type
        
    def update(self):
        """Update particle position and life"""
        self.x += self.vx
        self.y += self.vy
        self.life -= 1
        # Add some randomness to movement
        self.vx += random.uniform(-0.5, 0.5)
        self.vy -= 0.3  # Gravity effect upward
        
    def is_alive(self):
        """Check if particle is still alive"""
        return self.life > 0
    
    def get_color(self):
        """Get particle color based on life and type"""
        life_ratio = self.life / self.max_life
        
        if self.color_type == 'red':
            # Red fire: bright yellow core to intense red to dark red
            if life_ratio > 0.7:
                return (0, 100, 255)  # Yellow-orange
            elif life_ratio > 0.4:
                return (0, 0, 255)    # Pure bright red
            else:
                return (0, 0, 180)    # Deep red
        else:  # white fire
            # White fire: bright white to blue-white to transparent
            if life_ratio > 0.7:
                return (255, 255, 255)  # Bright white
            elif life_ratio > 0.4:
                return (255, 220, 180)  # Warm white
            else:
                return (200, 200, 255)  # Cool white-blue
    
    def get_alpha(self):
        """Get transparency based on life"""
        return int((self.life / self.max_life) * 255)


class NeonTrail:
    """Neon fire trail for finger writing"""
    def __init__(self, max_length=50):
        self.points = deque(maxlen=max_length)
        self.max_length = max_length
    
    def add_point(self, point):
        """Add a point to the trail with smoothing"""
        if point is not None:
            # Smooth point by averaging with previous point (lighter smoothing)
            if len(self.points) > 0 and self.points[-1] is not None:
                prev_point = self.points[-1]
                # Lighter smoothing: 0.85 new, 0.15 old
                smoothed_x = int(0.85 * point[0] + 0.15 * prev_point[0])
                smoothed_y = int(0.85 * point[1] + 0.15 * prev_point[1])
                self.points.append((smoothed_x, smoothed_y))
            else:
                self.points.append(point)
        else:
            # Add None to break trail continuity
            if len(self.points) > 0 and self.points[-1] is not None:
                self.points.append(None)
    
    def draw(self, frame):
        """Draw neon pink fire trail with glow effect"""
        if len(self.points) < 2:
            return
        
        # Create overlay for transparency
        overlay = frame.copy()
        
        # Draw multiple layers for glow effect
        for i in range(len(self.points) - 1):
            if self.points[i] is None or self.points[i + 1] is None:
                continue
            
            # Calculate alpha based on position in trail
            alpha = (i + 1) / len(self.points)
            
            # Bright pink neon color
            base_color = (180, 20, 255)  # Hot pink
            
            # Draw outer glow (larger, more transparent)
            thickness = max(1, int(20 * alpha))
            cv2.line(overlay, self.points[i], self.points[i + 1], 
                    (255, 50, 255), thickness, cv2.LINE_AA)  # Bright pink
            
            # Draw middle glow
            thickness = max(1, int(12 * alpha))
            cv2.line(overlay, self.points[i], self.points[i + 1], 
                    (255, 20, 255), thickness, cv2.LINE_AA)  # Hot pink
            
            # Draw core (bright)
            thickness = max(1, int(6 * alpha))
            cv2.line(overlay, self.points[i], self.points[i + 1], 
                    (255, 100, 255), thickness, cv2.LINE_AA)  # Magenta-pink
        
        # Blend overlay with original frame
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
        
        # Add bright core on top
        for i in range(len(self.points) - 1):
            if self.points[i] is None or self.points[i + 1] is None:
                continue
            alpha = (i + 1) / len(self.points)
            thickness = max(1, int(3 * alpha))
            cv2.line(frame, self.points[i], self.points[i + 1], 
                    (255, 150, 255), thickness, cv2.LINE_AA)  # Bright pink core


class FireWritingApp:
    """Main application for fire writing with hand tracking"""
    def __init__(self):
        # Download hand landmark model if not present
        model_path = 'hand_landmarker.task'
        if not os.path.exists(model_path):
            print("Downloading hand landmark model...")
            url = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
            urllib.request.urlretrieve(url, model_path)
            print("Model downloaded successfully!")
        
        # Configure MediaPipe HandLandmarker (new API for v0.10+)
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.HandLandmarkerOptions(
            base_options=base_options,
            num_hands=2,  # Detect up to 2 hands
            min_hand_detection_confidence=0.7,
            min_hand_presence_confidence=0.7,
            min_tracking_confidence=0.7,
            running_mode=vision.RunningMode.VIDEO
        )
        
        # Create hand detector
        self.detector = vision.HandLandmarker.create_from_options(options)
        
        # Particle systems for each palm
        self.particles = []
        
        # Heart effects for each hand
        self.left_heart = HeartEffect(hand_type='left')
        self.right_heart = HeartEffect(hand_type='right')
        
        # Store hand positions for heart detection
        self.left_hand_data = None
        self.right_hand_data = None
        
        # Track if heart gesture is active
        self.heart_gesture_active = False
        
        # Video capture
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        
        # Frame counter for video mode
        self.frame_count = 0
        
    def get_hand_landmarks(self, hand_landmarks, frame_shape):
        """Extract key landmarks from hand"""
        h, w, _ = frame_shape
        
        # Get palm center (approximately wrist + middle finger base)
        wrist = hand_landmarks[0]
        middle_mcp = hand_landmarks[9]
        palm_x = int((wrist.x + middle_mcp.x) / 2 * w)
        palm_y = int((wrist.y + middle_mcp.y) / 2 * h)
        
        # Get index finger tip
        index_tip = hand_landmarks[8]
        finger_x = int(index_tip.x * w)
        finger_y = int(index_tip.y * h)
        
        # Get thumb tip
        thumb_tip = hand_landmarks[4]
        thumb_x = int(thumb_tip.x * w)
        thumb_y = int(thumb_tip.y * h)
        
        # Calculate hand size (distance from wrist to middle finger tip for depth estimation)
        middle_tip = hand_landmarks[12]
        hand_size = math.sqrt(
            (middle_tip.x - wrist.x)**2 * w**2 + 
            (middle_tip.y - wrist.y)**2 * h**2
        )
        
        return (palm_x, palm_y), (finger_x, finger_y), (thumb_x, thumb_y), hand_size
    
    def calculate_heart_size(self, hand_size, base_size=80):
        """Calculate heart size based on hand size (proxy for distance from camera)"""
        # Larger hand = closer to camera = bigger heart
        # Normalize based on typical hand size range (50-200 pixels)
        scale_factor = hand_size / 120.0  # 120 is average hand size
        return int(base_size * scale_factor)
    
    def is_pinching(self, thumb_pos, index_pos, threshold=40):
        """Check if thumb and index finger are pinching (close together)"""
        distance = math.sqrt((thumb_pos[0] - index_pos[0])**2 + (thumb_pos[1] - index_pos[1])**2)
        return distance < threshold
    
    def detect_heart_gesture(self):
        """Detect if both hands are forming a heart shape"""
        if self.left_hand_data is None or self.right_hand_data is None:
            return False
        
        left_thumb = self.left_hand_data['thumb']
        left_index = self.left_hand_data['index']
        right_thumb = self.right_hand_data['thumb']
        right_index = self.right_hand_data['index']
        
        # Calculate distances
        # Thumbs should be close together
        thumb_distance = math.sqrt((left_thumb[0] - right_thumb[0])**2 + 
                                   (left_thumb[1] - right_thumb[1])**2)
        
        # Index fingers should be close together
        index_distance = math.sqrt((left_index[0] - right_index[0])**2 + 
                                   (left_index[1] - right_index[1])**2)
        
        # Hands should be at reasonable distance apart
        hand_distance = math.sqrt((self.left_hand_data['palm'][0] - self.right_hand_data['palm'][0])**2 + 
                                  (self.left_hand_data['palm'][1] - self.right_hand_data['palm'][1])**2)
        
        # Heart detected if thumbs are close, index fingers are close, and hands are apart
        if thumb_distance < 60 and index_distance < 60 and 100 < hand_distance < 300:
            return True
        
        return False
    
    def draw_hand_landmarks(self, frame, hand_landmarks):
        """Draw hand landmarks on frame with anti-aliasing"""
        h, w, _ = frame.shape
        
        # Draw landmarks
        for landmark in hand_landmarks:
            x = int(landmark.x * w)
            y = int(landmark.y * h)
            cv2.circle(frame, (x, y), 3, (0, 255, 0), -1, cv2.LINE_AA)
        
        # Draw connections
        connections = [
            (0, 1), (1, 2), (2, 3), (3, 4),  # Thumb
            (0, 5), (5, 6), (6, 7), (7, 8),  # Index
            (0, 9), (9, 10), (10, 11), (11, 12),  # Middle
            (0, 13), (13, 14), (14, 15), (15, 16),  # Ring
            (0, 17), (17, 18), (18, 19), (19, 20),  # Pinky
            (5, 9), (9, 13), (13, 17)  # Palm
        ]
        
        for connection in connections:
            start_idx, end_idx = connection
            start = hand_landmarks[start_idx]
            end = hand_landmarks[end_idx]
            start_point = (int(start.x * w), int(start.y * h))
            end_point = (int(end.x * w), int(end.y * h))
            cv2.line(frame, start_point, end_point, (0, 200, 0), 1, cv2.LINE_AA)
    
    def create_fire_particles(self, position, color_type, num_particles=8):
        """Create new fire particles at position"""
        for _ in range(num_particles):
            self.particles.append(FireParticle(position[0], position[1], color_type))
    
    def update_particles(self):
        """Update all particles"""
        self.particles = [p for p in self.particles if p.is_alive()]
        for particle in self.particles:
            particle.update()
    
    def draw_particles(self, frame):
        """Draw all fire particles with blur effect and anti-aliasing"""
        # Create overlay for particles
        overlay = np.zeros_like(frame, dtype=np.uint8)
        
        for particle in self.particles:
            color = particle.get_color()
            alpha = particle.get_alpha()
            size = int(particle.size * (particle.life / particle.max_life))
            
            if size > 0:
                px, py = int(particle.x), int(particle.y)
                
                # Draw main particle with color
                cv2.circle(overlay, (px, py), size, color, -1, cv2.LINE_AA)
                
                # Add subtle yellow outline (thinner, only for red fire)
                if particle.color_type == 'red':
                    yellow_outline = (0, 180, 255)  # Bright yellow
                    cv2.circle(overlay, (px, py), size, yellow_outline, max(1, size//6), cv2.LINE_AA)
                    
                    # Add bright yellow core for red fire
                    if size > 3:
                        core_size = max(1, size // 3)
                        cv2.circle(overlay, (px, py), core_size, (0, 255, 255), -1, cv2.LINE_AA)
        
        # Apply Gaussian blur for glow effect
        overlay = cv2.GaussianBlur(overlay, (15, 15), 0)
        
        # Blend with frame
        mask = overlay.astype(float) / 255.0
        frame_float = frame.astype(float)
        overlay_float = overlay.astype(float)
        
        blended = frame_float * (1 - mask) + overlay_float * mask
        frame[:] = blended.astype(np.uint8)
        
        # Draw black texture lines on top for depth (after blur) - fewer lines
        for particle in self.particles:
            size = int(particle.size * (particle.life / particle.max_life))
            if size > 8:  # Only on larger particles
                px, py = int(particle.x), int(particle.y)
                
                # Draw only 1-2 black lines for subtle texture
                num_lines = random.randint(1, 2)
                for _ in range(num_lines):
                    offset_x = random.randint(-size//3, size//3)
                    offset_y = random.randint(-size//3, size//3)
                    end_x = px + random.randint(-size//4, size//4)
                    end_y = py + random.randint(-size//4, size//4)
                    
                    # Draw thin black lines for texture
                    cv2.line(frame, (px + offset_x, py + offset_y), 
                            (end_x, end_y), (0, 0, 0), 1, cv2.LINE_AA)
    
    def run(self):
        """Main application loop"""
        print("Fire Writing Application Started!")
        print("- Red fire on LEFT hand palm")
        print("- White fire on RIGHT hand palm")
        print("- Make a HEART shape with both hands:")
        print("  * Two hearts appear near each palm")
        print("  * Fire disappears during heart gesture")
        print("  * Hearts scale with palm distance from camera")
        print("  * Hearts follow palms when separated")
        print("- Press 'c' to clear hearts and resume fire")
        print("- Press 'q' to quit")
        print()
        
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            
            # Flip frame horizontally for mirror view
            frame = cv2.flip(frame, 1)
            h, w, _ = frame.shape
            
            # Convert to RGB for MediaPipe
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Create mp.Image for the new API
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
            
            # Process frame with timestamp
            self.frame_count += 1
            timestamp_ms = int(self.frame_count * 33.33)  # Approximate 30fps
            
            # Detect hands
            detection_result = self.detector.detect_for_video(mp_image, timestamp_ms)
            
            # Track which hands were detected
            left_detected = False
            right_detected = False
            
            # Reset hand data
            self.left_hand_data = None
            self.right_hand_data = None
            
            # First pass: collect hand data for heart detection
            if detection_result.hand_landmarks and detection_result.handedness:
                for hand_landmarks, handedness in zip(detection_result.hand_landmarks, 
                                                     detection_result.handedness):
                    # Determine if left or right hand
                    hand_label = handedness[0].category_name
                    
                    # Get landmarks (now includes thumb position and hand size)
                    palm_pos, finger_pos, thumb_pos, hand_size = self.get_hand_landmarks(hand_landmarks, frame.shape)
                    
                    # Store hand data for heart detection
                    hand_data = {
                        'palm': palm_pos,
                        'index': finger_pos,
                        'thumb': thumb_pos,
                        'hand_size': hand_size
                    }
                    
                    if hand_label == 'Left':
                        left_detected = True
                        self.left_hand_data = hand_data
                    else:
                        right_detected = True
                        self.right_hand_data = hand_data
            
            # Check for heart gesture BEFORE creating fire
            is_heart = self.detect_heart_gesture()
            
            if is_heart:
                # Heart gesture detected - activate hearts if not already active
                if not self.heart_gesture_active:
                    print("Heart detected! ❤️ - Fire stopped")
                    self.heart_gesture_active = True
                    # Activate both hearts
                    if self.left_hand_data:
                        left_size = self.calculate_heart_size(self.left_hand_data['hand_size'])
                        self.left_heart.activate(
                            self.left_hand_data['palm'][0], 
                            self.left_hand_data['palm'][1], 
                            left_size
                        )
                    
                    if self.right_hand_data:
                        right_size = self.calculate_heart_size(self.right_hand_data['hand_size'])
                        self.right_heart.activate(
                            self.right_hand_data['palm'][0], 
                            self.right_hand_data['palm'][1], 
                            right_size
                        )
            
            # If hearts are active, continuously update their positions based on palm locations
            if self.heart_gesture_active:
                if self.left_hand_data and self.left_heart.active:
                    left_size = self.calculate_heart_size(self.left_hand_data['hand_size'])
                    self.left_heart.activate(
                        self.left_hand_data['palm'][0], 
                        self.left_hand_data['palm'][1], 
                        left_size
                    )
                
                if self.right_hand_data and self.right_heart.active:
                    right_size = self.calculate_heart_size(self.right_hand_data['hand_size'])
                    self.right_heart.activate(
                        self.right_hand_data['palm'][0], 
                        self.right_hand_data['palm'][1], 
                        right_size
                    )
            
            # Once hearts are active, keep them active (don't resume fire when hands open)
            # Fire will only resume when 'c' is pressed to clear
            
            # Second pass: process hand actions (fire, writing) based on heart gesture state
            if detection_result.hand_landmarks and detection_result.handedness:
                for hand_landmarks, handedness in zip(detection_result.hand_landmarks, 
                                                     detection_result.handedness):
                    # Determine if left or right hand
                    hand_label = handedness[0].category_name
                    
                    # Get landmarks again
                    palm_pos, finger_pos, thumb_pos, hand_size = self.get_hand_landmarks(hand_landmarks, frame.shape)
                    
                    if hand_label == 'Left':
                        # Only show fire if not in heart gesture mode
                        if not self.heart_gesture_active:
                            # Red fire for left hand
                            self.create_fire_particles(palm_pos, 'red', num_particles=3)
                    else:
                        # Only show fire if not in heart gesture mode
                        if not self.heart_gesture_active:
                            # White fire for right hand
                            self.create_fire_particles(palm_pos, 'white', num_particles=3)
            
            # Update and draw particles
            self.update_particles()
            self.draw_particles(frame)
            
            # Update and draw heart effects for both hands
            self.left_heart.update()
            self.right_heart.update()
            self.left_heart.draw(frame)
            self.right_heart.draw(frame)
            
            # Display instructions with anti-aliasing
            cv2.putText(frame, "HEART gesture: special effect | 'c': clear | 'q': quit", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2, cv2.LINE_AA)
            
            # Show frame
            cv2.imshow('Fire Writing', frame)
            
            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('c'):
                # Clear heart effects and resume fire
                self.left_heart.deactivate()
                self.right_heart.deactivate()
                self.heart_gesture_active = False
                print("Hearts cleared! Fire resumed.")
        
        # Cleanup
        self.cap.release()
        cv2.destroyAllWindows()
        self.detector.close()


if __name__ == "__main__":
    app = FireWritingApp()
    app.run()
