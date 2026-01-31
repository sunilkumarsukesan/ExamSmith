"""
Image Search for Picture-Based Questions
Fetches appropriate images of PUBLIC PLACES for 10th standard students
"""

import logging
import random
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)

# Pre-curated high-quality image URLs (Unsplash - free to use)
# All images are of PUBLIC PLACES suitable for 10th standard students
PUBLIC_PLACE_IMAGES = [
    # Parks and Gardens
    {
        "url": "https://images.unsplash.com/photo-1568515387631-8b650bbcdb90?w=600",
        "topic": "Public Park",
        "description": "A beautiful public park with people enjoying nature, children playing, and green spaces"
    },
    {
        "url": "https://images.unsplash.com/photo-1519331379826-f10be5486c6f?w=600",
        "topic": "City Garden",
        "description": "A well-maintained city garden with walking paths, benches, and flowering plants"
    },
    
    # Libraries
    {
        "url": "https://images.unsplash.com/photo-1521587760476-6c12a4b040da?w=600",
        "topic": "Public Library",
        "description": "A grand public library with tall bookshelves and people reading and studying"
    },
    {
        "url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=600",
        "topic": "Reading Room",
        "description": "A quiet library reading room with students studying at tables"
    },
    
    # Schools and Education
    {
        "url": "https://images.unsplash.com/photo-1580582932707-520aed937b7b?w=600",
        "topic": "School Playground",
        "description": "A school playground with students engaged in various activities"
    },
    {
        "url": "https://images.unsplash.com/photo-1509062522246-3755977927d7?w=600",
        "topic": "Classroom",
        "description": "A classroom with teacher and students actively learning together"
    },
    
    # Hospitals and Health
    {
        "url": "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?w=600",
        "topic": "Hospital",
        "description": "A modern hospital building where doctors and nurses serve patients"
    },
    {
        "url": "https://images.unsplash.com/photo-1538108149393-fbbd81895907?w=600",
        "topic": "Health Center",
        "description": "A community health center providing medical services to people"
    },
    
    # Railway and Bus Stations
    {
        "url": "https://images.unsplash.com/photo-1474487548417-781cb71495f3?w=600",
        "topic": "Railway Station",
        "description": "A busy railway station with passengers waiting on the platform"
    },
    {
        "url": "https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=600",
        "topic": "Bus Station",
        "description": "A public bus station with buses and commuters"
    },
    
    # Museums and Cultural Places
    {
        "url": "https://images.unsplash.com/photo-1554907984-15263bfd63bd?w=600",
        "topic": "Museum",
        "description": "A grand museum with visitors viewing art and exhibits"
    },
    {
        "url": "https://images.unsplash.com/photo-1518998053901-5348d3961a04?w=600",
        "topic": "Art Gallery",
        "description": "An art gallery with people appreciating paintings and sculptures"
    },
    
    # Post Office and Government Buildings
    {
        "url": "https://images.unsplash.com/photo-1582555172866-f73bb12a2ab3?w=600",
        "topic": "Post Office",
        "description": "A post office where people send letters and parcels"
    },
    
    # Markets and Shopping Areas
    {
        "url": "https://images.unsplash.com/photo-1555529669-e69e7aa0ba9a?w=600",
        "topic": "Public Market",
        "description": "A vibrant public market with vendors selling fruits and vegetables"
    },
    {
        "url": "https://images.unsplash.com/photo-1441986300917-64674bd600d8?w=600",
        "topic": "Shopping Street",
        "description": "A busy shopping street with stores and pedestrians"
    },
    
    # Religious and Community Places
    {
        "url": "https://images.unsplash.com/photo-1548013146-72479768bada?w=600",
        "topic": "Temple",
        "description": "A beautiful temple with devotees offering prayers"
    },
    {
        "url": "https://images.unsplash.com/photo-1545167622-3a6ac756afa4?w=600",
        "topic": "Community Hall",
        "description": "A community hall where people gather for events and functions"
    },
    
    # Sports Facilities
    {
        "url": "https://images.unsplash.com/photo-1461896836934- voices42d80c?w=600",
        "topic": "Sports Stadium",
        "description": "A sports stadium with athletes and spectators enjoying a match"
    },
    {
        "url": "https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=600",
        "topic": "Swimming Pool",
        "description": "A public swimming pool with people swimming and exercising"
    },
    
    # Beach and Waterfront
    {
        "url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=600",
        "topic": "Beach",
        "description": "A public beach with people enjoying the sun, sand, and sea"
    },
    
    # Zoo and Nature Places
    {
        "url": "https://images.unsplash.com/photo-1534567153574-2b12153a87f0?w=600",
        "topic": "Zoo",
        "description": "A zoo where families observe various animals in enclosures"
    }
]


