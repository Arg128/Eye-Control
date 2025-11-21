import tkinter as tk
from PIL import Image, ImageTk, ImageSequence
import os

class GifPlayer(tk.Label):
    def __init__(self, master, gif_path, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.gif_path = gif_path
        self.frames = []
        self.load_gif()
        self.frame_index = 0
        self.animating = False

    def load_gif(self):
        """Load all frames of the GIF into memory."""
        if not os.path.exists(self.gif_path):
            raise FileNotFoundError(f"GIF file not found: {self.gif_path}")

        gif = Image.open(self.gif_path)
        self.frames = [ImageTk.PhotoImage(frame.copy().convert("RGBA"))
                       for frame in ImageSequence.Iterator(gif)]

    def start_animation(self):
        """Start or restart the GIF animation."""
        self.animating = True
        self.frame_index = 0
        self.show_frame()

    def stop_animation(self):
        """Stop the GIF animation."""
        self.animating = False

    def show_frame(self):
        """Display the current frame and schedule the next one."""
        if not self.animating:
            return
        self.config(image=self.frames[self.frame_index])
        self.frame_index = (self.frame_index + 1) % len(self.frames)
        # Schedule next frame (adjust delay for speed)
        self.after(100, self.show_frame)  # 100 ms per frame

# ---------------- MAIN APP ----------------
if __name__ == "__main__":
    root = tk.Tk()
    root.title("GIF Replay Example")
    os.chdir('..')
    gif_player = GifPlayer(root, "./assets/loading_image.gif")
    gif_player.pack(pady=10)

    # Buttons to control animation
    tk.Button(root, text="Play / Replay", command=gif_player.start_animation).pack(pady=5)
    tk.Button(root, text="Stop", command=gif_player.stop_animation).pack(pady=5)

    root.mainloop()