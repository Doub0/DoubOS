"""
DoubOS - Fun and Easter Egg Commands
Because every good OS needs some fun!
"""

from commands import Command, CommandContext
from typing import List
import random
from datetime import datetime


class CowsayCommand(Command):
    """ASCII cow says things"""
    
    def __init__(self):
        super().__init__("cowsay", "🐮 Make a cow say something", "cowsay <message>")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        message = " ".join(args) if args else "Moo!"
        msg_len = len(message)
        
        return f"""
 {"_" * (msg_len + 2)}
< {message} >
 {"‾" * (msg_len + 2)}
        \\   ^__^
         \\  (oo)\\_______
            (__)\\       )\\/\\
                ||----w |
                ||     ||
"""


class FortuneCommand(Command):
    """Display random fortune"""
    
    def __init__(self):
        super().__init__("fortune", "🔮 Display a random fortune", "fortune")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        fortunes = [
            "You will write bug-free code today... or will you?",
            "A recursive function is calling you.",
            "Beware of off-by-one errors.",
            "Your next commit will break production.",
            "The answer is 42.",
            "sudo make me a sandwich",
            "There is no place like 127.0.0.1",
            "To err is human, to really screw up requires root access.",
            "All your base are belong to us.",
            "The cloud is just someone else's computer.",
            "It works on my machine ¯\\_(ツ)_/¯",
            "Have you tried turning it off and on again?",
            "Coffee not found. Programmer is sleeping.",
            "Debugging: Being the detective in a crime movie where you're also the murderer.",
            "There are only 10 types of people in the world: those who understand binary and those who don't."
        ]
        return random.choice(fortunes)


class HackerCommand(Command):
    """Become a 1337 h4x0r"""
    
    def __init__(self):
        super().__init__("hacker", "👨‍💻 Enter hacker mode", "hacker")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        return """
██╗  ██╗ █████╗  ██████╗██╗  ██╗███████╗██████╗ 
██║  ██║██╔══██╗██╔════╝██║ ██╔╝██╔════╝██╔══██╗
███████║███████║██║     █████╔╝ █████╗  ██████╔╝
██╔══██║██╔══██║██║     ██╔═██╗ ██╔══╝  ██╔══██╗
██║  ██║██║  ██║╚██████╗██║  ██╗███████╗██║  ██║
╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝

[INITIALIZING HACK MODE...]
[Bypassing firewall...] ✓
[Cracking encryption...] ✓  
[Accessing mainframe...] ✓
[Downloading database...] ✓

🎉 You are now 1337! 🎉
"""


class MatrixCommand(Command):
    """Enter the Matrix"""
    
    def __init__(self):
        super().__init__("matrix", "🟢 Enter the Matrix", "matrix")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        return """
Wake up, Neo...
The Matrix has you...
Follow the white rabbit.

Knock, knock, Neo.

⢀⣠⣾⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⠀⣠⣤⣶⣶
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠀⠀⠀⢰⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣧⣀⣀⣾⣿⣿⣿⣿
⣿⣿⣿⣿⣿⡏⠉⠛⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⣿
⣿⣿⣿⣿⣿⣿⠀⠀⠀⠈⠛⢿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠛⠉⠁⠀⣿
⣿⣿⣿⣿⣿⣿⣧⡀⠀⠀⠀⠀⠙⠿⠿⠿⠻⠿⠿⠟⠿⠛⠉⠀⠀⠀⠀⠀⣸⣿
⣿⣿⣿⣿⣿⣿⣿⣷⣄⠀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⠏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠠⣴⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⡟⠀⠀⢰⣹⡆⠀⠀⠀⠀⠀⠀⣭⣷⠀⠀⠀⠸⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⠃⠀⠀⠈⠉⠀⠀⠤⠄⠀⠀⠀⠉⠁⠀⠀⠀⠀⢿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⢾⣿⣷⠀⠀⠀⠀⡠⠤⢄⠀⠀⠀⠠⣿⣿⣷⠀⢸⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⡀⠉⠀⠀⠀⠀⠀⢄⠀⢀⠀⠀⠀⠀⠉⠉⠁⠀⠀⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣧⠀⠀⠀⠀⠀⠀⠀⠈⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⣿⣿
"""


class AsciiArtCommand(Command):
    """Display DoubOS ASCII art"""
    
    def __init__(self):
        super().__init__("ascii", "🎨 Display DoubOS ASCII art", "ascii")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        return """
██████╗  ██████╗ ██╗   ██╗██████╗  ██████╗ ███████╗
██╔══██╗██╔═══██╗██║   ██║██╔══██╗██╔═══██╗██╔════╝
██║  ██║██║   ██║██║   ██║██████╔╝██║   ██║███████╗
██║  ██║██║   ██║██║   ██║██╔══██╗██║   ██║╚════██║
██████╔╝╚██████╔╝╚██████╔╝██████╔╝╚██████╔╝███████║
╚═════╝  ╚═════╝  ╚═════╝ ╚═════╝  ╚═════╝ ╚══════╝

         A Fully Fledged Operating System
              💾 Virtual Edition 💾
"""