class ImageSearcher:
    """Searches for appropriate public place images for picture-based questions."""
    
    def __init__(self):
        self.used_topics = set()
    
    async def get_random_public_place_image(self, preferred_topic: str = None) -> Dict:
        """
        Get a random public place image suitable for 10th standard students.
        
        Args:
            preferred_topic: Optional topic preference (e.g., "park", "library", "hospital")
            
        Returns:
            Dict with url, topic, and description
        """
        # If a preferred topic is given, try to find a matching image
        if preferred_topic:
            preferred_lower = preferred_topic.lower()
            matching_images = [
                img for img in PUBLIC_PLACE_IMAGES
                if preferred_lower in img["topic"].lower() or preferred_lower in img["description"].lower()
            ]
            if matching_images:
                # Filter out already used topics if possible
                unused = [img for img in matching_images if img["topic"] not in self.used_topics]
                selected = random.choice(unused if unused else matching_images)
                self.used_topics.add(selected["topic"])
                logger.info(f"Selected matching image for '{preferred_topic}': {selected['topic']}")
                return selected
        
        # Otherwise select a random unused image
        available_images = [
            img for img in PUBLIC_PLACE_IMAGES 
            if img["topic"] not in self.used_topics
        ]
        
        if not available_images:
            # Reset if all used
            self.used_topics.clear()
            available_images = PUBLIC_PLACE_IMAGES
        
        selected = random.choice(available_images)
        self.used_topics.add(selected["topic"])
        
        logger.info(f"Selected random image topic: {selected['topic']}")
        return selected
    
    def get_question_prompt_for_image(self, image_data: Dict) -> str:
        """
        Generate an appropriate question prompt for the public place image.
        
        Args:
            image_data: Dict with topic and description
            
        Returns:
            Question text for the picture-based question
        """
        prompts = [
            f"Look at the following picture of a public place and express your views on it in a paragraph of about 100-120 words.",
            f"Study the picture of the public place given below and write a paragraph describing what you see and its importance in our society.",
            f"Observe the picture of the public place below and write a paragraph expressing your thoughts about its role in community life.",
            f"Look at the picture of this public place. Write a paragraph of about 100 words describing the scene and explaining why such places are important.",
            f"Examine the picture of the public place carefully and write a paragraph about its significance and how it serves the community."
        ]
        
        return random.choice(prompts)


# Global instance
image_searcher = ImageSearcher()


async def get_picture_question(preferred_topic: str = None) -> Dict:
    """
    Generate a complete picture-based question for Q42.
    
    Args:
        preferred_topic: Optional topic preference for the image
    
    Returns:
        Question dict with image_url, question_text, marks, etc.
    """
    image_data = await image_searcher.get_random_public_place_image(preferred_topic)
    question_text = image_searcher.get_question_prompt_for_image(image_data)
    
    return {
        "question_text": question_text,
        "image_url": image_data["url"],
        "image_topic": image_data["topic"],
        "image_description": image_data["description"],
        "marks": 5,
        "section": "Writing",
        "lesson_type": "picture_composition",
        "unit_name": "Picture-Based Writing"
    }


async def get_new_picture_for_revision(teacher_feedback: str, current_topic: str = None) -> Dict:
    """
    Get a new picture based on teacher feedback for revision.
    
    Args:
        teacher_feedback: Teacher's feedback about what kind of image they want
        current_topic: The current image topic (to avoid repeating)
        
    Returns:
        New question dict with different image
    """
    # Parse feedback to find preferred topic
    feedback_lower = teacher_feedback.lower()
    
    # Map common keywords to image topics
    topic_keywords = {
        "park": "Park",
        "garden": "Garden",
        "library": "Library",
        "school": "School",
        "hospital": "Hospital",
        "railway": "Railway",
        "train": "Railway",
        "bus": "Bus",
        "museum": "Museum",
        "market": "Market",
        "beach": "Beach",
        "zoo": "Zoo",
        "temple": "Temple",
        "church": "Temple",
        "mosque": "Temple",
        "stadium": "Stadium",
        "pool": "Swimming",
        "post office": "Post Office"
    }
    
    preferred_topic = None
    for keyword, topic in topic_keywords.items():
        if keyword in feedback_lower:
            preferred_topic = topic
            break
    
    # Mark current topic as used to avoid repetition
    if current_topic:
        image_searcher.used_topics.add(current_topic)
    
    # Get new image
    image_data = await image_searcher.get_random_public_place_image(preferred_topic)
    question_text = image_searcher.get_question_prompt_for_image(image_data)
    
    return {
        "question_text": question_text,
        "image_url": image_data["url"],
        "image_topic": image_data["topic"],
        "image_description": image_data["description"],
        "marks": 5,
        "section": "Writing",
        "lesson_type": "picture_composition",
        "unit_name": "Picture-Based Writing"
    }
