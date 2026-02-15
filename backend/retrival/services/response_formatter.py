"""
Response Formatter for Educational Chatbot
Formats LLM responses into well-structured, student-friendly content with emojis and proper formatting
"""

import re
from typing import Dict, List, Any


class ResponseFormatter:
    """Formats AI responses for educational content with proper structure and emojis"""
    
    # Emoji mappings for different content types
    EMOJIS = {
        "definition": "📖",
        "concept": "💡",
        "explanation": "🔍",
        "summary": "📝",
        "example": "✏️",
        "key_point": "⭐",
        "warning": "⚠️",
        "tip": "💭",
        "quote": "💬",
        "answer": "✅",
        "question": "❓",
        "remember": "🧠",
        "important": "🔴",
        "note": "📌",
        "section": "📚",
        "step": "👉",
        "benefit": "🎯",
        "formula": "🧮",
        "comparison": "⚖️",
        "grammar": "✍️",
        "vocabulary": "📚",
        "literature": "📖",
        "poetry": "🎭",
        "prose": "📄",
    }
    
    @staticmethod
    def format_response(raw_response: str) -> str:
        """
        Format raw LLM response into well-structured student-friendly content
        
        Args:
            raw_response: Raw response from the LLM model
            
        Returns:
            Formatted response with structure, emojis, and proper alignment
        """
        if not raw_response or not raw_response.strip():
            return "I couldn't generate a response. Please try again with a different question."
        
        # Remove excessive whitespace but preserve intentional line breaks
        text = raw_response.strip()
        
        # Split into paragraphs
        paragraphs = re.split(r'\n\n+', text)
        formatted_parts = []
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # Detect and format different types of content
            if ResponseFormatter._is_markdown_header(para):
                formatted_parts.append(ResponseFormatter._format_markdown_header(para))
            elif ResponseFormatter._is_definition(para):
                formatted_parts.append(ResponseFormatter._format_definition(para))
            elif ResponseFormatter._is_list(para):
                formatted_parts.append(ResponseFormatter._format_list(para))
            elif ResponseFormatter._is_numbered_list(para):
                formatted_parts.append(ResponseFormatter._format_numbered_list(para))
            elif ResponseFormatter._is_key_point(para):
                formatted_parts.append(ResponseFormatter._format_key_point(para))
            elif ResponseFormatter._is_quote(para):
                formatted_parts.append(ResponseFormatter._format_quote(para))
            else:
                formatted_parts.append(ResponseFormatter._format_paragraph(para))
        
        return "\n\n".join(formatted_parts)
    
    @staticmethod
    def _is_markdown_header(text: str) -> bool:
        """Check if text is a markdown header"""
        return re.match(r'^#+\s+', text.strip()) is not None
    
    @staticmethod
    def _format_markdown_header(text: str) -> str:
        """Format markdown headers with appropriate emojis"""
        # Extract header level and content
        match = re.match(r'^(#+)\s+(.+)$', text.strip())
        if not match:
            return text
        
        level = len(match.group(1))
        content = match.group(2).strip()
        content_lower = content.lower()
        
        # Determine emoji based on header content
        emoji = "📚"  # Default
        
        if any(kw in content_lower for kw in ["summary", "overview", "introduction"]):
            emoji = "📖"
        elif any(kw in content_lower for kw in ["theme", "meaning", "message"]):
            emoji = "💡"
        elif any(kw in content_lower for kw in ["device", "technique", "literary", "figure"]):
            emoji = "✍️"
        elif any(kw in content_lower for kw in ["analysis", "analyze", "stanza", "verse"]):
            emoji = "🔍"
        elif any(kw in content_lower for kw in ["key point", "remember", "important"]):
            emoji = "⭐"
        elif any(kw in content_lower for kw in ["question", "test", "quiz"]):
            emoji = "❓"
        elif any(kw in content_lower for kw in ["example", "instance"]):
            emoji = "✏️"
        elif any(kw in content_lower for kw in ["poem", "poetry", "poet"]):
            emoji = "🎭"
        
        # Format based on header level
        if level == 2:
            return f"\n{emoji} **{content}**"
        elif level == 3:
            return f"\n{emoji} {content}"
        else:
            return f"{emoji} {content}"
    
    @staticmethod
    def _is_definition(text: str) -> bool:
        """Check if text looks like a definition"""
        return (
            "is defined as" in text.lower() or 
            "means" in text.lower() or 
            "refers to" in text.lower() or
            text.startswith("Definition:") or
            text.startswith("Def:")
        )
    
    @staticmethod
    def _is_list(text: str) -> bool:
        """Check if text is a bulleted list"""
        lines = text.split('\n')
        bullet_count = sum(1 for line in lines if re.match(r'^\s*[-•*]\s', line.strip()))
        # Consider it a list if more than one line has bullets or lots of text is bulleted
        total_lines = len([l for l in lines if l.strip()])
        return bullet_count > 0 and (bullet_count >= 2 or (total_lines > 0 and bullet_count / total_lines > 0.5))
    
    @staticmethod
    def _is_numbered_list(text: str) -> bool:
        """Check if text is a numbered list"""
        lines = text.split('\n')
        numbered_count = sum(1 for line in lines if re.match(r'^\s*\d+[.)]\s', line))
        return numbered_count > 0
    
    @staticmethod
    def _is_key_point(text: str) -> bool:
        """Check if text is a key point or important note"""
        return (
            text.startswith("Remember:") or
            text.startswith("Important:") or
            text.startswith("Note:") or
            text.startswith("Key Point:") or
            "must know" in text.lower() or
            "always remember" in text.lower()
        )
    
    @staticmethod
    def _is_quote(text: str) -> bool:
        """Check if text is a quote"""
        return text.startswith('"') and text.endswith('"')
    
    @staticmethod
    def _format_definition(text: str) -> str:
        """Format definition with appropriate emoji and styling"""
        emoji = ResponseFormatter.EMOJIS.get("definition", "📖")
        text = re.sub(r'^Definition:\s*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'^Def:\s*', '', text, flags=re.IGNORECASE)
        
        # Split into term and definition
        if "is defined as" in text.lower():
            parts = re.split(r'\s+is\s+defined\s+as\s+', text, flags=re.IGNORECASE)
            if len(parts) == 2:
                term, definition = parts
                return f"{emoji} **{term.strip()}** – {definition.strip()}"
        elif "means" in text.lower() or "refers to" in text.lower():
            return f"{emoji} {text}"
        
        return f"{emoji} {text}"
    
    @staticmethod
    def _format_list(text: str) -> str:
        """Format bulleted list with emojis"""
        lines = text.split('\n')
        formatted_lines = []
        
        for i, line in enumerate(lines):
            stripped = line.lstrip()
            indent = line[:len(line) - len(stripped)]
            
            # Check if line is a bullet point
            if re.match(r'^[-•*]\s', stripped):
                content = re.sub(r'^[-•*]\s+', '', stripped).strip()
                # Add emoji based on content type
                emoji = ResponseFormatter._get_content_emoji(content)
                formatted_lines.append(f"{indent}{emoji} {content}")
            elif stripped and not stripped.startswith('#'):
                # Non-bullet, non-header lines in a list context
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    @staticmethod
    def _format_numbered_list(text: str) -> str:
        """Format numbered list with better structure"""
        lines = text.split('\n')
        formatted_lines = []
        
        for line in lines:
            stripped = line.lstrip()
            indent = line[:len(line) - len(stripped)]
            
            # Check if line is numbered
            match = re.match(r'^(\d+)[.)]\s+(.+)', stripped)
            if match:
                num, content = match.groups()
                emoji = ResponseFormatter._get_content_emoji(content)
                formatted_lines.append(f"{indent}{emoji} **Step {num}:** {content}")
            else:
                formatted_lines.append(line)
        
        return '\n'.join(formatted_lines)
    
    @staticmethod
    def _format_key_point(text: str) -> str:
        """Format important key points with emphasis"""
        text = re.sub(r'^(Remember|Important|Note|Key Point):\s*', '', text, flags=re.IGNORECASE)
        emoji = ResponseFormatter.EMOJIS.get("key_point", "⭐")
        return f"{emoji} **Remember:** {text}"
    
    @staticmethod
    def _format_quote(text: str) -> str:
        """Format quote with styling"""
        emoji = ResponseFormatter.EMOJIS.get("quote", "💬")
        return f"\n{emoji} > {text}\n"
    
    @staticmethod
    def _format_paragraph(text: str) -> str:
        """Format regular paragraph with emojis based on content type"""
        # Add emoji at the beginning if it looks like an explanation or concept
        if len(text) > 50:  # Only for substantial paragraphs
            if any(keyword in text.lower() for keyword in 
                   ["example", "for example", "such as", "e.g"]):
                emoji = ResponseFormatter.EMOJIS.get("example", "✏️")
                return f"{emoji} {text}"
            elif any(keyword in text.lower() for keyword in 
                     ["remember", "note that", "important", "always"]):
                emoji = ResponseFormatter.EMOJIS.get("important", "🔴")
                return f"{emoji} {text}"
            elif any(keyword in text.lower() for keyword in 
                     ["concept", "idea", "means", "definition", "refer"]):
                emoji = ResponseFormatter.EMOJIS.get("concept", "💡")
                return f"{emoji} {text}"
        
        return text
    
    @staticmethod
    def _get_content_emoji(content: str) -> str:
        """Determine appropriate emoji for content based on keywords"""
        content_lower = content.lower()
        
        # Check for specific keywords
        for keyword, emoji_key in [
            (["example", "instance"], "example"),
            (["important", "crucial", "must"], "important"),
            (["remember", "note", "observe"], "remember"),
            (["explanation"], "explanation"),
            (["key", "essential"], "key_point"),
            (["warning"], "warning"),
            (["tip", "trick", "helpful"], "tip"),
            (["grammar"], "grammar"),
            (["vocabulary", "word"], "vocabulary"),
            (["poetry", "poem", "verse"], "poetry"),
            (["answer", "solution"], "answer"),
            (["question"], "question"),
        ]:
            if any(kw in content_lower for kw in keyword):
                return ResponseFormatter.EMOJIS.get(emoji_key, "•")
        
        return "•"


def format_chat_response(response: str) -> str:
    """
    Convenience function to format chat responses
    
    Args:
        response: Raw response from LLM
        
    Returns:
        Formatted response for display
    """
    return ResponseFormatter.format_response(response)
