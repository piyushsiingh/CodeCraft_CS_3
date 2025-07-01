import re
import sys
import time
import string
from enum import Enum, auto
from threading import Thread
from getpass import getpass

class StrengthLevel(Enum):
    VERY_WEAK = auto()
    WEAK = auto()
    MODERATE = auto()
    STRONG = auto()
    VERY_STRONG = auto()

class PasswordAssessor:
    def __init__(self):
        self.common_passwords = self._load_common_passwords()
        self.animation_active = False
        self.current_password = ""
        
    def _load_common_passwords(self):
        # Top 100 most common passwords (sample)
        return {
            '123456', 'password', '123456789', '12345', '12345678',
            'qwerty', '1234567', '111111', '123123', 'abc123',
            'password1', '1234', 'iloveyou', 'admin', 'welcome'
        }
    
    def assess_password(self, password):
        """Assess password strength with animation"""
        if not password:
            return {
                'strength': StrengthLevel.VERY_WEAK,
                'score': 0,
                'feedback': ['Password cannot be empty']
            }
        
        # Check against common passwords
        if password.lower() in self.common_passwords:
            return {
                'strength': StrengthLevel.VERY_WEAK,
                'score': 0,
                'feedback': ['Password is too common']
            }
        
        # Initialize assessment
        length = len(password)
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in string.punctuation for c in password)
        has_repeats = self._check_repeating_chars(password)
        has_sequences = self._check_sequential_chars(password)
        
        # Calculate score (0-100)
        score = 0
        
        # Length (max 40 points)
        if length >= 12:
            score += 40
        elif length >= 8:
            score += 30
        elif length >= 6:
            score += 15
        else:
            score += 5
        
        # Character variety (max 40 points)
        char_types = sum([has_upper, has_lower, has_digit, has_special])
        score += char_types * 10
        
        # Deductions for weaknesses (max -20 points)
        if has_repeats:
            score -= 5
        if has_sequences:
            score -= 5
        if password.isalpha():
            score -= 5
        if password.isnumeric():
            score -= 5
        
        # Ensure score is within bounds
        score = max(0, min(100, score))
        
        # Determine strength level
        if score >= 80:
            strength = StrengthLevel.VERY_STRONG
        elif score >= 60:
            strength = StrengthLevel.STRONG
        elif score >= 40:
            strength = StrengthLevel.MODERATE
        elif score >= 20:
            strength = StrengthLevel.WEAK
        else:
            strength = StrengthLevel.VERY_WEAK
        
        # Generate feedback
        feedback = []
        
        # Positive feedback
        if length >= 12:
            feedback.append("✓ Good password length")
        elif length >= 8:
            feedback.append("✓ Acceptable length")
        else:
            feedback.append("✗ Password is too short")
        
        if has_upper and has_lower:
            feedback.append("✓ Contains both uppercase and lowercase letters")
        elif has_upper or has_lower:
            feedback.append("✓ Contains letters")
        else:
            feedback.append("✗ Missing letters")
        
        if has_digit:
            feedback.append("✓ Contains numbers")
        else:
            feedback.append("✗ Missing numbers")
        
        if has_special:
            feedback.append("✓ Contains special characters")
        else:
            feedback.append("✗ Missing special characters")
        
        # Negative feedback
        if has_repeats:
            feedback.append("✗ Repeating characters reduce strength")
        if has_sequences:
            feedback.append("✗ Sequential characters reduce strength")
        
        return {
            'strength': strength,
            'score': score,
            'feedback': feedback
        }
    
    def _check_repeating_chars(self, password):
        """Check for repeating characters (3 or more)"""
        return bool(re.search(r'(.)\1{2,}', password))
    
    def _check_sequential_chars(self, password):
        """Check for sequential characters (3 or more)"""
        # Check numeric sequences
        if re.search(r'123|234|345|456|567|678|789|012', password):
            return True
        
        # Check keyboard sequences (simple)
        common_sequences = [
            'qwerty', 'asdfgh', 'zxcvbn', 'qazwsx', 'edcrfv'
        ]
        password_lower = password.lower()
        return any(seq in password_lower for seq in common_sequences)
    
    def show_strength_meter(self, score):
        """Animated strength meter with colors"""
        meter_length = 20
        filled = int(score / 100 * meter_length)
        
        # Color coding
        if score >= 80:
            color = "\033[92m"  # Green
        elif score >= 60:
            color = "\033[93m"  # Yellow
        elif score >= 40:
            color = "\033[33m"   # Orange
        else:
            color = "\033[91m"  # Red
        
        meter = color + '[' + '=' * filled + ' ' * (meter_length - filled) + ']' + "\033[0m"
        return meter
    
    def animate_typing(self):
        """Shows animated typing feedback"""
        while self.animation_active:
            sys.stdout.write(f"\rEnter password: {'*' * len(self.current_password)}")
            sys.stdout.flush()
            time.sleep(0.1)
    
    def run_assessment_loop(self):
        """Main interactive loop"""
        print("\n\033[1mPassword Strength Checker\033[0m")
        print("Type your password and see real-time feedback (press ENTER to submit)")
        print("Type 'quit' to exit\n")
        
        while True:
            self.animation_active = True
            self.current_password = ""
            
            # Start typing animation
            t = Thread(target=self.animate_typing)
            t.start()
            
            # Get password input
            while True:
                char = getpass("", stream=None)  # Hidden input
                if char == '\r':  # Enter key
                    break
                elif char == '\x7f':  # Backspace
                    self.current_password = self.current_password[:-1]
                else:
                    self.current_password += char
            
            self.animation_active = False
            t.join()
            
            # Check for exit command
            if self.current_password.lower() in ('quit', 'exit'):
                print("\nExiting...")
                break
            
            # Assess password
            result = self.assess_password(self.current_password)
            
            # Display results with animation
            print("\n\033[2K\rAnalyzing...", end='')
            for _ in range(3):
                print(".", end='', flush=True)
                time.sleep(0.3)
            
            print("\n\033[2K\rResults:")
            print(f"Strength: \033[1m{result['strength'].name.replace('_', ' ')}\033[0m")
            print(f"Score: {result['score']}/100")
            print(self.show_strength_meter(result['score']))
            
            print("\nFeedback:")
            for item in result['feedback']:
                if item.startswith("✓"):
                    print(f"\033[92m{item}\033[0m")  # Green
                else:
                    print(f"\033[91m{item}\033[0m")  # Red
            
            # Show ASCII art based on strength
            self.show_strength_art(result['strength'])
            
            # Recommendations for weak passwords
            if result['strength'] in (StrengthLevel.VERY_WEAK, StrengthLevel.WEAK):
                print("\n\033[93mRecommendations:\033[0m")
                print("- Use at least 12 characters")
                print("- Mix uppercase, lowercase, numbers, and symbols")
                print("- Avoid common words and patterns")
                print("- Example: 'BlueCoffeeTable42!'\n")
    
    def show_strength_art(self, strength):
        """ASCII art visualization"""
        art = {
            StrengthLevel.VERY_STRONG: """
            ┏━━━━━━━━━━━━━━━━━━┓
            ┃  VERY STRONG! 🔒 ┃
            ┗━━━━━━━━━━━━━━━━━━┛
            """,
            StrengthLevel.STRONG: """
            ┏━━━━━━━━━━━━━━━━┓
            ┃  STRONG! 👍   ┃
            ┗━━━━━━━━━━━━━━━━┛
            """,
            StrengthLevel.MODERATE: """
            ┏━━━━━━━━━━━━━━━━┓
            ┃  MODERATE 😐  ┃
            ┗━━━━━━━━━━━━━━━━┛
            """,
            StrengthLevel.WEAK: """
            ┏━━━━━━━━━━━━━━━━┓
            ┃  WEAK! ⚠️     ┃
            ┗━━━━━━━━━━━━━━━━┛
            """,
            StrengthLevel.VERY_WEAK: """
            ┏━━━━━━━━━━━━━━━━┓
            ┃  VERY WEAK! 💀 ┃
            ┗━━━━━━━━━━━━━━━━┛
            """
        }
        print(art.get(strength, ""))

if __name__ == "__main__":
    checker = PasswordAssessor()
    checker.run_assessment_loop()