class SnakeCommand(Command):
    """Display a snake"""
    
    def __init__(self):
        super().__init__("snake", "🐍 Display a snake", "snake")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        return r"""
              /^\/^\
            _|__|  O|
   \/     /~     \\_/ \\
    \\____|__________/  \\
           \\_______      \\
                   `\\     \\                 \\
                     |     |                  \\
                    /      /                    \\
                   /     /                       \\
                 /      /                         \\ \\
                /     /                            \\  \\
              /     /             _----_            \\   \\
             /     /           _-~      ~-_         |   |
            (      (        _-~    _--_    ~-_     _/   |
             \\      ~-____-~    _-~    ~-_    ~-_-~    /
               ~-_           _-~          ~-_       _-~
                  ~--______-~                ~-___-~
"""


class BannerCommand(Command):
    """Create text banners"""
    
    def __init__(self):
        super().__init__("banner", "📢 Create a text banner", "banner <text>")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        text = " ".join(args) if args else "DoubOS"
        border = "=" * (len(text) + 4)
        return f"""
{border}
  {text.upper()}
{border}
"""


class JokCommand(Command):
    """Tell a programming joke"""
    
    def __init__(self):
        super().__init__("joke", "😄 Tell a programming joke", "joke")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        jokes = [
            "Why do programmers prefer dark mode?\nBecause light attracts bugs! 🐛",
            "A SQL query walks into a bar, walks up to two tables and asks...\n'Can I join you?'",
            "How many programmers does it take to change a light bulb?\nNone. That's a hardware problem.",
            "Why do Java developers wear glasses?\nBecause they can't C#!",
            "What's the object-oriented way to become wealthy?\nInheritance.",
            "Why did the programmer quit his job?\nBecause he didn't get arrays!",
            "What do you call a programmer from Finland?\nNils.",
            "There are 10 types of people:\nThose who understand binary and those who don't.",
            "Why do programmers always mix up Halloween and Christmas?\nBecause Oct 31 == Dec 25!",
            "Programming is 10% writing code and 90% understanding why it's not working."
        ]
        return random.choice(jokes)


class QuoteCommand(Command):
    """Display an inspiring quote"""
    
    def __init__(self):
        super().__init__("quote", "💭 Display an inspiring quote", "quote")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        quotes = [
            '"Talk is cheap. Show me the code." - Linus Torvalds',
            '"Code is like humor. When you have to explain it, it\'s bad." - Cory House',
            '"First, solve the problem. Then, write the code." - John Johnson',
            '"Any fool can write code that a computer can understand. Good programmers write code that humans can understand." - Martin Fowler',
            '"The best error message is the one that never shows up." - Thomas Fuchs',
            '"Simplicity is the soul of efficiency." - Austin Freeman',
            '"Make it work, make it right, make it fast." - Kent Beck',
            '"Code never lies, comments sometimes do." - Ron Jeffries',
            '"The most disastrous thing that you can ever learn is your first programming language." - Alan Kay',
            '"Programs must be written for people to read, and only incidentally for machines to execute." - Harold Abelson'
        ]
        return random.choice(quotes)


class DiceCommand(Command):
    """Roll dice"""
    
    def __init__(self):
        super().__init__("dice", "🎲 Roll dice", "dice [sides]")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        sides = 6
        if args:
            try:
                sides = int(args[0])
            except:
                return "dice: invalid number of sides"
                
        roll = random.randint(1, sides)
        return f"🎲 Rolling d{sides}... You got: {roll}"


class FlipCommand(Command):
    """Flip a coin"""
    
    def __init__(self):
        super().__init__("flip", "🪙 Flip a coin", "flip")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        result = random.choice(["Heads", "Tails"])
        return f"🪙 Flipping coin... {result}!"


class WeatherCommand(Command):
    """Check the weather"""
    
    def __init__(self):
        super().__init__("weather", "🌤️ Check the weather", "weather [city]")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        city = " ".join(args) if args else "Virtual City"
        temp = random.randint(-10, 35)
        conditions = ["Sunny ☀️", "Cloudy ☁️", "Rainy 🌧️", "Stormy ⛈️", "Snowy ❄️", "Foggy 🌫️"]
        condition = random.choice(conditions)
        
        return f"""Weather in {city}:
Temperature: {temp}°C
Conditions: {condition}
Humidity: {random.randint(30, 90)}%
Wind: {random.randint(5, 30)} km/h"""


class ColorCommand(Command):
    """Display color palette"""
    
    def __init__(self):
        super().__init__("colors", "🎨 Display color palette", "colors")
        
    def execute(self, args: List[str], context: CommandContext) -> str:
        return """DoubOS Color Palette:

\033[90m█ \033[0mBlack     \033[91m█ \033[0mRed       \033[92m█ \033[0mGreen     \033[93m█ \033[0mYellow
\033[94m█ \033[0mBlue      \033[95m█ \033[0mMagenta   \033[96m█ \033[0mCyan      \033[97m█ \033[0mWhite

\033[1m█ \033[0mBold      \033[4m█ \033[0mUnderline \033[7m█ \033[0mReverse   \033[2m█ \033[0mDim
"""


# Function to register all fun commands
def register_fun_commands(processor):
    """Register all fun commands with the processor"""
    processor.register_command(CowsayCommand())
    processor.register_command(FortuneCommand())
    processor.register_command(HackerCommand())
    processor.register_command(MatrixCommand())
    processor.register_command(AsciiArtCommand())
    processor.register_command(SnakeCommand())
    processor.register_command(BannerCommand())
    processor.register_command(JokCommand())
    processor.register_command(QuoteCommand())
    processor.register_command(DiceCommand())
    processor.register_command(FlipCommand())
    processor.register_command(WeatherCommand())
    processor.register_command(ColorCommand())
