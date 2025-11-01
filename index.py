import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import time
import math
import json
import os
from datetime import datetime
from pathlib import Path
import random
import pickle

# AI Integration imports
try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False
    print("AI library not installed. Install with: pip install google-generativeai")

class JarmissAI:
    def __init__(self, root):
        self.root = root
        self.root.title("JARMISS AI System")
        self.root.geometry("1200x800")
        self.root.configure(bg="#0a0a1a")
        
        # State management
        self.current_user = None
        self.chat_history = []
        self.current_chat_id = None
        self.voice_enabled = False
        self.animation_frame = 0
        self.uploaded_file = None
        self.show_password = False
        
        # AI Configuration
        self.ai_model = None
        self.ai_enabled = False
        self.api_key = ""
        
        # Data file paths
        self.data_dir = Path("jarmiss_data")
        self.data_dir.mkdir(exist_ok=True)
        self.users_file = self.data_dir / "users.pkl"
        
        # Available avatars
        self.avatars = ["👤", "🤖", "👨", "👩", "🧑", "👨‍💻", "👩‍💻", "🧑‍💻", 
                       "👨‍🔬", "👩‍🔬", "🧙‍♂️", "🧙‍♀️", "🦸‍♂️", "🦸‍♀️", "🧑‍🚀"]
        
        # Load or initialize user database
        self.load_users_db()
        
        # Initialize UI
        self.show_loading_screen()
    
    def load_users_db(self):
        """Load users database from file or create default"""
        if self.users_file.exists():
            try:
                with open(self.users_file, 'rb') as f:
                    self.users_db = pickle.load(f)
            except:
                self.users_db = self.create_default_db()
        else:
            self.users_db = self.create_default_db()
    
    def create_default_db(self):
        """Create default user database"""
        return {
            "demo@jarmiss.ai": {
                "username": "Demo User",
                "password": "Demo@12345",
                "phone": "",
                "avatar": "🤖",
                "theme": "Dark",
                "notifications": True,
                "auto_save": True,
                "chats": [],
                "pinned_chats": [],
                "api_key": ""
            }
        }
    
    def save_users_db(self):
        """Save users database to file"""
        try:
            with open(self.users_file, 'wb') as f:
                pickle.dump(self.users_db, f)
        except Exception as e:
            print(f"Error saving user data: {e}")
    
    def configure_ai(self, api_key=None):
        """Configure AI with API key"""
        if not GEMINI_AVAILABLE:
            return False
        
        try:
            if api_key:
                self.api_key = api_key
                genai.configure(api_key=api_key)
                # Simple model initialization
                self.ai_model = genai.GenerativeModel('gemini-pro')
                self.ai_enabled = True
                print("✅ AI configured successfully!")
                return True
            return False
        except Exception as e:
            print(f"❌ AI Configuration Error: {e}")
            self.ai_enabled = False
            return False
    
    def get_ai_response_async(self, user_message):
        """Get AI response asynchronously"""
        def fetch_response():
            try:
                if self.ai_enabled and self.ai_model:
                    # Show typing indicator
                    self.root.after(0, lambda: self.show_typing_indicator())
                    
                    # Generate response - simplified for reliability
                    response = self.ai_model.generate_content(user_message)
                    
                    # Extract text from response
                    if hasattr(response, 'text'):
                        response_text = response.text
                    elif hasattr(response, 'candidates') and len(response.candidates) > 0:
                        response_text = response.candidates[0].content.parts[0].text
                    else:
                        response_text = "I received your message but couldn't generate a response. Please try again."
                    
                    # Hide typing indicator and show response
                    self.root.after(0, lambda: self.hide_typing_indicator())
                    self.root.after(0, lambda: self.display_ai_response(response_text))
                else:
                    # Fallback to rule-based response
                    response_text = self.generate_fallback_response(user_message)
                    self.root.after(0, lambda: self.display_ai_response(response_text))
            except Exception as e:
                error_msg = f"❌ AI Error: {str(e)}\n\n💡 Possible solutions:\n1. Check your API key is correct\n2. Verify internet connection\n3. API might have rate limits\n\nFalling back to basic responses."
                print(f"Detailed AI Error: {type(e).__name__}: {e}")  # Debug logging
                self.root.after(0, lambda: self.hide_typing_indicator())
                self.root.after(0, lambda: self.display_ai_response(error_msg))
        
        # Run in separate thread
        thread = threading.Thread(target=fetch_response, daemon=True)
        thread.start()
    
    def show_typing_indicator(self):
        """Show typing indicator in chat"""
        self.chat_display.config(state=tk.NORMAL)
        self.typing_indicator_mark = self.chat_display.index(tk.END)
        self.chat_display.insert(tk.END, "JARMISS", "ai")
        self.chat_display.insert(tk.END, " is typing", "timestamp")
        self.chat_display.insert(tk.END, "...\n", "typing")
        self.chat_display.tag_configure("typing", foreground="#ffaa00", font=("Arial", 11, "italic"))
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def hide_typing_indicator(self):
        """Remove typing indicator"""
        self.chat_display.config(state=tk.NORMAL)
        if hasattr(self, 'typing_indicator_mark'):
            self.chat_display.delete(self.typing_indicator_mark, tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def display_ai_response(self, response_text):
        """Display AI response in chat"""
        timestamp = datetime.now().strftime("%H:%M")
        
        msg = {
            "sender": "ai",
            "text": response_text,
            "timestamp": timestamp
        }
        self.chat_history.append(msg)
        
        self.display_message("ai", response_text, timestamp)
        self.save_current_chat()
    
    def play_sound_effect(self, sound_type="beep"):
        """Simulate sound effects with visual feedback"""
        if sound_type == "robot":
            print("🤖 ZZZ... BEEP... PROCESSING...")
    
    def show_loading_screen(self):
        """Phase 1: Loading screen with bouncing ball animation"""
        self.loading_frame = tk.Frame(self.root, bg="#0a0a1a")
        self.loading_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create canvas for animation
        self.loading_canvas = tk.Canvas(
            self.loading_frame, 
            bg="#0a0a1a", 
            highlightthickness=0,
            width=1200,
            height=800
        )
        self.loading_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Loading text
        self.loading_text = self.loading_canvas.create_text(
            600, 150,
            text="Just a rather mighty...\nInitializing JARMISS AI...",
            font=("Arial", 28, "bold"),
            fill="#ff69b4",
            justify=tk.CENTER
        )
        
        # Sound effect text
        self.sound_text = self.loading_canvas.create_text(
            600, 230,
            text="",
            font=("Courier", 14, "bold"),
            fill="#00ffff",
            justify=tk.CENTER
        )
        
        # Ball properties
        self.ball_x = 100
        self.ball_y = 400
        self.ball_radius = 40
        self.ball_velocity_y = 0
        self.ball_velocity_x = 8
        self.gravity = 0.8
        self.bounce_damping = 0.85
        self.ground_level = 650
        
        # Create glowing ball with multiple layers
        self.glow_circles = []
        for i in range(6):
            size = self.ball_radius + (i * 15)
            alpha_val = 200 - (i * 30)
            color = f"#{alpha_val:02x}{(alpha_val//3):02x}{255:02x}"
            circle = self.loading_canvas.create_oval(
                self.ball_x - size, self.ball_y - size,
                self.ball_x + size, self.ball_y + size,
                fill="", outline=color, width=3
            )
            self.glow_circles.append(circle)
        
        # Main ball (gradient effect with overlapping circles)
        self.ball_layers = []
        for i in range(4):
            size = self.ball_radius - (i * 8)
            brightness = 255 - (i * 40)
            color = f"#{brightness:02x}{69:02x}{180 + (i * 15):02x}"
            layer = self.loading_canvas.create_oval(
                self.ball_x - size, self.ball_y - size,
                self.ball_x + size, self.ball_y + size,
                fill=color, outline=""
            )
            self.ball_layers.append(layer)
        
        # Shine/highlight on ball
        self.ball_shine = self.loading_canvas.create_oval(
            self.ball_x - 15, self.ball_y - 20,
            self.ball_x + 10, self.ball_y - 5,
            fill="#ffffff", outline=""
        )
        
        # Ground line
        self.ground = self.loading_canvas.create_line(
            0, self.ground_level, 1200, self.ground_level,
            fill="#00ffff", width=3
        )
        
        # Trail effect
        self.trail_circles = []
        
        # Particle system for bounce effect
        self.particles = []
        
        # Start animation
        self.sound_messages = [
            "ZZZ... BEEP... ZZZ...",
            "PROCESSING... ZZZ...",
            "BEEP... BOOP... ZZZ...",
            "INITIALIZING... ZZZ...",
            "COMPUTING... BEEP...",
            "ZZZ... LOADING... ZZZ..."
        ]
        self.sound_index = 0
        self.animate_loading()
        self.update_sound_text()
    
    def update_sound_text(self):
        """Update robotic sound text"""
        if hasattr(self, 'loading_canvas'):
            self.loading_canvas.itemconfig(
                self.sound_text,
                text=self.sound_messages[self.sound_index % len(self.sound_messages)]
            )
            self.sound_index += 1
            if self.animation_frame < 250:
                self.root.after(600, self.update_sound_text)
    
    def animate_loading(self):
        """Animate bouncing ball"""
        if self.animation_frame < 250:
            # Apply gravity
            self.ball_velocity_y += self.gravity
            self.ball_y += self.ball_velocity_y
            self.ball_x += self.ball_velocity_x
            
            # Check ground collision
            if self.ball_y + self.ball_radius >= self.ground_level:
                self.ball_y = self.ground_level - self.ball_radius
                self.ball_velocity_y = -self.ball_velocity_y * self.bounce_damping
                
                # Create bounce particles
                for _ in range(8):
                    particle = {
                        'x': self.ball_x,
                        'y': self.ground_level,
                        'vx': random.uniform(-4, 4),
                        'vy': random.uniform(-8, -3),
                        'life': 20,
                        'id': None
                    }
                    particle['id'] = self.loading_canvas.create_oval(
                        particle['x'] - 3, particle['y'] - 3,
                        particle['x'] + 3, particle['y'] + 3,
                        fill="#00ffff", outline=""
                    )
                    self.particles.append(particle)
            
            # Bounce off right wall
            if self.ball_x + self.ball_radius >= 1200:
                self.ball_x = 1200 - self.ball_radius
                self.ball_velocity_x = -abs(self.ball_velocity_x)
            
            # Bounce off left wall
            if self.ball_x - self.ball_radius <= 0:
                self.ball_x = self.ball_radius
                self.ball_velocity_x = abs(self.ball_velocity_x)
            
            # Update trail
            if self.animation_frame % 3 == 0:
                trail = self.loading_canvas.create_oval(
                    self.ball_x - 8, self.ball_y - 8,
                    self.ball_x + 8, self.ball_y + 8,
                    fill="#ff69b4", outline="", stipple="gray50"
                )
                self.trail_circles.append(trail)
                if len(self.trail_circles) > 15:
                    self.loading_canvas.delete(self.trail_circles.pop(0))
            
            # Update particles
            for particle in self.particles[:]:
                particle['vy'] += 0.5
                particle['x'] += particle['vx']
                particle['y'] += particle['vy']
                particle['life'] -= 1
                
                self.loading_canvas.coords(
                    particle['id'],
                    particle['x'] - 3, particle['y'] - 3,
                    particle['x'] + 3, particle['y'] + 3
                )
                
                if particle['life'] <= 0:
                    self.loading_canvas.delete(particle['id'])
                    self.particles.remove(particle)
            
            # Update glow circles
            for i, circle in enumerate(self.glow_circles):
                size = self.ball_radius + (i * 15) + math.sin(self.animation_frame * 0.2) * 5
                self.loading_canvas.coords(
                    circle,
                    self.ball_x - size, self.ball_y - size,
                    self.ball_x + size, self.ball_y + size
                )
            
            # Update ball layers
            for i, layer in enumerate(self.ball_layers):
                size = self.ball_radius - (i * 8)
                self.loading_canvas.coords(
                    layer,
                    self.ball_x - size, self.ball_y - size,
                    self.ball_x + size, self.ball_y + size
                )
            
            # Update shine
            self.loading_canvas.coords(
                self.ball_shine,
                self.ball_x - 15, self.ball_y - 20,
                self.ball_x + 10, self.ball_y - 5
            )
            
            self.animation_frame += 1
            self.root.after(20, self.animate_loading)
        else:
            # Animation complete, show auth screen
            self.root.after(500, self.show_auth_screen)
    
    def show_auth_screen(self):
        """Phase 2: Authentication screen with visible demo credentials"""
        self.loading_frame.destroy()
        
        self.auth_frame = tk.Frame(self.root, bg="#0a0a1a")
        self.auth_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create notebook for tabs
        style = ttk.Style()
        style.theme_use('default')
        style.configure('TNotebook', background="#0a0a1a", borderwidth=0)
        style.configure('TNotebook.Tab', background="#1a1a2e", foreground="#00ffff", 
                       padding=[20, 10], font=("Arial", 12, "bold"))
        style.map('TNotebook.Tab', background=[('selected', '#16213e')])
        
        self.auth_notebook = ttk.Notebook(self.auth_frame)
        self.auth_notebook.pack(expand=True, fill=tk.BOTH, padx=100, pady=80)
        
        # Login Tab
        login_frame = tk.Frame(self.auth_notebook, bg="#16213e")
        self.auth_notebook.add(login_frame, text="Login")
        
        tk.Label(login_frame, text="JARMISS AI", font=("Arial", 36, "bold"), 
                fg="#ff69b4", bg="#16213e").pack(pady=20)
        tk.Label(login_frame, text="Just A Rather Mighty Intelligent System Service", 
                font=("Arial", 10, "italic"), fg="#00ffff", bg="#16213e").pack(pady=5)
        
        # Demo credentials box - PROMINENT
        demo_box = tk.Frame(login_frame, bg="#ffaa00", relief=tk.RAISED, bd=3)
        demo_box.pack(pady=15, padx=20, fill=tk.X)
        
        tk.Label(demo_box, text="🎯 DEMO ACCESS CREDENTIALS", 
                font=("Arial", 12, "bold"), fg="#000000", bg="#ffaa00").pack(pady=8)
        tk.Label(demo_box, text="📧 Email: demo@jarmiss.ai", 
                font=("Arial", 11), fg="#000000", bg="#ffaa00").pack(pady=2)
        tk.Label(demo_box, text="🔑 Password: Demo@12345", 
                font=("Arial", 11), fg="#000000", bg="#ffaa00").pack(pady=2)
        tk.Button(demo_box, text="⚡ Quick Demo Login", font=("Arial", 11, "bold"), 
                 bg="#000000", fg="#ffaa00", command=self.demo_login, 
                 cursor="hand2", padx=20, pady=5).pack(pady=8)
        
        # Login fields
        tk.Label(login_frame, text="Email:", font=("Arial", 12), 
                fg="#ffffff", bg="#16213e").pack(pady=5, anchor="w", padx=60)
        self.login_email = tk.Entry(login_frame, font=("Arial", 12), width=35, bg="#1a1a2e", 
                                    fg="#ffffff", insertbackground="#ffffff")
        self.login_email.pack(pady=5, padx=60)
        
        tk.Label(login_frame, text="Password:", font=("Arial", 12), 
                fg="#ffffff", bg="#16213e").pack(pady=5, anchor="w", padx=60)
        
        # Password frame with show/hide button
        pass_frame = tk.Frame(login_frame, bg="#16213e")
        pass_frame.pack(pady=5, padx=60, fill=tk.X)
        
        self.login_password = tk.Entry(pass_frame, font=("Arial", 12), show="*", 
                                       bg="#1a1a2e", fg="#ffffff", insertbackground="#ffffff")
        self.login_password.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        self.show_pass_btn = tk.Button(pass_frame, text="👁", font=("Arial", 12), 
                                       bg="#1a1a2e", fg="#00ffff", 
                                       command=self.toggle_password_visibility,
                                       cursor="hand2", relief=tk.FLAT, padx=8)
        self.show_pass_btn.pack(side=tk.LEFT, padx=5)
        
        tk.Button(login_frame, text="Login", font=("Arial", 14, "bold"), 
                 bg="#00ffff", fg="#000000", command=self.handle_login, 
                 cursor="hand2", padx=40, pady=10).pack(pady=20)
        
        tk.Button(login_frame, text="Forgot Password?", font=("Arial", 10), 
                 bg="#16213e", fg="#00ffff", relief=tk.FLAT, 
                 command=self.forgot_password, cursor="hand2").pack(pady=5)
        
        # Signup Tab
        signup_frame = tk.Frame(self.auth_notebook, bg="#16213e")
        self.auth_notebook.add(signup_frame, text="Sign Up")
        
        tk.Label(signup_frame, text="Create Account", font=("Arial", 30, "bold"), 
                fg="#ff69b4", bg="#16213e").pack(pady=15)
        
        # Signup fields
        fields_frame = tk.Frame(signup_frame, bg="#16213e")
        fields_frame.pack(pady=10)
        
        tk.Label(fields_frame, text="Email:", font=("Arial", 11), 
                fg="#ffffff", bg="#16213e").grid(row=0, column=0, sticky="w", pady=3, padx=5)
        self.signup_email = tk.Entry(fields_frame, font=("Arial", 11), width=30, 
                                     bg="#1a1a2e", fg="#ffffff", insertbackground="#ffffff")
        self.signup_email.grid(row=0, column=1, pady=3, padx=5)
        
        tk.Label(fields_frame, text="Username:", font=("Arial", 11), 
                fg="#ffffff", bg="#16213e").grid(row=1, column=0, sticky="w", pady=3, padx=5)
        self.signup_username = tk.Entry(fields_frame, font=("Arial", 11), width=30, 
                                        bg="#1a1a2e", fg="#ffffff", insertbackground="#ffffff")
        self.signup_username.grid(row=1, column=1, pady=3, padx=5)
        
        tk.Label(fields_frame, text="Phone (Optional):", font=("Arial", 11), 
                fg="#ffffff", bg="#16213e").grid(row=2, column=0, sticky="w", pady=3, padx=5)
        self.signup_phone = tk.Entry(fields_frame, font=("Arial", 11), width=30, 
                                     bg="#1a1a2e", fg="#ffffff", insertbackground="#ffffff")
        self.signup_phone.grid(row=2, column=1, pady=3, padx=5)
        
        tk.Label(fields_frame, text="Password:", font=("Arial", 11), 
                fg="#ffffff", bg="#16213e").grid(row=3, column=0, sticky="w", pady=3, padx=5)
        
        # Password with show/hide for signup
        signup_pass_frame = tk.Frame(fields_frame, bg="#16213e")
        signup_pass_frame.grid(row=3, column=1, pady=3, padx=5, sticky="ew")
        
        self.signup_password = tk.Entry(signup_pass_frame, font=("Arial", 11), 
                                        show="*", bg="#1a1a2e", fg="#ffffff", 
                                        insertbackground="#ffffff")
        self.signup_password.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.signup_password.bind('<KeyRelease>', self.check_password_strength)
        
        tk.Button(signup_pass_frame, text="👁", font=("Arial", 10), 
                 bg="#1a1a2e", fg="#00ffff", 
                 command=self.toggle_signup_password,
                 cursor="hand2", relief=tk.FLAT, padx=6).pack(side=tk.LEFT, padx=3)
        
        # Password strength indicator
        self.strength_frame = tk.Frame(signup_frame, bg="#16213e")
        self.strength_frame.pack(pady=5)
        self.strength_bar = tk.Canvas(self.strength_frame, width=200, height=10, 
                                      bg="#1a1a2e", highlightthickness=0)
        self.strength_bar.pack()
        self.strength_label = tk.Label(self.strength_frame, text="", font=("Arial", 9), 
                                       fg="#aaaaaa", bg="#16213e")
        self.strength_label.pack()
        
        tk.Label(fields_frame, text="Confirm Password:", font=("Arial", 11), 
                fg="#ffffff", bg="#16213e").grid(row=4, column=0, sticky="w", pady=3, padx=5)
        self.signup_confirm = tk.Entry(fields_frame, font=("Arial", 11), width=30, 
                                       show="*", bg="#1a1a2e", fg="#ffffff", 
                                       insertbackground="#ffffff")
        self.signup_confirm.grid(row=4, column=1, pady=3, padx=5)
        
        tk.Button(signup_frame, text="Create Account", font=("Arial", 14, "bold"), 
                 bg="#00ffff", fg="#000000", command=self.handle_signup, 
                 cursor="hand2", padx=30, pady=10).pack(pady=20)
    
    def toggle_password_visibility(self):
        """Toggle password visibility for login"""
        if self.login_password.cget('show') == '*':
            self.login_password.config(show='')
            self.show_pass_btn.config(text='🙈')
        else:
            self.login_password.config(show='*')
            self.show_pass_btn.config(text='👁')
    
    def toggle_signup_password(self):
        """Toggle password visibility for signup"""
        if self.signup_password.cget('show') == '*':
            self.signup_password.config(show='')
        else:
            self.signup_password.config(show='*')
    
    def check_password_strength(self, event=None):
        """Check password strength visually"""
        password = self.signup_password.get()
        strength = 0
        
        if len(password) >= 8:
            strength += 1
        if any(c.isupper() for c in password):
            strength += 1
        if any(c.islower() for c in password):
            strength += 1
        if any(c.isdigit() for c in password):
            strength += 1
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            strength += 1
        
        # Update bar
        self.strength_bar.delete("all")
        colors = ["#ff0000", "#ff6600", "#ffaa00", "#aaff00", "#00ff00"]
        if strength > 0:
            width = (strength / 5) * 200
            self.strength_bar.create_rectangle(0, 0, width, 10, fill=colors[strength-1], outline="")
        
        labels = ["Very Weak", "Weak", "Fair", "Good", "Strong"]
        self.strength_label.config(text=labels[strength-1] if strength > 0 else "")
    
    def handle_login(self):
        """Handle login attempt"""
        email = self.login_email.get()
        password = self.login_password.get()
        
        if email in self.users_db and self.users_db[email]["password"] == password:
            self.current_user = email
            # Load user's API key if saved
            saved_key = self.users_db[email].get("api_key", "")
            if saved_key:
                self.configure_ai(saved_key)
            self.show_welcome_animation()
        else:
            messagebox.showerror("Login Failed", 
                               "Invalid credentials. Account not found.\n\nWould you like to sign up?")
    
    def demo_login(self):
        """Direct demo login"""
        self.current_user = "demo@jarmiss.ai"
        # Load user's API key if saved
        saved_key = self.users_db[self.current_user].get("api_key", "")
        if saved_key:
            self.configure_ai(saved_key)
        self.show_welcome_animation()
    
    def handle_signup(self):
        """Handle signup"""
        email = self.signup_email.get()
        username = self.signup_username.get()
        phone = self.signup_phone.get()
        password = self.signup_password.get()
        confirm = self.signup_confirm.get()
        
        # Validation
        if not email or not username or not password:
            messagebox.showerror("Error", "Please fill in all required fields")
            return
        
        if password != confirm:
            messagebox.showerror("Error", "Passwords do not match")
            return
        
        if len(password) < 8:
            messagebox.showerror("Error", "Password must be at least 8 characters")
            return
        
        if email in self.users_db:
            messagebox.showerror("Error", "Email already registered")
            return
        
        # Create account
        self.users_db[email] = {
            "username": username,
            "password": password,
            "phone": phone,
            "avatar": "👤",
            "theme": "Dark",
            "notifications": True,
            "auto_save": True,
            "chats": [],
            "pinned_chats": [],
            "api_key": ""
        }
        self.save_users_db()
        
        messagebox.showinfo("Success", "Account created successfully!")
        self.current_user = email
        self.show_welcome_animation()
    
    def forgot_password(self):
        """Handle forgot password"""
        messagebox.showinfo("Forgot Password", 
                          "Password recovery would be sent to your email.\n(Demo feature)")
    
    def show_welcome_animation(self):
        """Phase 3: Welcome back animation with bouncing balls"""
        self.auth_frame.destroy()
        
        self.welcome_frame = tk.Frame(self.root, bg="#0a0a1a")
        self.welcome_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create canvas for animation
        canvas = tk.Canvas(self.welcome_frame, bg="#0a0a1a", highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)
        
        # Multiple bouncing balls with different properties
        self.welcome_balls = []
        colors = ["#ff69b4", "#00ffff", "#ffaa00", "#00ff00", "#ff00ff"]
        
        for i in range(5):
            ball = {
                'x': 200 + i * 200,
                'y': 200 + random.randint(-50, 50),
                'radius': 30 + random.randint(-10, 10),
                'vy': random.uniform(-2, 2),
                'vx': random.uniform(-3, 3),
                'color': colors[i],
                'bounce_height': random.uniform(0.7, 0.9),
                'circles': []
            }
            
            # Create glow layers for each ball
            for j in range(4):
                size = ball['radius'] + (j * 12)
                alpha = 200 - (j * 40)
                r, g, b = int(ball['color'][1:3], 16), int(ball['color'][3:5], 16), int(ball['color'][5:7], 16)
                glow_color = f"#{max(0, r-j*20):02x}{max(0, g-j*20):02x}{max(0, b-j*20):02x}"
                
                circle = canvas.create_oval(
                    ball['x'] - size, ball['y'] - size,
                    ball['x'] + size, ball['y'] + size,
                    fill="", outline=glow_color, width=2
                )
                ball['circles'].append(circle)
            
            # Main ball
            ball['main'] = canvas.create_oval(
                ball['x'] - ball['radius'], ball['y'] - ball['radius'],
                ball['x'] + ball['radius'], ball['y'] + ball['radius'],
                fill=ball['color'], outline="#ffffff", width=2
            )
            
            # Shine
            ball['shine'] = canvas.create_oval(
                ball['x'] - 10, ball['y'] - 15,
                ball['x'] + 5, ball['y'] - 5,
                fill="#ffffff", outline=""
            )
            
            self.welcome_balls.append(ball)
        
        # Welcome text
        canvas.create_text(
            600, 550,
            text="I am JARMISS.\nYour personal intelligent assistant.\nWelcome back.",
            font=("Arial", 24, "bold"),
            fill="#ff69b4",
            justify=tk.CENTER
        )
        
        # ZZZ sound effect
        canvas.create_text(
            600, 650,
            text="ZZZ... BEEP... INITIALIZING... ZZZ...",
            font=("Courier", 12, "bold"),
            fill="#00ffff",
            justify=tk.CENTER
        )
        
        # Animate balls
        self.welcome_animation_frame = 0
        self.animate_welcome_balls(canvas)
        
        # Transition to dashboard after 3 seconds
        self.root.after(3000, self.show_dashboard)
    
    def animate_welcome_balls(self, canvas):
        """Animate the welcome screen bouncing balls"""
        if self.welcome_animation_frame < 150 and hasattr(self, 'welcome_frame'):
            for ball in self.welcome_balls:
                # Apply physics
                ball['vy'] += 0.5
                ball['y'] += ball['vy']
                ball['x'] += ball['vx']
                
                # Bounce off bottom
                if ball['y'] + ball['radius'] >= 500:
                    ball['y'] = 500 - ball['radius']
                    ball['vy'] = -abs(ball['vy']) * ball['bounce_height']
                
                # Bounce off top
                if ball['y'] - ball['radius'] <= 100:
                    ball['y'] = 100 + ball['radius']
                    ball['vy'] = abs(ball['vy'])
                
                # Bounce off sides
                if ball['x'] + ball['radius'] >= 1100:
                    ball['x'] = 1100 - ball['radius']
                    ball['vx'] = -abs(ball['vx'])
                elif ball['x'] - ball['radius'] <= 100:
                    ball['x'] = 100 + ball['radius']
                    ball['vx'] = abs(ball['vx'])
                
                # Update glow circles
                for j, circle in enumerate(ball['circles']):
                    size = ball['radius'] + (j * 12) + math.sin(self.welcome_animation_frame * 0.2 + j) * 3
                    canvas.coords(
                        circle,
                        ball['x'] - size, ball['y'] - size,
                        ball['x'] + size, ball['y'] + size
                    )
                
                # Update main ball
                canvas.coords(
                    ball['main'],
                    ball['x'] - ball['radius'], ball['y'] - ball['radius'],
                    ball['x'] + ball['radius'], ball['y'] + ball['radius']
                )
                
                # Update shine
                canvas.coords(
                    ball['shine'],
                    ball['x'] - 10, ball['y'] - 15,
                    ball['x'] + 5, ball['y'] - 5
                )
            
            self.welcome_animation_frame += 1
            self.root.after(20, lambda: self.animate_welcome_balls(canvas))
    
    def show_dashboard(self):
        """Phase 4: Main dashboard"""
        self.welcome_frame.destroy()
        
        # Main container
        self.dashboard_frame = tk.Frame(self.root, bg="#0a0a1a")
        self.dashboard_frame.pack(fill=tk.BOTH, expand=True)
        
        # Left Panel - Chat History
        left_panel = tk.Frame(self.dashboard_frame, bg="#16213e", width=250)
        left_panel.pack(side=tk.LEFT, fill=tk.Y)
        left_panel.pack_propagate(False)
        
        tk.Label(left_panel, text="Chat History", font=("Arial", 16, "bold"), 
                fg="#ff69b4", bg="#16213e").pack(pady=10)
        
        # Search and New Chat
        search_frame = tk.Frame(left_panel, bg="#16213e")
        search_frame.pack(pady=5, padx=10, fill=tk.X)
        
        self.search_entry = tk.Entry(search_frame, font=("Arial", 10), bg="#1a1a2e", 
                                     fg="#ffffff", insertbackground="#ffffff")
        self.search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0,5))
        self.search_entry.bind('<KeyRelease>', lambda e: self.search_chats())
        
        tk.Button(search_frame, text="🔍", font=("Arial", 12), bg="#1a1a2e", 
                 fg="#00ffff", command=self.search_chats, cursor="hand2").pack(side=tk.LEFT)
        
        tk.Button(left_panel, text="➕ New Chat", font=("Arial", 11, "bold"), 
                 bg="#00ffff", fg="#000000", command=self.new_chat, 
                 cursor="hand2").pack(pady=10, padx=10, fill=tk.X)
        
        # Chat list
        self.chat_list_frame = tk.Frame(left_panel, bg="#16213e")
        self.chat_list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Scrollable chat list
        self.chat_canvas = tk.Canvas(self.chat_list_frame, bg="#16213e", highlightthickness=0)
        scrollbar = tk.Scrollbar(self.chat_list_frame, orient="vertical", 
                                command=self.chat_canvas.yview)
        self.chat_scrollable = tk.Frame(self.chat_canvas, bg="#16213e")
        
        self.chat_scrollable.bind(
            "<Configure>",
            lambda e: self.chat_canvas.configure(scrollregion=self.chat_canvas.bbox("all"))
        )
        
        self.chat_canvas.create_window((0, 0), window=self.chat_scrollable, anchor="nw")
        self.chat_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.chat_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Center Panel - Chat Area
        center_panel = tk.Frame(self.dashboard_frame, bg="#0a0a1a")
        center_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Top bar with profile
        top_bar = tk.Frame(center_panel, bg="#16213e", height=60)
        top_bar.pack(side=tk.TOP, fill=tk.X)
        top_bar.pack_propagate(False)
        
        tk.Label(top_bar, text="JARMISS AI", font=("Arial", 20, "bold"), 
                fg="#ff69b4", bg="#16213e").pack(side=tk.LEFT, padx=20, pady=10)
        
        # AI Status indicator
        self.ai_status_label = tk.Label(top_bar, text="🤖 AI: " + ("Active" if self.ai_enabled else "Offline"), 
                                       font=("Arial", 10, "bold"),
                                       fg="#00ff00" if self.ai_enabled else "#ff6666", 
                                       bg="#16213e")
        self.ai_status_label.pack(side=tk.LEFT, padx=10)
        
        # Profile section
        profile_frame = tk.Frame(top_bar, bg="#16213e")
        profile_frame.pack(side=tk.RIGHT, padx=20, pady=10)
        
        username = self.users_db[self.current_user]["username"]
        avatar = self.users_db[self.current_user].get("avatar", "👤")
        
        tk.Label(profile_frame, text=username, font=("Arial", 12), 
                fg="#ffffff", bg="#16213e").pack(side=tk.LEFT, padx=10)
        
        tk.Button(profile_frame, text=avatar, font=("Arial", 16), bg="#1a1a2e", 
                 fg="#00ffff", command=self.show_profile, cursor="hand2", 
                 relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=5)
        
        tk.Button(profile_frame, text="⚙️", font=("Arial", 16), bg="#1a1a2e", 
                 fg="#ffaa00", command=self.show_ai_settings, cursor="hand2", 
                 relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=5)
        
        tk.Button(profile_frame, text="🚪", font=("Arial", 16), bg="#1a1a2e", 
                 fg="#ff6666", command=self.logout, cursor="hand2", 
                 relief=tk.FLAT, padx=10).pack(side=tk.LEFT)
        
        # Chat display area
        self.chat_display_frame = tk.Frame(center_panel, bg="#0a0a1a")
        self.chat_display_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Chat text with scrollbar
        chat_scroll = tk.Scrollbar(self.chat_display_frame)
        chat_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.chat_display = tk.Text(
            self.chat_display_frame,
            font=("Arial", 11),
            bg="#1a1a2e",
            fg="#ffffff",
            wrap=tk.WORD,
            yscrollcommand=chat_scroll.set,
            state=tk.DISABLED,
            padx=15,
            pady=15
        )
        self.chat_display.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        chat_scroll.config(command=self.chat_display.yview)
        
        # Configure text tags
        self.chat_display.tag_configure("user", foreground="#00ffff", font=("Arial", 11, "bold"))
        self.chat_display.tag_configure("ai", foreground="#ff69b4", font=("Arial", 11, "bold"))
        self.chat_display.tag_configure("timestamp", foreground="#888888", font=("Arial", 9))
        
        # Input area
        input_frame = tk.Frame(center_panel, bg="#16213e")
        input_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=20, pady=10)
        
        # File preview
        self.file_preview_frame = tk.Frame(input_frame, bg="#16213e")
        
        # Input controls
        controls_frame = tk.Frame(input_frame, bg="#16213e")
        controls_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=5)
        
        # Buttons
        tk.Button(controls_frame, text="📁", font=("Arial", 14), bg="#1a1a2e", 
                 fg="#00ffff", command=self.upload_file, cursor="hand2", 
                 relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=2)
        
        tk.Button(controls_frame, text="📸", font=("Arial", 14), bg="#1a1a2e", 
                 fg="#00ffff", command=self.capture_photo, cursor="hand2", 
                 relief=tk.FLAT, padx=10).pack(side=tk.LEFT, padx=2)
        
        self.voice_btn = tk.Button(controls_frame, text="🎤", font=("Arial", 14), 
                                   bg="#1a1a2e", fg="#00ffff", command=self.toggle_voice, 
                                   cursor="hand2", relief=tk.FLAT, padx=10)
        self.voice_btn.pack(side=tk.LEFT, padx=2)
        
        # Input text
        self.input_text = tk.Text(controls_frame, font=("Arial", 11), height=3, 
                                 bg="#1a1a2e", fg="#ffffff", insertbackground="#ffffff", 
                                 wrap=tk.WORD)
        self.input_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        self.input_text.bind('<Return>', lambda e: self.send_message() if not e.state & 0x1 else None)
        
        tk.Button(controls_frame, text="Send", font=("Arial", 12, "bold"), 
                 bg="#00ffff", fg="#000000", command=self.send_message, 
                 cursor="hand2", padx=15).pack(side=tk.RIGHT, padx=2)
        
        # Initialize with new chat
        self.new_chat()
    
    def show_ai_settings(self):
        """Show AI configuration settings"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("AI Settings")
        settings_window.geometry("600x500")
        settings_window.configure(bg="#16213e")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        # Center window
        settings_window.update_idletasks()
        x = (settings_window.winfo_screenwidth() // 2) - (600 // 2)
        y = (settings_window.winfo_screenheight() // 2) - (500 // 2)
        settings_window.geometry(f"600x500+{x}+{y}")
        
        # Header
        tk.Label(settings_window, text="🤖 AI Configuration", font=("Arial", 24, "bold"), 
                fg="#ff69b4", bg="#16213e").pack(pady=20)
        
        # Status
        status_frame = tk.Frame(settings_window, bg="#1a1a2e", relief=tk.RAISED, bd=2)
        status_frame.pack(fill=tk.X, padx=30, pady=10)
        
        tk.Label(status_frame, text="Current Status:", font=("Arial", 12, "bold"), 
                fg="#00ffff", bg="#1a1a2e").pack(pady=10)
        
        status_text = "✅ AI Active" if self.ai_enabled else "❌ AI Offline (Using fallback responses)"
        status_color = "#00ff00" if self.ai_enabled else "#ff6666"
        
        tk.Label(status_frame, text=status_text, font=("Arial", 11), 
                fg=status_color, bg="#1a1a2e").pack(pady=5, padx=20)
        
        if not GEMINI_AVAILABLE:
            tk.Label(status_frame, text="⚠️ AI library not installed", 
                    font=("Arial", 10, "italic"), fg="#ffaa00", bg="#1a1a2e").pack(pady=5)
            tk.Label(status_frame, text="Install: pip install google-generativeai", 
                    font=("Arial", 9), fg="#ffffff", bg="#1a1a2e").pack(pady=(0, 10))
        
        # API Key Section
        api_frame = tk.LabelFrame(settings_window, text="🔑 AI API Key", 
                                 font=("Arial", 14, "bold"), fg="#00ffff", 
                                 bg="#1a1a2e", relief=tk.RAISED, bd=2)
        api_frame.pack(fill=tk.X, padx=30, pady=20)
        
        tk.Label(api_frame, text="Enter your AI API key to enable smart responses:", 
                font=("Arial", 11), fg="#ffffff", bg="#1a1a2e").pack(pady=10, padx=20, anchor="w")
        
        # API Key Entry
        key_frame = tk.Frame(api_frame, bg="#1a1a2e")
        key_frame.pack(fill=tk.X, padx=20, pady=5)
        
        api_key_entry = tk.Entry(key_frame, font=("Arial", 11), bg="#16213e", 
                                fg="#ffffff", insertbackground="#ffffff", show="*")
        api_key_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        # Pre-fill if key exists
        current_key = self.users_db[self.current_user].get("api_key", "")
        if current_key:
            api_key_entry.insert(0, current_key)
        
        show_key_var = tk.BooleanVar(value=False)
        def toggle_key_visibility():
            api_key_entry.config(show="" if show_key_var.get() else "*")
        
        def quick_save_key():
            """Quick save API key without testing"""
            key = api_key_entry.get().strip()
            if key:
                self.users_db[self.current_user]["api_key"] = key
                self.save_users_db()
                
                # Also try to configure AI immediately
                if self.configure_ai(key):
                    if hasattr(self, 'ai_status_label'):
                        self.ai_status_label.config(text="🤖 AI: Active", fg="#00ff00")
                    messagebox.showinfo("Saved", 
                        "✅ API key saved and AI activated!\n\n"
                        "🤖 You can now chat with intelligent AI responses!", 
                        parent=settings_window)
                else:
                    messagebox.showinfo("Saved", 
                        "✅ API key saved!\n\n"
                        "⚠️ AI configuration needs verification.\n"
                        "Use 'Test Connection' to verify.", 
                        parent=settings_window)
            else:
                messagebox.showerror("Error", "Please enter an API key", parent=settings_window)
        
        tk.Checkbutton(key_frame, text="Show", variable=show_key_var, 
                      command=toggle_key_visibility, font=("Arial", 10),
                      bg="#1a1a2e", fg="#ffffff", selectcolor="#16213e",
                      activebackground="#1a1a2e", activeforeground="#00ffff").pack(side=tk.LEFT, padx=2)
        
        tk.Button(key_frame, text="💾 Save", font=("Arial", 10, "bold"), 
                 bg="#00ff00", fg="#000000", command=quick_save_key, 
                 cursor="hand2", relief=tk.RAISED, bd=2, padx=8, pady=2).pack(side=tk.LEFT, padx=2)
        
        # Info
        info_text = scrolledtext.ScrolledText(api_frame, font=("Arial", 9), height=6, 
                                             bg="#16213e", fg="#aaaaaa", wrap=tk.WORD,
                                             relief=tk.FLAT)
        info_text.pack(fill=tk.X, padx=20, pady=10)
        info_text.insert(1.0, 
            "📌 How to get your API key:\n"
            "1. Visit: https://aistudio.google.com/app/apikey\n"
            "2. Click 'Create API Key'\n"
            "3. Copy the key and paste it above\n"
            "4. Free tier includes 60 requests per minute\n\n"
            "⚠️ Keep your API key secure and don't share it!"
        )
        info_text.config(state=tk.DISABLED)
        
        # Test connection
        test_result_label = tk.Label(settings_window, text="", font=("Arial", 10), 
                                    bg="#16213e")
        test_result_label.pack(pady=5)
        
        def test_connection():
            key = api_key_entry.get().strip()
            if not key:
                test_result_label.config(text="❌ Please enter an API key", fg="#ff6666")
                return
            
            test_result_label.config(text="🔄 Testing connection...", fg="#ffaa00")
            settings_window.update()
            
            def test_thread():
                try:
                    genai.configure(api_key=key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    response = model.generate_content("Say 'Hello, I am working!' if you can read this.")
                    if response and (hasattr(response, 'text') or hasattr(response, 'candidates')):
                        settings_window.after(0, lambda: test_result_label.config(
                            text="✅ Connection successful! AI is working!", fg="#00ff00"))
                        return True
                except Exception as e:
                    error_text = str(e)[:80]
                    settings_window.after(0, lambda: test_result_label.config(
                        text=f"❌ Failed: {error_text}", fg="#ff6666"))
                return False
            
            thread = threading.Thread(target=test_thread, daemon=True)
            thread.start()
        
        def save_api_key():
            key = api_key_entry.get().strip()
            if key:
                # Save to user profile
                self.users_db[self.current_user]["api_key"] = key
                self.save_users_db()  # Persist to disk
                
                # Configure AI
                if self.configure_ai(key):
                    # Update status label in main window
                    if hasattr(self, 'ai_status_label'):
                        self.ai_status_label.config(text="🤖 AI: Active", fg="#00ff00")
                    messagebox.showinfo("Success", 
                        "✅ API key saved and activated successfully!\n\n"
                        "🤖 AI is now active and ready to chat!\n\n"
                        "💬 Try asking me anything - I'll give you intelligent responses.\n\n"
                        "💾 Your API key is securely stored and will be loaded automatically on next login.", 
                        parent=settings_window)
                    settings_window.destroy()
                else:
                    messagebox.showerror("Error", 
                        "❌ Failed to configure AI.\n\n"
                        "Please check:\n"
                        "1. Your API key is correct\n"
                        "2. You have installed: pip install google-generativeai\n"
                        "3. Your internet connection is active", 
                        parent=settings_window)
            else:
                messagebox.showerror("Error", "Please enter an API key", parent=settings_window)
        
        # Buttons
        btn_frame = tk.Frame(settings_window, bg="#16213e")
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="🧪 Test Connection", font=("Arial", 11, "bold"), 
                 bg="#ffaa00", fg="#000000", command=test_connection, 
                 cursor="hand2", padx=15, pady=8).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="💾 Save & Activate", font=("Arial", 11, "bold"), 
                 bg="#00ff00", fg="#000000", command=save_api_key, 
                 cursor="hand2", padx=15, pady=8).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="❌ Cancel", font=("Arial", 11, "bold"), 
                 bg="#ff6666", fg="#ffffff", command=settings_window.destroy, 
                 cursor="hand2", padx=15, pady=8).pack(side=tk.LEFT, padx=5)
    
    def new_chat(self):
        """Create a new chat"""
        chat_id = f"chat_{int(time.time())}"
        self.current_chat_id = chat_id
        self.chat_history = []
        self.uploaded_file = None
        
        # Clear display
        self.chat_display.config(state=tk.NORMAL)
        self.chat_display.delete(1.0, tk.END)
        self.chat_display.config(state=tk.DISABLED)
        
        # Hide file preview
        if hasattr(self, 'file_preview_frame'):
            self.file_preview_frame.pack_forget()
        
        # Add to user's chat list
        if self.current_user:
            self.users_db[self.current_user]["chats"].append({
                "id": chat_id,
                "title": "New Chat",
                "timestamp": datetime.now().isoformat(),
                "messages": []
            })
        
        self.update_chat_list()
    
    def update_chat_list(self):
        """Update the chat list in left panel with pinned chats at top"""
        for widget in self.chat_scrollable.winfo_children():
            widget.destroy()
        
        if self.current_user:
            chats = self.users_db[self.current_user]["chats"]
            pinned_chat_ids = self.users_db[self.current_user].get("pinned_chats", [])
            
            # Separate pinned and regular chats
            pinned_chats = [c for c in chats if c["id"] in pinned_chat_ids]
            regular_chats = [c for c in chats if c["id"] not in pinned_chat_ids]
            
            # Display pinned chats first
            if pinned_chats:
                pin_header = tk.Label(
                    self.chat_scrollable,
                    text="📌 PINNED CHATS",
                    font=("Arial", 9, "bold"),
                    bg="#16213e",
                    fg="#ffaa00",
                    anchor="w",
                    padx=10,
                    pady=5
                )
                pin_header.pack(fill=tk.X, pady=(5, 2))
                
                for chat in reversed(pinned_chats):
                    self.create_chat_button(chat, is_pinned=True)
            
            # Display regular chats
            if regular_chats:
                if pinned_chats:
                    regular_header = tk.Label(
                        self.chat_scrollable,
                        text="💬 ALL CHATS",
                        font=("Arial", 9, "bold"),
                        bg="#16213e",
                        fg="#00ffff",
                        anchor="w",
                        padx=10,
                        pady=5
                    )
                    regular_header.pack(fill=tk.X, pady=(10, 2))
                
                for chat in reversed(regular_chats):
                    self.create_chat_button(chat, is_pinned=False)
    
    def create_chat_button(self, chat, is_pinned=False):
        """Create a chat button with options menu"""
        chat_frame = tk.Frame(self.chat_scrollable, bg="#16213e")
        chat_frame.pack(fill=tk.X, pady=1)
        
        is_current = chat["id"] == self.current_chat_id
        
        # Main chat button
        btn = tk.Button(
            chat_frame,
            text=f"{'📌 ' if is_pinned else ''}{chat['title'][:22]}{'...' if len(chat['title']) > 22 else ''}",
            font=("Arial", 10, "bold" if is_current else "normal"),
            bg="#00ffff" if is_current else "#1a1a2e",
            fg="#000000" if is_current else "#ffffff",
            anchor="w",
            command=lambda c=chat["id"]: self.load_chat(c),
            cursor="hand2",
            relief=tk.FLAT,
            padx=10,
            pady=8
        )
        btn.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Options menu button
        options_btn = tk.Button(
            chat_frame,
            text="⋮",
            font=("Arial", 14, "bold"),
            bg="#00ffff" if is_current else "#1a1a2e",
            fg="#000000" if is_current else "#ffffff",
            command=lambda c=chat: self.show_chat_options(c, chat_frame),
            cursor="hand2",
            relief=tk.FLAT,
            padx=8,
            pady=8
        )
        options_btn.pack(side=tk.RIGHT)
    
    def show_chat_options(self, chat, parent_frame):
        """Show options menu for a chat"""
        # Create popup menu
        menu = tk.Menu(self.root, tearoff=0, bg="#1a1a2e", fg="#ffffff", 
                      activebackground="#00ffff", activeforeground="#000000",
                      font=("Arial", 10))
        
        pinned_chats = self.users_db[self.current_user].get("pinned_chats", [])
        is_pinned = chat["id"] in pinned_chats
        
        # Add menu options
        if is_pinned:
            menu.add_command(label="📌 Unpin Chat", 
                           command=lambda: self.unpin_chat(chat["id"]))
        else:
            menu.add_command(label="📌 Pin Chat", 
                           command=lambda: self.pin_chat(chat["id"]))
        
        menu.add_command(label="✏️ Edit Name", 
                        command=lambda: self.edit_chat_name(chat))
        menu.add_separator()
        menu.add_command(label="🗑️ Delete Chat", 
                        command=lambda: self.delete_chat(chat["id"]))
        
        # Show menu at mouse position
        try:
            menu.tk_popup(parent_frame.winfo_rootx() + parent_frame.winfo_width() - 50,
                         parent_frame.winfo_rooty() + parent_frame.winfo_height())
        finally:
            menu.grab_release()
    
    def pin_chat(self, chat_id):
        """Pin a chat to the top"""
        pinned_chats = self.users_db[self.current_user].get("pinned_chats", [])
        if chat_id not in pinned_chats:
            pinned_chats.append(chat_id)
            self.users_db[self.current_user]["pinned_chats"] = pinned_chats
            self.update_chat_list()
    
    def unpin_chat(self, chat_id):
        """Unpin a chat"""
        pinned_chats = self.users_db[self.current_user].get("pinned_chats", [])
        if chat_id in pinned_chats:
            pinned_chats.remove(chat_id)
            self.users_db[self.current_user]["pinned_chats"] = pinned_chats
            self.update_chat_list()
    
    def edit_chat_name(self, chat):
        """Edit the name of a chat"""
        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit Chat Name")
        edit_window.geometry("450x200")
        edit_window.configure(bg="#16213e")
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        # Center the window
        edit_window.update_idletasks()
        x = (edit_window.winfo_screenwidth() // 2) - (450 // 2)
        y = (edit_window.winfo_screenheight() // 2) - (200 // 2)
        edit_window.geometry(f"450x200+{x}+{y}")
        
        tk.Label(edit_window, text="✏️ Edit Chat Name", font=("Arial", 16, "bold"), 
                fg="#ff69b4", bg="#16213e").pack(pady=20)
        
        tk.Label(edit_window, text="Enter new name:", font=("Arial", 11), 
                fg="#ffffff", bg="#16213e").pack(pady=5)
        
        name_entry = tk.Entry(edit_window, font=("Arial", 12), width=35,
                             bg="#1a1a2e", fg="#ffffff", insertbackground="#ffffff")
        name_entry.insert(0, chat["title"])
        name_entry.pack(pady=10, padx=30)
        name_entry.focus()
        name_entry.select_range(0, tk.END)
        
        def save_name():
            new_name = name_entry.get().strip()
            if new_name:
                chat["title"] = new_name
                self.update_chat_list()
                edit_window.destroy()
            else:
                messagebox.showerror("Error", "Chat name cannot be empty", parent=edit_window)
        
        # Bind Enter key
        name_entry.bind('<Return>', lambda e: save_name())
        
        btn_frame = tk.Frame(edit_window, bg="#16213e")
        btn_frame.pack(pady=15)
        
        tk.Button(btn_frame, text="💾 Save", font=("Arial", 11, "bold"), 
                 bg="#00ff00", fg="#000000", command=save_name, 
                 cursor="hand2", padx=20, pady=8).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="❌ Cancel", font=("Arial", 11, "bold"), 
                 bg="#ff6666", fg="#ffffff", command=edit_window.destroy, 
                 cursor="hand2", padx=20, pady=8).pack(side=tk.LEFT, padx=5)
    
    def delete_chat(self, chat_id):
        """Delete a chat"""
        if messagebox.askyesno("Delete Chat", 
                              "Are you sure you want to delete this chat?\nThis action cannot be undone!"):
            # Remove from chats list
            self.users_db[self.current_user]["chats"] = [
                c for c in self.users_db[self.current_user]["chats"] 
                if c["id"] != chat_id
            ]
            
            # Remove from pinned if pinned
            pinned_chats = self.users_db[self.current_user].get("pinned_chats", [])
            if chat_id in pinned_chats:
                pinned_chats.remove(chat_id)
                self.users_db[self.current_user]["pinned_chats"] = pinned_chats
            
            # If current chat was deleted, create new one
            if self.current_chat_id == chat_id:
                self.new_chat()
            else:
                self.update_chat_list()
    
    def load_chat(self, chat_id):
        """Load a specific chat"""
        self.current_chat_id = chat_id
        self.uploaded_file = None
        
        # Hide file preview
        if hasattr(self, 'file_preview_frame'):
            self.file_preview_frame.pack_forget()
        
        # Find chat in user's chats
        chat = next((c for c in self.users_db[self.current_user]["chats"] 
                    if c["id"] == chat_id), None)
        
        if chat:
            self.chat_history = chat["messages"]
            
            # Display messages
            self.chat_display.config(state=tk.NORMAL)
            self.chat_display.delete(1.0, tk.END)
            
            for msg in self.chat_history:
                self.display_message(msg["sender"], msg["text"], msg["timestamp"])
            
            self.chat_display.config(state=tk.DISABLED)
            self.update_chat_list()
    
    def send_message(self):
        """Send a message"""
        text = self.input_text.get("1.0", tk.END).strip()
        
        # Check if there's a file attached
        if self.uploaded_file and not text:
            text = f"Please analyze the attached file: {self.uploaded_file['name']}"
        
        if not text:
            return
        
        timestamp = datetime.now().strftime("%H:%M")
        
        # Add file info if uploaded
        message_text = text
        if self.uploaded_file:
            message_text = f"📎 {self.uploaded_file['name']}\n\n{text}"
        
        # Add to history
        msg = {
            "sender": "user",
            "text": message_text,
            "timestamp": timestamp
        }
        self.chat_history.append(msg)
        
        # Display message
        self.display_message("user", message_text, timestamp)
        
        # Clear input
        self.input_text.delete("1.0", tk.END)
        
        # Get AI response
        if self.uploaded_file:
            file_info = self.uploaded_file
            self.uploaded_file = None
            self.file_preview_frame.pack_forget()
            self.root.after(500, lambda: self.get_file_analysis_response(file_info, text))
        else:
            self.root.after(500, lambda: self.get_ai_response_async(text))
        
        # Update chat title if first message
        self.update_chat_title(text)
    
    def display_message(self, sender, text, timestamp):
        """Display a message in chat"""
        self.chat_display.config(state=tk.NORMAL)
        
        if sender == "user":
            self.chat_display.insert(tk.END, "You", "user")
        else:
            self.chat_display.insert(tk.END, "JARMISS", "ai")
        
        self.chat_display.insert(tk.END, f" [{timestamp}]", "timestamp")
        self.chat_display.insert(tk.END, f"\n{text}\n\n")
        self.chat_display.see(tk.END)
        self.chat_display.config(state=tk.DISABLED)
    
    def get_file_analysis_response(self, file_info, user_text):
        """Generate AI response for file analysis"""
        filename = file_info['name']
        file_path = file_info['path']
        ext = os.path.splitext(filename)[1].lower()
        
        # Try to read file content for AI analysis
        file_content = ""
        try:
            if ext in [".txt", ".py", ".js", ".html", ".css", ".cpp", ".java", ".md"]:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    file_content = f.read(10000)  # First 10k chars
        except:
            pass
        
        if self.ai_enabled and self.ai_model and file_content:
            # Create detailed prompt for AI
            prompt = (f"I have uploaded a file named '{filename}'.\n\n"
                     f"File content:\n```\n{file_content}\n```\n\n"
                     f"User's question: {user_text}\n\n"
                     f"Please analyze this file and provide a detailed, helpful response to the user's question. "
                     f"Be specific and reference actual content from the file.")
            self.get_ai_response_async(prompt)
        elif self.ai_enabled and self.ai_model:
            # AI is enabled but couldn't read file content
            prompt = (f"I have uploaded a file named '{filename}' (type: {ext}).\n\n"
                     f"User's question: {user_text}\n\n"
                     f"Please provide helpful guidance about this type of file and how to work with it.")
            self.get_ai_response_async(prompt)
        else:
            # Fallback response
            response = f"I've received your file: {filename}\n\n"
            
            if ext in [".txt", ".py", ".js", ".html", ".css", ".cpp", ".java"]:
                response += ("📄 Text/Code File Analysis:\n"
                            "• File type: Source code/text document\n"
                            "• I can help you understand the structure\n"
                            "• Explain the code functionality\n"
                            "• Suggest improvements or debug issues\n\n")
            elif ext in [".pdf", ".docx", ".doc"]:
                response += ("📑 Document Analysis:\n"
                            "• File type: Document\n"
                            "• I can extract and summarize content\n"
                            "• Find specific information\n"
                            "• Answer questions about the document\n\n")
            elif ext in [".xlsx", ".xls", ".csv"]:
                response += ("📊 Spreadsheet Analysis:\n"
                            "• File type: Data file\n"
                            "• I can analyze data patterns\n"
                            "• Calculate statistics\n"
                            "• Help with data visualization\n\n")
            elif ext in [".png", ".jpg", ".jpeg", ".gif", ".bmp"]:
                response += ("🖼️ Image Analysis:\n"
                            "• File type: Image\n"
                            "• I can describe visual content\n"
                            "• Identify objects and text\n"
                            "• Analyze visual elements\n\n")
            else:
                response += ("📦 File Received:\n"
                            "• I've received your file\n"
                            "• I can provide general guidance\n"
                            "• Ask me specific questions about it\n\n")
            
            response += "\n💡 Tip: Enable AI in settings (⚙️ button) for detailed file analysis!"
            
            self.root.after(0, lambda: self.display_ai_response(response))
    
    def generate_fallback_response(self, message):
        """Generate intelligent fallback response when AI is offline"""
        message_lower = message.lower()
        
        # Greeting responses
        if any(word in message_lower for word in ["hello", "hi", "hey", "greetings"]):
            return "Hello! I'm JARMISS, your personal AI assistant. How can I help you today? 🤖✨\n\n💡 Enable AI in settings (⚙️) for smarter responses!"
        
        # Help responses
        elif any(word in message_lower for word in ["help", "what can you do", "capabilities"]):
            return ("I can assist you with:\n"
                   "• 💬 Answering questions and providing information\n"
                   "• 📁 Analyzing files and documents you upload\n"
                   "• 📸 Processing images you capture or upload\n"
                   "• 🎤 Voice conversations (activate with mic button)\n"
                   "• 📚 Managing your chat history\n\n"
                   "💡 Enable AI in settings (⚙️) for advanced capabilities!")
        
        # AI configuration
        elif "ai" in message_lower and any(word in message_lower for word in ["enable", "activate", "configure", "setup"]):
            return ("To enable AI:\n"
                   "1. Click the ⚙️ settings button in the top right\n"
                   "2. Get your free API key from: https://aistudio.google.com/app/apikey\n"
                   "3. Enter the key and click 'Save & Activate'\n"
                   "4. Enjoy intelligent conversations! 🚀\n\n"
                   "The free tier includes 60 requests per minute.")
        
        # File analysis
        elif "file" in message_lower or "document" in message_lower:
            return "I can analyze various file types including documents, spreadsheets, images, and more. Please use the 📁 button to upload a file, and I'll help you with it!"
        
        # Image analysis
        elif "image" in message_lower or "photo" in message_lower or "picture" in message_lower:
            return "I can analyze images! Use the 📸 button to capture a photo or upload one with 📁, and I'll describe what I see and answer questions about it."
        
        # Voice chat
        elif "voice" in message_lower or "speak" in message_lower:
            return "You can activate voice chat by clicking the 🎤 microphone button. I'll listen to your voice and respond accordingly!"
        
        # Time/date
        elif "time" in message_lower or "date" in message_lower:
            now = datetime.now()
            return f"⏰ Current date and time: {now.strftime('%A, %B %d, %Y at %H:%M:%S')}"
        
        # About JARMISS
        elif "who are you" in message_lower or "what are you" in message_lower:
            return ("I am JARMISS - Just A Rather Mighty Intelligent System Service. 🤖💖\n\n"
                   "I'm your personal AI assistant designed to help you with information, "
                   "file analysis, image processing, and intelligent conversations. "
                   "I'm here to make your digital life easier!\n\n"
                   "ZZZ... BEEP... Always ready to assist! 💫\n\n"
                   "💡 Enable AI in settings (⚙️) for even better responses!")
        
        # Thank you
        elif "thank" in message_lower:
            return "You're welcome! I'm always here to help. Is there anything else you'd like to know? 😊"
        
        # Goodbye
        elif any(word in message_lower for word in ["bye", "goodbye", "see you", "exit"]):
            return "Goodbye! Feel free to return anytime you need assistance. Have a great day! 👋✨"
        
        # Default intelligent response
        else:
            return (f"I understand you're asking about: '{message[:100]}...'\n\n"
                   f"I'm currently running in basic mode. For intelligent, context-aware responses, "
                   f"please enable AI in settings (⚙️ button).\n\n"
                   f"In the meantime, I can still help with:\n"
                   f"• File uploads and basic analysis\n"
                   f"• Image processing\n"
                   f"• Chat management\n"
                   f"• General information\n\n"
                   f"ZZZ... BEEP... Ready to help! 🤖")
    
    def save_current_chat(self):
        """Save current chat to user's data"""
        if self.current_user and self.current_chat_id:
            chat = next((c for c in self.users_db[self.current_user]["chats"] 
                        if c["id"] == self.current_chat_id), None)
            if chat:
                chat["messages"] = self.chat_history
                self.save_users_db()  # Persist to disk
    
    def update_chat_title(self, first_message):
        """Update chat title based on first message"""
        if self.current_user and self.current_chat_id:
            chat = next((c for c in self.users_db[self.current_user]["chats"] 
                        if c["id"] == self.current_chat_id), None)
            if chat and chat["title"] == "New Chat":
                # Use first 30 chars of message as title
                chat["title"] = first_message[:30] + ("..." if len(first_message) > 30 else "")
                self.update_chat_list()
    
    def search_chats(self):
        """Search through chat history with enhanced display"""
        query = self.search_entry.get().lower()
        if not query:
            self.update_chat_list()
            return
        
        # Clear current list
        for widget in self.chat_scrollable.winfo_children():
            widget.destroy()
        
        # Search header
        tk.Label(
            self.chat_scrollable,
            text=f"🔍 Search results for: '{query}'",
            font=("Arial", 9, "bold"),
            bg="#16213e",
            fg="#ffaa00",
            anchor="w",
            padx=10,
            pady=8
        ).pack(fill=tk.X, pady=(5, 10))
        
        # Filter and display matching chats
        if self.current_user:
            chats = self.users_db[self.current_user]["chats"]
            pinned_chat_ids = self.users_db[self.current_user].get("pinned_chats", [])
            found_chats = []
            
            for chat in chats:
                # Search in title and messages
                if (query in chat["title"].lower() or 
                    any(query in msg["text"].lower() for msg in chat["messages"])):
                    found_chats.append(chat)
            
            if found_chats:
                for chat in reversed(found_chats):
                    is_pinned = chat["id"] in pinned_chat_ids
                    self.create_chat_button(chat, is_pinned=is_pinned)
            else:
                tk.Label(
                    self.chat_scrollable,
                    text="No chats found matching your search",
                    font=("Arial", 10, "italic"),
                    bg="#16213e",
                    fg="#888888",
                    pady=20
                ).pack(fill=tk.X)
    
    def upload_file(self):
        """Handle file upload"""
        file_path = filedialog.askopenfilename(
            title="Select a file",
            filetypes=[
                ("All Files", "*.*"),
                ("Text Files", "*.txt"),
                ("PDF Files", "*.pdf"),
                ("Word Documents", "*.docx"),
                ("Excel Files", "*.xlsx"),
                ("Images", "*.png *.jpg *.jpeg *.gif"),
                ("Code Files", "*.py *.js *.java *.cpp *.html *.css")
            ]
        )
        
        if file_path:
            filename = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            
            # Store file info
            self.uploaded_file = {
                'name': filename,
                'path': file_path,
                'size': file_size
            }
            
            # Show file preview
            self.file_preview_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
            
            for widget in self.file_preview_frame.winfo_children():
                widget.destroy()
            
            preview_content = tk.Frame(self.file_preview_frame, bg="#1a1a2e", relief=tk.RAISED, bd=2)
            preview_content.pack(fill=tk.X, padx=5, pady=5)
            
            tk.Label(preview_content, text="📎 File Ready:", font=("Arial", 10, "bold"), 
                    fg="#00ff00", bg="#1a1a2e").pack(side=tk.LEFT, padx=8, pady=5)
            tk.Label(preview_content, text=f"{filename} ({file_size:,} bytes)", 
                    font=("Arial", 9), fg="#ffffff", bg="#1a1a2e").pack(side=tk.LEFT, padx=5, pady=5)
            
            tk.Button(preview_content, text="✕ Remove", font=("Arial", 9, "bold"), 
                     bg="#ff6666", fg="#ffffff", 
                     command=self.remove_uploaded_file, 
                     cursor="hand2", relief=tk.FLAT, padx=8, pady=3).pack(side=tk.RIGHT, padx=8, pady=5)
            
            tk.Label(preview_content, text="Type your message and click Send →", 
                    font=("Arial", 9, "italic"), fg="#ffaa00", bg="#1a1a2e").pack(side=tk.RIGHT, padx=10)
    
    def remove_uploaded_file(self):
        """Remove the uploaded file"""
        self.uploaded_file = None
        self.file_preview_frame.pack_forget()
    
    def capture_photo(self):
        """Handle photo capture"""
        # Allow selecting an image file for now
        file_path = filedialog.askopenfilename(
            title="Select an image (or capture from camera)",
            filetypes=[
                ("Images", "*.png *.jpg *.jpeg *.gif *.bmp"),
                ("All Files", "*.*")
            ]
        )
        
        if file_path:
            filename = os.path.basename(file_path)
            file_size = os.path.getsize(file_path)
            
            # Store file info
            self.uploaded_file = {
                'name': filename,
                'path': file_path,
                'size': file_size
            }
            
            # Show file preview
            self.file_preview_frame.pack(side=tk.TOP, fill=tk.X, pady=5)
            
            for widget in self.file_preview_frame.winfo_children():
                widget.destroy()
            
            preview_content = tk.Frame(self.file_preview_frame, bg="#1a1a2e", relief=tk.RAISED, bd=2)
            preview_content.pack(fill=tk.X, padx=5, pady=5)
            
            tk.Label(preview_content, text="📸 Photo Ready:", font=("Arial", 10, "bold"), 
                    fg="#00ff00", bg="#1a1a2e").pack(side=tk.LEFT, padx=8, pady=5)
            tk.Label(preview_content, text=f"{filename}", 
                    font=("Arial", 9), fg="#ffffff", bg="#1a1a2e").pack(side=tk.LEFT, padx=5, pady=5)
            
            tk.Button(preview_content, text="✕ Remove", font=("Arial", 9, "bold"), 
                     bg="#ff6666", fg="#ffffff", 
                     command=self.remove_uploaded_file, 
                     cursor="hand2", relief=tk.FLAT, padx=8, pady=3).pack(side=tk.RIGHT, padx=8, pady=5)
            
            tk.Label(preview_content, text="Type your message and click Send →", 
                    font=("Arial", 9, "italic"), fg="#ffaa00", bg="#1a1a2e").pack(side=tk.RIGHT, padx=10)
    
    def toggle_voice(self):
        """Toggle voice chat"""
        self.voice_enabled = not self.voice_enabled
        
        if self.voice_enabled:
            self.voice_btn.config(bg="#00ff00", fg="#000000")
            messagebox.showinfo("Voice Chat Activated", 
                              "🎤 Voice chat activated!\n\n"
                              "ZZZ... BEEP... LISTENING... ZZZ...\n\n"
                              "In a full implementation:\n"
                              "• Speak into your microphone\n"
                              "• I'll transcribe and respond\n"
                              "• I can speak responses back\n"
                              "• Natural conversation flow\n\n"
                              "Click mic again to deactivate.")
        else:
            self.voice_btn.config(bg="#1a1a2e", fg="#00ffff")
    
    def show_profile(self):
        """Show profile panel"""
        profile_window = tk.Toplevel(self.root)
        profile_window.title("Profile Settings")
        profile_window.geometry("600x750")
        profile_window.configure(bg="#16213e")
        profile_window.transient(self.root)
        profile_window.grab_set()
        
        # Header with avatar
        header_frame = tk.Frame(profile_window, bg="#1a1a2e", relief=tk.RAISED, bd=2)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        user = self.users_db[self.current_user]
        avatar = user.get("avatar", "👤")
        
        # Large avatar display
        tk.Label(header_frame, text=avatar, font=("Arial", 80), 
                bg="#1a1a2e").pack(pady=20)
        
        tk.Label(header_frame, text="👤 Profile Settings", font=("Arial", 24, "bold"), 
                fg="#ff69b4", bg="#1a1a2e").pack(pady=(0, 10))
        
        tk.Label(header_frame, text=user["username"], font=("Arial", 16), 
                fg="#00ffff", bg="#1a1a2e").pack(pady=(0, 20))
        
        # Scrollable content
        content_canvas = tk.Canvas(profile_window, bg="#16213e", highlightthickness=0)
        content_scrollbar = tk.Scrollbar(profile_window, orient="vertical", command=content_canvas.yview)
        content_frame = tk.Frame(content_canvas, bg="#16213e")
        
        content_frame.bind(
            "<Configure>",
            lambda e: content_canvas.configure(scrollregion=content_canvas.bbox("all"))
        )
        
        content_canvas.create_window((0, 0), window=content_frame, anchor="nw")
        content_canvas.configure(yscrollcommand=content_scrollbar.set)
        
        content_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20)
        content_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Account Information Section
        info_section = tk.LabelFrame(content_frame, text="📋 Account Information", 
                                     font=("Arial", 14, "bold"), fg="#00ffff", 
                                     bg="#1a1a2e", relief=tk.RAISED, bd=2)
        info_section.pack(fill=tk.X, pady=10, padx=10)
        
        fields = [
            ("📧 Email", self.current_user),
            ("👤 Username", user["username"]),
            ("📱 Phone", user.get("phone", "") or "Not set"),
            ("🎨 Avatar", avatar),
            ("💬 Total Chats", str(len(user["chats"])))
        ]
        
        for label, value in fields:
            row = tk.Frame(info_section, bg="#1a1a2e")
            row.pack(fill=tk.X, pady=8, padx=20)
            
            tk.Label(row, text=f"{label}:", font=("Arial", 12, "bold"), 
                    fg="#00ffff", bg="#1a1a2e", width=18, anchor="w").pack(side=tk.LEFT)
            tk.Label(row, text=value, font=("Arial", 12), 
                    fg="#ffffff", bg="#1a1a2e", anchor="w").pack(side=tk.LEFT, padx=10)
        
        # Preferences Section
        pref_section = tk.LabelFrame(content_frame, text="⚙️ Preferences", 
                                     font=("Arial", 14, "bold"), fg="#00ffff", 
                                     bg="#1a1a2e", relief=tk.RAISED, bd=2)
        pref_section.pack(fill=tk.X, pady=10, padx=10)
        
        # Theme preference
        theme_frame = tk.Frame(pref_section, bg="#1a1a2e")
        theme_frame.pack(fill=tk.X, pady=8, padx=20)
        tk.Label(theme_frame, text="🎨 Theme:", font=("Arial", 12, "bold"), 
                fg="#00ffff", bg="#1a1a2e", width=18, anchor="w").pack(side=tk.LEFT)
        tk.Label(theme_frame, text=user.get("theme", "Dark"), font=("Arial", 12), 
                fg="#ffffff", bg="#1a1a2e", anchor="w").pack(side=tk.LEFT, padx=10)
        
        # AI Status
        ai_frame = tk.Frame(pref_section, bg="#1a1a2e")
        ai_frame.pack(fill=tk.X, pady=8, padx=20)
        tk.Label(ai_frame, text="🤖 AI Status:", font=("Arial", 12, "bold"), 
                fg="#00ffff", bg="#1a1a2e", width=18, anchor="w").pack(side=tk.LEFT)
        tk.Label(ai_frame, text="Active" if self.ai_enabled else "Offline", 
                font=("Arial", 12), fg="#00ff00" if self.ai_enabled else "#ff6666", 
                bg="#1a1a2e", anchor="w").pack(side=tk.LEFT, padx=10)
        
        # Statistics Section
        stats_section = tk.LabelFrame(content_frame, text="📊 Statistics", 
                                     font=("Arial", 14, "bold"), fg="#00ffff", 
                                     bg="#1a1a2e", relief=tk.RAISED, bd=2)
        stats_section.pack(fill=tk.X, pady=10, padx=10)
        
        # Calculate total messages
        total_messages = sum(len(chat["messages"]) for chat in user["chats"])
        
        stats = [
            ("💬 Total Messages", str(total_messages)),
            ("📝 Active Chats", str(len(user["chats"]))),
            ("⏱️ Member Since", "Demo Account")
        ]
        
        for label, value in stats:
            row = tk.Frame(stats_section, bg="#1a1a2e")
            row.pack(fill=tk.X, pady=8, padx=20)
            
            tk.Label(row, text=f"{label}:", font=("Arial", 12, "bold"), 
                    fg="#00ffff", bg="#1a1a2e", width=18, anchor="w").pack(side=tk.LEFT)
            tk.Label(row, text=value, font=("Arial", 12), 
                    fg="#ffffff", bg="#1a1a2e", anchor="w").pack(side=tk.LEFT, padx=10)
        
        # Buttons at bottom
        btn_frame = tk.Frame(profile_window, bg="#16213e")
        btn_frame.pack(pady=20, side=tk.BOTTOM)
        
        tk.Button(btn_frame, text="✏️ Edit Profile", font=("Arial", 12, "bold"), 
                 bg="#00ffff", fg="#000000", command=lambda: self.edit_profile(profile_window), 
                 cursor="hand2", padx=20, pady=10).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="🗑️ Clear Chat History", font=("Arial", 12, "bold"), 
                 bg="#ffaa00", fg="#000000", command=lambda: self.clear_chat_history(profile_window), 
                 cursor="hand2", padx=20, pady=10).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="❌ Close", font=("Arial", 12, "bold"), 
                 bg="#ff6666", fg="#ffffff", command=profile_window.destroy, 
                 cursor="hand2", padx=20, pady=10).pack(side=tk.LEFT, padx=5)
    
    def clear_chat_history(self, parent_window):
        """Clear all chat history"""
        if messagebox.askyesno("Clear Chat History", 
                              "Are you sure you want to delete all your chats?\nThis action cannot be undone!", 
                              parent=parent_window):
            self.users_db[self.current_user]["chats"] = []
            self.users_db[self.current_user]["pinned_chats"] = []
            self.save_users_db()
            self.current_chat_id = None
            self.chat_history = []
            messagebox.showinfo("Success", "All chat history has been cleared!", parent=parent_window)
            parent_window.destroy()
            # Refresh dashboard
            if hasattr(self, 'dashboard_frame'):
                self.dashboard_frame.destroy()
                self.show_dashboard()
    
    def edit_profile(self, parent_window):
        """Edit profile information"""
        edit_window = tk.Toplevel(parent_window)
        edit_window.title("Edit Profile")
        edit_window.geometry("550x600")
        edit_window.configure(bg="#16213e")
        edit_window.transient(parent_window)
        edit_window.grab_set()
        
        tk.Label(edit_window, text="✏️ Edit Profile", font=("Arial", 20, "bold"), 
                fg="#ff69b4", bg="#16213e").pack(pady=20)
        
        user = self.users_db[self.current_user]
        
        # Scrollable content
        scroll_canvas = tk.Canvas(edit_window, bg="#16213e", highlightthickness=0, height=380)
        scroll_bar = tk.Scrollbar(edit_window, orient="vertical", command=scroll_canvas.yview)
        fields_container = tk.Frame(scroll_canvas, bg="#16213e")
        
        fields_container.bind(
            "<Configure>",
            lambda e: scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))
        )
        
        scroll_canvas.create_window((0, 0), window=fields_container, anchor="nw")
        scroll_canvas.configure(yscrollcommand=scroll_bar.set)
        
        scroll_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=30)
        scroll_bar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Avatar Selection Section
        avatar_section = tk.LabelFrame(fields_container, text="🎨 Choose Avatar", 
                                       font=("Arial", 12, "bold"), fg="#00ffff", 
                                       bg="#1a1a2e", relief=tk.RAISED, bd=2)
        avatar_section.pack(fill=tk.X, pady=10, padx=10)
        
        # Current avatar display
        current_avatar_frame = tk.Frame(avatar_section, bg="#1a1a2e")
        current_avatar_frame.pack(pady=10)
        
        tk.Label(current_avatar_frame, text="Current Avatar:", font=("Arial", 10), 
                fg="#ffffff", bg="#1a1a2e").pack(side=tk.LEFT, padx=5)
        
        selected_avatar = tk.StringVar(value=user.get("avatar", "👤"))
        avatar_display = tk.Label(current_avatar_frame, text=selected_avatar.get(), 
                                  font=("Arial", 40), bg="#1a1a2e")
        avatar_display.pack(side=tk.LEFT, padx=10)
        
        # Avatar grid
        avatar_grid = tk.Frame(avatar_section, bg="#1a1a2e")
        avatar_grid.pack(pady=10, padx=10)
        
        def select_avatar(avatar):
            selected_avatar.set(avatar)
            avatar_display.config(text=avatar)
        
        for i, avatar in enumerate(self.avatars):
            btn = tk.Button(avatar_grid, text=avatar, font=("Arial", 24), 
                          bg="#16213e" if avatar != selected_avatar.get() else "#00ffff",
                          fg="#ffffff", command=lambda a=avatar: select_avatar(a),
                          cursor="hand2", relief=tk.RAISED, bd=2,
                          width=2, height=1)
            btn.grid(row=i//5, column=i%5, padx=5, pady=5)
        
        # Basic Info Section
        basic_section = tk.LabelFrame(fields_container, text="📝 Basic Information", 
                                      font=("Arial", 12, "bold"), fg="#00ffff", 
                                      bg="#1a1a2e", relief=tk.RAISED, bd=2)
        basic_section.pack(fill=tk.X, pady=10, padx=10)
        
        # Username
        tk.Label(basic_section, text="Username:", font=("Arial", 11, "bold"), 
                fg="#ffffff", bg="#1a1a2e").pack(pady=(10, 5), padx=20, anchor="w")
        edit_username = tk.Entry(basic_section, font=("Arial", 11), width=40, 
                                bg="#16213e", fg="#ffffff", insertbackground="#ffffff")
        edit_username.insert(0, user["username"])
        edit_username.pack(pady=5, padx=20)
        
        # Phone
        tk.Label(basic_section, text="Phone:", font=("Arial", 11, "bold"), 
                fg="#ffffff", bg="#1a1a2e").pack(pady=(10, 5), padx=20, anchor="w")
        edit_phone = tk.Entry(basic_section, font=("Arial", 11), width=40, 
                             bg="#16213e", fg="#ffffff", insertbackground="#ffffff")
        edit_phone.insert(0, user.get("phone", ""))
        edit_phone.pack(pady=(5, 15), padx=20)
        
        def save_profile_changes():
            """Save the profile changes"""
            new_username = edit_username.get().strip()
            new_phone = edit_phone.get().strip()
            new_avatar = selected_avatar.get()
            
            # Validation
            if not new_username:
                messagebox.showerror("Error", "Username cannot be empty", parent=edit_window)
                return
            
            # Update user data
            user["username"] = new_username
            user["phone"] = new_phone
            user["avatar"] = new_avatar
            self.save_users_db()
            
            messagebox.showinfo("Success", "Profile updated successfully!", parent=edit_window)
            edit_window.destroy()
            parent_window.destroy()
            
            # Refresh dashboard to show new username and avatar
            if hasattr(self, 'dashboard_frame'):
                self.dashboard_frame.destroy()
                self.show_dashboard()
        
        # Buttons at bottom
        btn_frame = tk.Frame(edit_window, bg="#16213e")
        btn_frame.pack(pady=20, side=tk.BOTTOM)
        
        tk.Button(btn_frame, text="💾 Save Changes", font=("Arial", 12, "bold"), 
                 bg="#00ff00", fg="#000000", command=save_profile_changes, 
                 cursor="hand2", padx=25, pady=10).pack(side=tk.LEFT, padx=5)
        
        tk.Button(btn_frame, text="❌ Cancel", font=("Arial", 12, "bold"), 
                 bg="#ff6666", fg="#ffffff", command=edit_window.destroy, 
                 cursor="hand2", padx=25, pady=10).pack(side=tk.LEFT, padx=5)
    
    def logout(self):
        """Handle logout"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.current_user = None
            self.current_chat_id = None
            self.chat_history = []
            self.uploaded_file = None
            self.ai_enabled = False
            self.ai_model = None
            self.api_key = ""
            self.dashboard_frame.destroy()
            self.show_auth_screen()

def main():
    root = tk.Tk()
    app = JarmissAI(root)
    root.mainloop()

if __name__ == "__main__":
    main()