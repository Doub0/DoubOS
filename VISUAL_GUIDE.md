# 🎮 DoubOS - Visual Quick Start Guide

## Step-by-Step: Getting Started with DoubOS

---

## 🚀 STEP 1: Launch DoubOS

### Option A: Use the Launcher (Easiest)
```bash
cd DoubOS
python launcher.py
```

You'll see:
```
┌────────────────────────────────┐
│   🖥️  DoubOS Launcher         │
│                                │
│  Advanced Desktop OS           │
│                                │
│  ┌──────────────────────────┐ │
│  │ 🔐 Login with credentials│ │
│  ├──────────────────────────┤ │
│  │ ⚡ Quick test (auto-login)│ │
│  ├──────────────────────────┤ │
│  │ 🧪 Run comprehensive test│ │
│  ├──────────────────────────┤ │
│  │ ❌ Exit                  │ │
│  └──────────────────────────┘ │
│                                │
│  Choose how to start DoubOS    │
└────────────────────────────────┘
```

### Option B: Direct Command
```bash
# For first time or testing
python doubos_test.py
```

---

## 🔐 STEP 2: Login Screen (if using full version)

You'll see:
```
┌─────────────────────────────────────────────┐
│                                             │
│                 DoubOS                      │
│         Your Advanced Desktop OS            │
│                                             │
│  ┌─────────────────────────────────────┐   │
│  │ 👤 Username:  _______________       │   │
│  │                                     │   │
│  │ 🔒 Password:  _______________       │   │
│  │                                     │   │
│  │    [ Login ]  [ Create Account ]   │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  Default: admin / admin123                 │
└─────────────────────────────────────────────┘
```

**Enter:**
- Username: `admin`
- Password: `admin123`
- Click **Login**

---

## 🖥️ STEP 3: Desktop Environment

After login, you'll see the full desktop:

```
┌───────────────────────────────────────────────────────────────┐
│  DoubOS Desktop                                     × □ ─     │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│  💻        📁        ⚙️        📝        🧮        🎮          │
│ Terminal  Files   Settings  Editor    Calc     Games         │
│                                                               │
│                                                               │
│                         DoubOS                                │
│                  Desktop Environment                          │
│                                                               │
│                                                               │
│                                                               │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│ ⊞ START  🌐 📧 🎵 🖼️           👤 admin  🔊 📶 🔋  ⏰ 2:30 PM│
└───────────────────────────────────────────────────────────────┘
```

---

## 💻 STEP 4: Launch Your First App - Terminal

### Click the 💻 Terminal icon on desktop

You'll see a window open INSIDE the desktop:

```
┌───────────────────────────────────────────────────────────────┐
│  DoubOS Desktop                                               │
├───────────────────────────────────────────────────────────────┤
│  💻  📁  ⚙️  📝  🧮  🎮                                         │
│                                                               │
│  ┌────────────────────────────────────────┐                  │
│  │ Terminal 💻                      ✕ □ − │                  │
│  ├────────────────────────────────────────┤                  │
│  │ DoubOS Terminal v1.0                   │                  │
│  │ Type 'help' for commands               │                  │
│  │                                        │                  │
│  │ $ ls                                   │                  │
│  │ 📁 Documents  📁 Downloads             │                  │
│  │ 📁 Pictures   📁 Projects              │                  │
│  │                                        │                  │
│  │ $ _                                    │                  │
│  └────────────────────────────────────────┘                  │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│ ⊞ START  🌐 📧 🎵 🖼️           👤 admin  🔊 📶 🔋  ⏰ 2:30 PM│
└───────────────────────────────────────────────────────────────┘
```

### Try some commands:
```bash
$ help          # See all commands
$ ls            # List files
$ cowsay hello  # Fun ASCII cow
$ fortune       # Random quote
$ matrix        # Matrix effect
$ clear         # Clear screen
```

---

## 🎮 STEP 5: Play Croptopia Game

### Click the 🎮 Games icon

