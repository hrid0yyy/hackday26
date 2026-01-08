"""Service layer for text to ASL sign language conversion."""

import json
import asyncio
from typing import List, Optional, Dict
from src.modules.text_to_sign.models import (
    TextToSignRequest,
    TextToSignResponse,
    SignWord,
    FingerspellResponse,
    UserStatus,
)
from src.core.config import settings
from src.core.db import supabase_admin_client
from openai import OpenAI


class TextToSignService:
    """Service for converting text to ASL sign language based on user's disability status."""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.db = supabase_admin_client
        
        # ASL fingerspelling alphabet descriptions
        self.fingerspell_alphabet = {
            'A': "Make a fist with thumb resting on the side of the index finger",
            'B': "Hold fingers straight up together, thumb tucked across palm",
            'C': "Curve hand into a 'C' shape, fingers together",
            'D': "Touch thumb to middle, ring, and pinky fingers; index points up",
            'E': "Curl all fingers down, thumb tucked under fingertips",
            'F': "Touch thumb and index finger in a circle, other fingers straight up",
            'G': "Point index finger and thumb parallel to ground, other fingers closed",
            'H': "Point index and middle fingers sideways together, other fingers closed",
            'I': "Make a fist with pinky finger extended up",
            'J': "Make 'I' handshape and trace a 'J' motion in the air",
            'K': "Point index and middle finger up in a 'V', thumb between them",
            'L': "Make an 'L' shape with thumb and index finger",
            'M': "Tuck thumb under first three fingers draped over",
            'N': "Tuck thumb under first two fingers draped over",
            'O': "Touch all fingertips to thumb forming an 'O' shape",
            'P': "Like 'K' but pointing downward",
            'Q': "Like 'G' but pointing downward",
            'R': "Cross middle finger over index finger, other fingers closed",
            'S': "Make a fist with thumb wrapped over fingers",
            'T': "Tuck thumb between index and middle finger in a fist",
            'U': "Hold index and middle finger straight up together, other fingers closed",
            'V': "Hold index and middle finger up in a 'V' shape",
            'W': "Hold index, middle, and ring fingers up spread apart",
            'X': "Hook index finger like a claw, other fingers closed",
            'Y': "Extend thumb and pinky, other fingers closed (hang loose sign)",
            'Z': "Point index finger and trace a 'Z' in the air"
        }
        
        # ASL alphabet image URLs from Lifeprint.com (free educational resource)
        self.asl_letter_images = {
            'A': "https://www.lifeprint.com/asl101/fingerspelling/abc-gifs/a.gif",
            'B': "https://www.lifeprint.com/asl101/fingerspelling/abc-gifs/b.gif",
            'C': "https://www.lifeprint.com/asl101/fingerspelling/abc-gifs/c.gif",
            'D': "https://www.lifeprint.com/asl101/fingerspelling/abc-gifs/d.gif",
            'E': "https://www.lifeprint.com/asl101/fingerspelling/abc-gifs/e.gif",
            'F': "https://www.lifeprint.com/asl101/fingerspelling/abc-gifs/f.gif",
            'G': "https://www.lifeprint.com/asl101/fingerspelling/abc-gifs/g.gif",
            'H': "https://www.lifeprint.com/asl101/fingerspelling/abc-gifs/h.gif",
            'I': "https://www.lifeprint.com/asl101/fingerspelling/abc-gifs/i.gif",
            'J': "https://www.lifeprint.com/asl101/fingerspelling/abc-gifs/j.gif",
            'K': "https://www.lifeprint.com/asl101/fingerspelling/abc-gifs/k.gif",
            'L': "https://www.lifeprint.com/asl101/fingerspelling/abc-gifs/l.gif",
            'M': "https://www.lifeprint.com/asl101/fingerspelling/abc-gifs/m.gif",
            'N': "https://www.lifeprint.com/asl101/fingerspelling/abc-gifs/n.gif",
            'O': "https://www.lifeprint.com/asl101/fingerspelling/abc-gifs/o.gif",
            'P': "https://www.lifeprint.com/asl101/fingerspelling/abc-gifs/p.gif",
            'Q': "https://www.lifeprint.com/asl101/fingerspelling/abc-gifs/q.gif",
            'R': "https://www.lifeprint.com/asl101/fingerspelling/abc-gifs/r.gif",
            'S': "https://www.lifeprint.com/asl101/fingerspelling/abc-gifs/s.gif",
            'T': "https://www.lifeprint.com/asl101/fingerspelling/abc-gifs/t.gif",
            'U': "https://www.lifeprint.com/asl101/fingerspelling/abc-gifs/u.gif",
            'V': "https://www.lifeprint.com/asl101/fingerspelling/abc-gifs/v.gif",
            'W': "https://www.lifeprint.com/asl101/fingerspelling/abc-gifs/w.gif",
            'X': "https://www.lifeprint.com/asl101/fingerspelling/abc-gifs/x.gif",
            'Y': "https://www.lifeprint.com/asl101/fingerspelling/abc-gifs/y.gif",
            'Z': "https://www.lifeprint.com/asl101/fingerspelling/abc-gifs/z.gif"
        }
    
    def get_user_status(self, user_id: str) -> UserStatus:
        """Get user's disability status from profiles table."""
        result = self.db.table("profiles").select("status").eq("id", user_id).execute()
        
        if result.data and len(result.data) > 0:
            status = result.data[0].get("status", "normal")
            return UserStatus(status)
        
        # Default to normal if profile not found
        return UserStatus.NORMAL
    
    def save_conversation(self, sender_id: str, receiver_id: str, raw_text: str, cleaned_text: str) -> str:
        """Save conversation to chat_conversation table."""
        result = self.db.table("chat_conversation").insert({
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "raw_text": raw_text,
            "cleaned_text": cleaned_text
        }).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]["id"]
        
        raise Exception("Failed to save conversation")
    
    def get_letter_images(self, sentence: str) -> List[Dict]:
        """Get ASL fingerspelling images for each letter in the sentence."""
        from src.modules.text_to_sign.models import LetterSign
        
        letter_images = []
        for char in sentence.upper():
            if char.isalpha() and char in self.asl_letter_images:
                letter_images.append(LetterSign(
                    letter=char,
                    image_url=self.asl_letter_images[char],
                    description=self.fingerspell_alphabet[char]
                ))
            elif char == ' ':
                # Add a space marker
                letter_images.append(LetterSign(
                    letter=" ",
                    image_url="",  # No image for space
                    description="Pause briefly between words"
                ))
        
        return letter_images
    
    async def convert_text_to_sign(self, request: TextToSignRequest) -> TextToSignResponse:
        """Convert text based on the receiver's disability status."""
        
        # Use the status directly from request
        receiver_status = request.receiver_status
        
        # Process based on status
        if receiver_status in [UserStatus.DEAF, UserStatus.MUTE]:
            # Convert to ASL for deaf/mute users
            return await self._convert_to_asl(request, receiver_status)
        elif receiver_status == UserStatus.BLIND:
            # Convert to audio-friendly format for blind users
            return await self._convert_for_blind(request, receiver_status)
        else:
            # Normal user - just clean the text
            return await self._process_normal(request, receiver_status)
    
    async def _convert_to_asl(self, request: TextToSignRequest, status: UserStatus) -> TextToSignResponse:
        """Convert text to ASL sign language for deaf/mute users."""
        
        detail_instructions = {
            "basic": "Provide simple, brief descriptions of each sign.",
            "detailed": "Provide detailed descriptions including handshape, movement, and location.",
            "expert": "Provide comprehensive descriptions with all technical details, variations, and regional differences."
        }
        
        system_prompt = f"""You are an expert ASL (American Sign Language) interpreter and teacher. 
Your task is to convert English text to ASL sign language instructions.

Important ASL grammar rules to follow:
1. ASL has different word order than English (Topic-Comment structure)
2. ASL often omits articles (a, an, the) and linking verbs (is, are, am)
3. Time indicators come first in ASL sentences
4. Questions use specific facial expressions and often have different word order

{detail_instructions.get(request.detail_level, detail_instructions["detailed"])}

Respond in JSON format with this structure:
{{
    "asl_gloss": "The sentence in ASL gloss notation (sign order, uppercase)",
    "cleaned_text": "The text cleaned up for display",
    "sentence_structure_note": "Brief explanation of grammar changes from English to ASL",
    "signs": [
        {{
            "word": "original word",
            "sign_type": "sign or fingerspell",
            "sign_description": "detailed description of how to perform the sign",
            "handshape": "description of hand shape",
            "movement": "description of movement",
            "location": "where the sign is made",
            "facial_expression": "required facial expression if any",
            "notes": "additional tips or variations"
        }}
    ]
}}

For proper nouns, names, or words without common ASL signs, use fingerspelling.
"""
        
        user_message = f"""Convert this text to ASL sign language:

"{request.text}"

Include fingerspelling: {request.include_fingerspelling}
Detail level: {request.detail_level}"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ],
            temperature=0.3,
            max_tokens=3000,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        
        # Parse signs
        signs = []
        for sign_data in result.get("signs", []):
            signs.append(SignWord(
                word=sign_data.get("word", ""),
                sign_type=sign_data.get("sign_type", "sign"),
                sign_description=sign_data.get("sign_description", ""),
                handshape=sign_data.get("handshape"),
                movement=sign_data.get("movement"),
                location=sign_data.get("location"),
                facial_expression=sign_data.get("facial_expression"),
                notes=sign_data.get("notes")
            ))
        
        # Get letter images if requested
        letter_images = None
        if request.generate_images:
            letter_images = self.get_letter_images(request.text)
        
        cleaned_text = result.get("cleaned_text", request.text)
        
        return TextToSignResponse(
            original_text=request.text,
            processed_text=cleaned_text,
            receiver_status=status,
            asl_gloss=result.get("asl_gloss", ""),
            signs=signs,
            letter_images=letter_images,
            sentence_structure_note=result.get("sentence_structure_note"),
            total_signs=len(signs)
        )
    
    async def _convert_for_blind(self, request: TextToSignRequest, status: UserStatus) -> TextToSignResponse:
        """Convert text to audio-friendly format for blind users."""
        
        system_prompt = """You are an assistant that optimizes text for blind users who use screen readers.
