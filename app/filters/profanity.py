"""
Profanity filter for message moderation.
"""
import re
from typing import List, Set

class ProfanityFilter:
    """Filter for detecting and handling profanity in messages."""
    
    def __init__(self):
        # Basic list of profane words (can be extended)
        self.profane_words = {
            # Russian profanity
            'блядь', 'сука', 'пизда', 'хуй', 'хер', 'ебать', 'ебануть', 'долбоеб',
            'мудак', 'говно', 'дерьмо', 'срать', 'срака', 'жопа', 'пидор', 'гей',
            'сволочь', 'падла', 'козел', 'кретин', 'дебил', 'идиот', 'дурак',
            'уебок', 'ублюдок', 'тварь', 'мразь', 'мразота', 'гад', 'ненавижу', 'убью',
            
            # English profanity
            'fuck', 'shit', 'bitch', 'asshole', 'damn', 'hell', 'crap',
            'bastard', 'whore', 'slut', 'pussy', 'dick', 'cock', 'nigga',
            'nigger', 'faggot', 'retard', 'moron', 'stupid', 'idiot',
            
            # Common variations with numbers and symbols
            'б1ядь', 'с*ка', 'п*зда', 'х*й', 'ф*ck', 'sh*t'
        }
        
        # Patterns for detecting obfuscated profanity
        self.patterns = [
            # Numbers as letters (3 for E, 1 for I, 0 for O, etc.)
            r'[бb][л1l][я3e]д[ьь]',
            r'[сs][у*][кk][аa]',
            r'[хx][у*][йj]',
            r'[пp][и1i][з3z]д[аa]',
            r'f[\*u]ck',
            r's[\*h]it',
            r'b[\*i]tch',
            # Transliteration patterns
            r'ye\s*xnj\s*tot',  # "ye xnj tot" = "е блядь"
            r'[еe]\s*[бb][лl][яя]\s*[дd][ьь]',  # "е блядь" variations
            # Multiple asterisks or symbols
            r'\*{2,}',
            r'[!@#$%^&*]{3,}',
        ]
        
        # Compile regex patterns
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.patterns]
    
    def contains_profanity(self, text: str) -> bool:
        """Check if text contains profanity."""
        if not text:
            return False
        
        # Normalize text (remove extra spaces, convert to lowercase)
        normalized_text = re.sub(r'\s+', ' ', text.lower().strip())
        
        # Check against word list
        words = normalized_text.split()
        for word in words:
            # Remove punctuation and check
            clean_word = re.sub(r'[^\w]', '', word)
            if clean_word in self.profane_words:
                return True
        
        # Check against regex patterns
        for pattern in self.compiled_patterns:
            if pattern.search(normalized_text):
                return True
        
        return False
    
    def get_detected_words(self, text: str) -> List[str]:
        """Get list of detected profane words in text."""
        detected = []
        
        if not text:
            return detected
        
        normalized_text = re.sub(r'\s+', ' ', text.lower().strip())
        
        # Check word list
        words = normalized_text.split()
        for word in words:
            clean_word = re.sub(r'[^\w]', '', word)
            if clean_word in self.profane_words:
                detected.append(word)
        
        # Check patterns
        for pattern in self.compiled_patterns:
            matches = pattern.findall(normalized_text)
            detected.extend(matches)
        
        return list(set(detected))  # Remove duplicates
    
    def censor_text(self, text: str, replacement: str = "***") -> str:
        """Replace profane words with censorship symbols."""
        if not text:
            return text
        
        result = text
        detected_words = self.get_detected_words(text)
        
        for word in detected_words:
            # Replace with case preservation
            result = re.sub(re.escape(word), replacement, result, flags=re.IGNORECASE)
        
        return result
    
    def add_words(self, words: List[str]):
        """Add new words to the profanity list."""
        self.profane_words.update(word.lower() for word in words)
    
    def remove_words(self, words: List[str]):
        """Remove words from the profanity list."""
        for word in words:
            self.profane_words.discard(word.lower())

# Global instance
profanity_filter = ProfanityFilter()