Games Menu opens:
```
┌────────────────────────────────────────┐
│ Games 🎮                         ✕ □ − │
├────────────────────────────────────────┤
│        🎮 Games Library                │
│                                        │
│  ┌──────────────────────────────────┐ │
│  │ 🌾 Croptopia                     │ │
│  │ Farming simulation - plant,      │ │
│  │ water, and harvest crops         │ │
│  │                  [ ▶ Play Game ] │ │
│  └──────────────────────────────────┘ │
│                                        │
│  ┌──────────────────────────────────┐ │
│  │ 🎮 Coming Soon                   │ │
│  │ More games will be added soon!   │ │
│  └──────────────────────────────────┘ │
└────────────────────────────────────────┘
```

### Click **▶ Play Game** button

Croptopia opens in a new window:
```
┌────────────────────────────────────────────┐
│ Croptopia 🌾                         ✕ □ − │
├────────────────────────────────────────────┤
│  Day: 1           Money: $100              │
├────────────────────────────────────────────┤
│  ┌────┬────┬────┬────┬────┬────┐          │
│  │    │    │    │    │    │    │          │
│  ├────┼────┼────┼────┼────┼────┤          │
│  │    │    │🍎 │    │    │    │          │
│  ├────┼────┼────┼────┼────┼────┤          │
│  │    │🥕 │    │    │    │    │          │
│  ├────┼────┼────┼────┼────┼────┤          │
│  │    │    │    │🌾 │    │    │          │
│  ├────┼────┼────┼────┼────┼────┤          │
│  │    │    │    │    │    │    │          │
│  └────┴────┴────┴────┴────┴────┘          │
│                                            │
│  Crops:  [🍎 Apple] [🥕 Carrot] [🌾 Wheat]│
│  Inventory: Apple: 0  Carrot: 0  Wheat: 0 │
│  [💧 Water All]  [🌙 Next Day]            │
└────────────────────────────────────────────┘
```

### How to Play:
1. **Click empty cell** → Plant selected crop ($10)
2. **Click 💧 Water All** → Water all crops
3. **Click 🌙 Next Day** → Advance to next day
4. **Wait 3 days** → Crops mature
5. **Click mature crop** → Harvest and earn money!

---

## 🪟 STEP 6: Multiple Windows

### Try opening several apps at once:

```
┌───────────────────────────────────────────────────────────────┐
│  DoubOS Desktop                                               │
├───────────────────────────────────────────────────────────────┤
│  💻  📁  ⚙️  📝  🧮  🎮                                         │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │Terminal  ✕□−│  │Files     ✕□−│  │Calc      ✕□−│        │
│  ├──────────────┤  ├──────────────┤  ├──────────────┤        │
│  │$ ls          │  │📍/home/admin │  │  7  8  9  ÷ │        │
│  │📁Documents   │  │📁Documents   │  │  4  5  6  × │        │
│  │📁Downloads   │  │📁Downloads   │  │  1  2  3  - │        │
│  │$ _           │  │📄README.md   │  │  0  .  =  + │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│ ⊞ START  🌐 📧 🎵 🖼️           👤 admin  🔊 📶 🔋  ⏰ 2:30 PM│
└───────────────────────────────────────────────────────────────┘
```

**Notice:** All windows are INSIDE the desktop, not separate OS windows!

---

## 🎨 STEP 7: Window Controls

### Each window has three control buttons:

```
┌────────────────────────────────┐
│ App Name              ✕  □  −  │
│                     Close │  │  │
│                        Max│  │  │
│                         Min│  │  │
└────────────────────────────────┘
```

### Try these actions:

**Drag Window:**
- Click and hold title bar
- Move mouse
- Window follows

**Minimize (−):**
- Click yellow "−" button
- Window shrinks to taskbar
- Click again to restore

**Maximize (□):**
- Click blue "□" button
- Window fills screen
- Click again to restore

**Close (✕):**
- Click red "✕" button
- Window closes

---

## 📋 STEP 8: START Menu