Your task is to:
1. Add descriptive context where visual elements might be referenced
2. Spell out abbreviations
3. Describe any formatting or structure
4. Make the text clear and easy to understand when read aloud

Respond in JSON format:
{
    "cleaned_text": "The optimized text for screen readers",
    "audio_description": "Additional audio context or descriptions if needed"
}
"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Optimize this text for a blind user: \"{request.text}\""}
            ],
            temperature=0.3,
            max_tokens=1500,
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        cleaned_text = result.get("cleaned_text", request.text)
        
        return TextToSignResponse(
            original_text=request.text,
            processed_text=cleaned_text,
            receiver_status=status,
            audio_description=result.get("audio_description")
        )
    
    async def _process_normal(self, request: TextToSignRequest, status: UserStatus) -> TextToSignResponse:
        """Process text for normal users - just clean."""
        
        # For normal users, just clean the text slightly
        cleaned_text = request.text.strip()
        
        return TextToSignResponse(
            original_text=request.text,
            processed_text=cleaned_text,
            receiver_status=status
        )
    
    def get_fingerspelling(self, word: str) -> FingerspellResponse:
        """Get fingerspelling instructions for a word."""
        letters = []
        for char in word.upper():
            if char in self.fingerspell_alphabet:
                letters.append({
                    "letter": char,
                    "handshape": self.fingerspell_alphabet[char]
                })
            elif char == ' ':
                letters.append({
                    "letter": "[space]",
                    "handshape": "Brief pause between words"
                })
            else:
                letters.append({
                    "letter": char,
                    "handshape": "No fingerspelling available for this character"
                })
        
        return FingerspellResponse(
            word=word,
            letters=letters
        )
    
    async def get_common_phrases(self) -> List[dict]:
        """Get common ASL phrases with their signs."""
        common_phrases = [
            {
                "phrase": "Hello",
                "asl_description": "Open hand, touch forehead near temple, move outward like a salute"
            },
            {
                "phrase": "Thank you",
                "asl_description": "Flat hand touches chin and moves forward and down"
            },
            {
                "phrase": "Please",
                "asl_description": "Flat hand circles on chest"
            },
            {
                "phrase": "Sorry",
                "asl_description": "Make 'A' handshape (fist), circle on chest"
            },
            {
                "phrase": "Yes",
                "asl_description": "Make 'S' handshape (fist), nod it up and down like nodding head"
            },
            {
                "phrase": "No",
                "asl_description": "Extend index and middle finger, snap them to thumb"
            },
            {
                "phrase": "Help",
                "asl_description": "Make thumbs-up on flat palm, lift both hands up"
            },
            {
                "phrase": "I love you",
                "asl_description": "Extend thumb, index finger, and pinky (ILY sign)"
            },
            {
                "phrase": "What's your name?",
                "asl_description": "Point to person, then tap index fingers together twice (NAME sign), with questioning facial expression"
            },
            {
                "phrase": "Nice to meet you",
                "asl_description": "Sign NICE (slide palm off other palm), MEET (index fingers come together), then point to person"
            }
        ]
        return common_phrases


# Create singleton instance
text_to_sign_service = TextToSignService()
