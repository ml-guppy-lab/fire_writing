# 🔥 Fire Writing - Interactive Hand Tracking with Fire Effects

An interactive computer vision project that brings **magical fire effects** to your hands using real-time hand tracking! Create stunning visual effects with fire animations on your palms and conjure beautiful hearts with just a gesture.

![Python](https://img.shields.io/badge/Python-3.12-blue.svg)
![OpenCV](https://img.shields.io/badge/OpenCV-4.8.1-green.svg)
![MediaPipe](https://img.shields.io/badge/MediaPipe-0.10.32-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Features

### 🔥 Dual Fire Effects
- **Red Fire** on your LEFT palm - Realistic fire with yellow cores and dynamic particle physics
- **White Fire** on your RIGHT palm - Bright, mystical white flames
- Fire particles with gravity simulation, upward motion, and life cycles
- Enhanced visual effects with yellow outlines and subtle texture lines

### ❤️ Heart Gesture Magic
- Form a heart shape with both hands to activate **special effects**
- Two beautiful neon pink hearts appear, one following each palm
- Hearts **dynamically scale** based on your hand's distance from the camera
  - Move hand closer → heart grows bigger
  - Move hand farther → heart shrinks smaller
- White and purple particles continuously stream from the heart's perimeter
- Hearts track their respective palms independently even when separated
- Fire automatically stops when hearts are active

### 🎨 Advanced Visual Effects
- Real-time hand tracking using MediaPipe's latest API
- Smooth anti-aliased rendering for professional quality
- Gaussian blur for realistic fire glow
- Particle systems with randomized motion and fading
- Mirror-view camera for intuitive interaction

## 🎥 Demo

**Watch the full demo on Instagram:**  
[@themlguppy](https://www.instagram.com/themlguppy)

*Experience the magic in action! See how the fire dances on palms and hearts respond to hand movements.*

## 🚀 Installation

### Prerequisites
- Python 3.12 or higher
- Webcam

### Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/ml-guppy-lab/fire_writing.git
   cd fire_writing
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. **Run the application**
   ```bash
   python fireWriting.py
   ```

## 📦 Dependencies

```
opencv-python==4.8.1.78
mediapipe==0.10.32
numpy>=1.26.0
scipy>=1.11.4
```

## 🎮 How to Use

### Fire Effects
1. **Show your palms** to the camera
2. Watch the **red fire** appear on your LEFT palm
3. Watch the **white fire** appear on your RIGHT palm
4. Move your hands around to see the fire particles flow dynamically

### Heart Gesture
1. **Bring both hands together** in front of the camera
2. **Touch your thumbs** together at the top
3. **Touch your index fingers** together at the bottom
4. Two hearts will appear near each palm! 🎉
5. **Separate your hands** and watch each heart follow its respective palm
6. **Move hands closer/farther** from the camera to see hearts scale dynamically

### Controls
| Key | Action |
|-----|--------|
| `c` | Clear hearts and resume fire effects |
| `q` | Quit application |

## 🛠️ Technical Details

### Architecture
- **Hand Detection**: MediaPipe HandLandmarker with VIDEO mode for real-time tracking
- **Particle System**: Custom FireParticle class with physics simulation
- **Heart Effects**: Parametric heart equations with dynamic scaling
- **Rendering**: Multi-layer blending with OpenCV for realistic effects

### Key Features Implementation
- **Fire Physics**: Particles with upward velocity, gravity, life cycles, and color transitions
- **Depth Estimation**: Hand size calculated from landmark distances to estimate camera distance
- **Gesture Recognition**: Distance-based detection for heart shape (thumbs + index fingers)
- **Smooth Rendering**: Gaussian blur + anti-aliasing for professional quality

## 🎨 Customization

You can customize various aspects in `fireWriting.py`:

- **Fire intensity**: Adjust `num_particles` parameter
- **Particle size**: Modify size range in `FireParticle.__init__`
- **Fire colors**: Change color values in `FireParticle.get_color()`
- **Heart size**: Adjust `base_size` in `calculate_heart_size()`
- **Particle speed**: Modify velocity ranges in particle initialization

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests

## 📄 License

This project is open source and available under the MIT License.

## 👨‍💻 Author

Created with ❤️ by **The ML Guppy**

**Follow me for more AI/ML projects:**
- Instagram: [@themlguppy](https://www.instagram.com/themlguppy)
- GitHub: [ml-guppy-lab](https://github.com/ml-guppy-lab)

---

## 🌟 Acknowledgments

- MediaPipe team for the excellent hand tracking model
- OpenCV community for the powerful computer vision library
- Everyone who watches and supports on Instagram! 🙏

---

**If you found this project interesting, don't forget to ⭐ star the repo!**