### Click the **⊞ START** button

```
┌─────────────────────────────────┐
│  👤 admin                        │
├─────────────────────────────────┤
│  Applications                   │
│                                 │
│  💻 Terminal                    │
│     Command-line interface      │
│                                 │
│  📁 File Explorer               │
│     Browse your files           │
│                                 │
│  📝 Text Editor                 │
│     Edit text files             │
│                                 │
│  🧮 Calculator                  │
│     Basic calculations          │
│                                 │
│  ⚙️ Settings                    │
│     System settings             │
│                                 │
│  🎮 Games                       │
│     Play games                  │
│                                 │
├─────────────────────────────────┤
│  [🔒Lock] [🔄Restart] [⏻Shut]  │
└─────────────────────────────────┘
```

---

## 🎯 STEP 9: Quick Tips

### Desktop Icons
- **Double-click** icons to launch apps
- **6 icons** available for instant access

### Keyboard
- **↑ / ↓** arrows in Terminal for command history
- **Enter** to execute commands

### Multiple Windows
- Open as many windows as you want
- **Click any window** to bring it to front
- Windows automatically stagger position

### Saving
- Everything **auto-saves** when you quit
- Filesystem → `doubos_filesystem.json`
- Users → `doubos_users.json`

---

## 🌟 STEP 10: Explore!

### Try These Commands in Terminal:
```bash
$ cowsay "I love DoubOS"     # ASCII cow
$ fortune                    # Random quote
$ matrix                     # Matrix effect
$ hacker                     # Hacker simulation
$ joke                       # Random joke
$ date                       # Current date/time
$ whoami                     # Current user
$ uptime                     # System uptime
```

### Try These Apps:
- **📁 File Explorer** - Browse virtual filesystem
- **📝 Text Editor** - Create and edit text
- **🧮 Calculator** - Do math calculations
- **⚙️ Settings** - View system settings
- **🎮 Games** - Play Croptopia farming game

### Power Options (from START menu):
- **🔒 Lock** - Return to login screen
- **🔄 Restart** - Restart desktop
- **⏻ Shutdown** - Exit DoubOS (saves state)

---

## ✅ SUCCESS CHECKLIST

After following this guide, you should:

- [x] Launched DoubOS
- [x] Logged in successfully
- [x] Seen the desktop with icons and taskbar
- [x] Opened Terminal window
- [x] Executed some commands
- [x] Played Croptopia game
- [x] Opened multiple windows
- [x] Dragged windows around
- [x] Used window controls (min/max/close)
- [x] Explored START menu
- [x] Understood how the system works

---

## 🎓 Next Steps

### Learn More:
- Read [USER_GUIDE.md](USER_GUIDE.md) for complete manual
- Check [WINDOWS_INFO.md](WINDOWS_INFO.md) for technical details
- See [COMMANDS.md](COMMANDS.md) for all terminal commands

### Experiment:
- Try opening all apps at once
- Play Croptopia until you're rich
- Create new user accounts
- Explore different window layouts

### Customize:
- Check Settings app for themes
- Look at code to understand architecture
- Modify or add new applications

---

## 🐛 Common Issues & Solutions

### "No window appeared"
**Solution:** Windows open INSIDE the desktop frame. Look for them in the desktop area, not as separate OS windows.

### "Can't drag window"
**Solution:** Click and hold the TITLE BAR (top bar with app name), then drag.

### "Terminal commands don't work"
**Solution:** Make sure you're typing in the Terminal app's input field (at the bottom). Press Enter to execute.

### "Croptopia won't start"
**Solution:** Click Games icon → Click "▶ Play Game" button in the games menu.

### "Lost my password"
**Solution:** Check `doubos_users.json` or delete it to reset. Default is admin/admin123.

---

## 🎉 Congratulations!

You now know how to use DoubOS! Enjoy your new operating system! 🚀

**Visual Quick Start Guide Complete ✅**

---

**DoubOS - Your Desktop, Perfected** 🖥️
