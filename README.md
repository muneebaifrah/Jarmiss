# 🌐 JARMISS — AI Personal Assistant

JARMISS (Just A Really Modern Intelligent Smart System) is an advanced AI desktop assistant designed to provide a seamless human-AI interaction experience. It understands voice commands, executes tasks, analyzes uploaded files, and gives smart responses similar to modern AI systems — but locally on your system.

---

## ✨ Features

- ✅ Voice command recognition (Speech-to-Text)
- ✅ Smart text responses (Chat-style AI)
- ✅ User profile storage & authentication
- ✅ File upload & AI-based file analysis
- ✅ On-screen AI animation with intro greeting
- ✅ System camera support *(optional)*
- ✅ Beautiful UI & futuristic interaction feel

---

## 📁 Project Structure

```
JARMISS
 ├─ jarmiss_data/
 │   └─ users.pkl      # Stores registered user data
 ├─ index.py            # Main execution file
 ├─ README.md
 └─ (additional files, assets, animations)
```

---

## 🛠️ Tech Stack

| Category | Tools / Libraries |
|---------|------------------|
| Language | Python |
| Interface | Tkinter / Custom UI animations |
| AI / NLP | Transformers / Speech Recognition |
| Storage | pickle file for user data |
| Speech | `pyttsx3` / STT Libraries |

---

## 🚀 How to Run

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/JARMISS.git

# Go inside folder
cd JARMISS

# Install libraries
pip install -r requirements.txt

# Run the assistant
python index.py
```

---

## 🔐 User Data Handling

User login details are securely stored in:

```
jarmiss_data/users.pkl
```

⚠️ Sensitive files like `.pkl` are ignored using `.gitignore` to protect users' privacy.

---

## 💡 Future Enhancements

- Cloud sync for profiles
- Face recognition login
- Optional LLM API integration (Gemini / GPT)
- Task automation (emails, reminders, web search, etc.)
- Local database instead of pickle

---

## 👩‍💻 Built With

**By Muneeba Ifrah**  
B.Tech CSE | AI & ML Enthusiast  
Using tech for impactful solutions ✅✨

---

## 📬 Contact

For suggestions or collaborations:

📧 Email: muneebaifrah@gmail.com  
🐙 GitHub: https://github.com/muneebaifrah
```

