"""
Coverage Validation Module

Validates that generated question paper meets all curriculum coverage requirements.
"""

from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)


class CoverageValidator:
    """Validates question paper coverage against curriculum requirements."""

    # Prescribed Memory Poems (2025 TN SSLC Curriculum)
    PRESCRIBED_MEMORY_POEMS = {
        "Life": "Henry Van Dyke",
        "The Road Not Taken": "Robert Frost",
        "No Men Are Foreign": "James Kirkup",
        "Laugh and Be Merry": "John Masefield",
        "The River": "Caroline Ann Bowles",
        "Sea Fever": "John Masefield",
    }

    # Prescribed Prose Lessons (2025 TN SSLC Curriculum)
    PRESCRIBED_PROSE_LESSONS = {
        1: "His First Flight",
        2: "The Tempest",
        3: "Two Gentlemen of Verona",
        4: "The Grumble Family",
        5: "A Tale of Two Cities",
        6: "The Last Lesson",
    }

    # Prescribed Poetry List (2025 TN SSLC Curriculum)
    PRESCRIBED_POETRY = {
        "Life": {"author": "Henry Van Dyke", "unit": 1, "is_memory": True},
        "The Road Not Taken": {"author": "Robert Frost", "unit": 2, "is_memory": True},
        "No Men Are Foreign": {"author": "James Kirkup", "unit": 3, "is_memory": True},
        "Laugh and Be Merry": {"author": "John Masefield", "unit": 4, "is_memory": True},
        "The River": {"author": "Caroline Ann Bowles", "unit": 5, "is_memory": True},
        "Sea Fever": {"author": "John Masefield", "unit": 0, "is_memory": True},
        "The Solitary Reaper": {"author": "William Wordsworth", "unit": 2, "is_memory": False},
        "Ozymandias": {"author": "Percy Bysshe Shelley", "unit": 3, "is_memory": False},
    }

    # Prescribed Supplementary Stories (2025 TN SSLC Curriculum)
    PRESCRIBED_SUPPLEMENTARY = {
        1: "The Necklace",
        2: "After Twenty Years",
        3: "The Last Leaf",
        4: "A Christmas Carol",
        5: "The Open Window",
    }

    # Grammar Area Codes
    GRAMMAR_AREAS = {
        "VOICE": "Active/Passive Voice",
        "SPEECH": "Direct/Indirect Speech",
        "PUNCTUATION": "Punctuation",
        "SENTENCE_TYPE": "Simple/Complex/Compound Sentences",
        "REARRANGEMENT": "Sentence Rearrangement",
    }

    def __init__(self):
        self.violations = []
        self.coverage_report = {}

    def validate_paper(self, questions: List[Dict], prose_lessons: List[int] = None, poems: List[str] = None) -> Tuple[bool, List[str]]:
        """
        Validate complete question paper against all coverage rules.
        
        Args:
            questions: List of generated questions with metadata
            prose_lessons: Total available prose lessons (default: [1, 2, 3, 4, 5, 6])
            poems: List of available poem titles
        
        Returns:
            (is_valid, list_of_violations)
        """
        self.violations = []
        
        if prose_lessons is None:
            prose_lessons = list(range(1, 7))  # Lessons 1-6
        if poems is None:
            poems = []

        # Run all validations
        self._validate_prose_coverage(questions, prose_lessons)
        self._validate_poetry_coverage(questions, poems)
        self._validate_grammar_distribution(questions)
        self._validate_vocabulary_distribution(questions)
        self._validate_supplementary_coverage(questions)
        self._validate_internal_choice(questions)
        self._validate_memory_poem(questions)

        is_valid = len(self.violations) == 0
        
        if is_valid:
            logger.info("✓ All coverage validations PASSED")
        else:
            logger.warning(f"✗ Coverage validations FAILED with {len(self.violations)} violations")
            for violation in self.violations:
                logger.warning(f"  - {violation}")
        
        return is_valid, self.violations

    def _validate_prose_coverage(self, questions: List[Dict], prose_lessons: List[int]):
        """Verify every prose lesson appears at least once."""
        prose_questions = [q for q in questions if q.get("lesson_type") == "prose"]
        covered_lessons = set()
        
        for q in prose_questions:
            unit_name = q.get("unit_name", "")
            # Extract lesson number from "Prose Lesson N"
            try:
                lesson_num = int(unit_name.split()[-1])
                covered_lessons.add(lesson_num)
            except:
                pass
        
        missing_lessons = set(prose_lessons) - covered_lessons
        
        if missing_lessons:
            violation = f"Prose coverage incomplete: Lessons {sorted(missing_lessons)} not covered"
            self.violations.append(violation)
            logger.warning(f"  ✗ {violation}")
        else:
            logger.info(f"  ✓ All {len(prose_lessons)} prose lessons covered: {sorted(covered_lessons)}")
        
        self.coverage_report["prose_lessons"] = {
            "required": prose_lessons,
            "covered": sorted(covered_lessons),
            "missing": sorted(missing_lessons)
        }

    def _validate_poetry_coverage(self, questions: List[Dict], poems: List[str] = None):
        """Verify poetry questions span at least 3 different poems."""
        poetry_questions = [q for q in questions if q.get("lesson_type") == "poetry"]
        covered_poems = set()
        
        for q in poetry_questions:
            unit_name = q.get("unit_name", "")
            # Extract poem name from "Poetry: <poem_name>"
            if "Poetry:" in unit_name:
                poem_name = unit_name.replace("Poetry:", "").strip()
                covered_poems.add(poem_name)
        
        if len(covered_poems) < 3:
            violation = f"Poetry coverage incomplete: Only {len(covered_poems)} poems covered, need ≥3"
            self.violations.append(violation)
            logger.warning(f"  ✗ {violation} (Poems: {covered_poems})")
        else:
            logger.info(f"  ✓ Poetry diversity satisfied: {len(covered_poems)} poems covered")
        
        self.coverage_report["poetry"] = {
            "required_min_poems": 3,
            "covered_poems": len(covered_poems),
            "poems": sorted(covered_poems)
        }

    def _validate_grammar_distribution(self, questions: List[Dict]):
        """Verify grammar areas not repeated more than 2 times."""
        grammar_questions = [q for q in questions if q.get("lesson_type") == "grammar"]
        grammar_areas = {}
        
        for q in grammar_questions:
            area = q.get("grammar_area", "unknown")
            grammar_areas[area] = grammar_areas.get(area, 0) + 1
        
        violations = {area: count for area, count in grammar_areas.items() if count > 2}
        
        if violations:
            for area, count in violations.items():
                violation = f"Grammar area '{area}' repeated {count} times, should be ≤2"
                self.violations.append(violation)
                logger.warning(f"  ✗ {violation}")
        else:
            logger.info(f"  ✓ Grammar distribution valid: {len(grammar_areas)} areas, max repeats: {max(grammar_areas.values()) if grammar_areas else 0}")
        
        self.coverage_report["grammar"] = {
            "areas_count": len(grammar_areas),
            "distribution": grammar_areas,
            "violations": violations
        }

    def _validate_vocabulary_distribution(self, questions: List[Dict]):
        """Verify vocabulary questions evenly distributed across units."""
        mcq_questions = [q for q in questions if q.get("part") == "I" and q.get("lesson_type") == "glossary"]
        units = {}
        
        for q in mcq_questions:
            unit = q.get("unit_name", "unknown")
            units[unit] = units.get(unit, 0) + 1
        
        if len(units) > 0:
            max_from_unit = max(units.values())
            total_mcqs = len(mcq_questions)
            
            if max_from_unit > total_mcqs * 0.6:  # More than 60% from one unit
                violation = f"Vocabulary distribution skewed: {max_from_unit}/{total_mcqs} MCQs from single unit"
                self.violations.append(violation)
                logger.warning(f"  ✗ {violation}")
            else:
                logger.info(f"  ✓ Vocabulary distribution acceptable: {len(units)} units represented")
        
        self.coverage_report["vocabulary"] = {
            "mcqs_count": len(mcq_questions),
            "units": units
        }

    def _validate_supplementary_coverage(self, questions: List[Dict]):
        """Verify supplementary story questions use different stories."""
        supplementary_questions = [q for q in questions if q.get("lesson_type") == "supplementary"]
        stories = {}
        
        for q in supplementary_questions:
            unit = q.get("unit_name", "unknown")
            stories[unit] = stories.get(unit, 0) + 1
        
        duplicates = {story: count for story, count in stories.items() if count > 1}
        
        if duplicates:
            for story, count in duplicates.items():
                violation = f"Supplementary story '{story}' used {count} times, should use different stories"
                self.violations.append(violation)
                logger.warning(f"  ✗ {violation}")
        else:
            logger.info(f"  ✓ Supplementary stories: {len(stories)} different stories used")
        
        self.coverage_report["supplementary"] = {
            "questions_count": len(supplementary_questions),
            "stories": stories,
            "duplicates": duplicates
        }

    def _validate_internal_choice(self, questions: List[Dict]):
        """Verify internal choice questions are properly marked."""
        # Part II: Prose should have internal_choice=true (choose 3 of 4)
        # Part IV: Q46 and Q47 should have internal_choice=true
        
        part_ii_prose = [q for q in questions if q.get("part") == "II" and q.get("section") == "Prose"]
        part_iv_questions = [q for q in questions if q.get("part") == "IV"]
        
        prose_with_choice = [q for q in part_ii_prose if q.get("internal_choice")]
        
        if len(part_ii_prose) > 0 and len(prose_with_choice) == 0:
            violation = "Part II Prose: internal_choice should be marked for 'choose 3 of 4' rule"
            self.violations.append(violation)
            logger.warning(f"  ✗ {violation}")
        
        part_iv_with_choice = [q for q in part_iv_questions if q.get("internal_choice")]
        if len(part_iv_questions) > 0 and len(part_iv_with_choice) < 2:
            violation = f"Part IV: Expected 2 questions with internal_choice=true, found {len(part_iv_with_choice)}"
            self.violations.append(violation)
            logger.warning(f"  ✗ {violation}")
        else:
            logger.info(f"  ✓ Internal choice questions properly marked")
        
        self.coverage_report["internal_choice"] = {
            "part_ii_prose_with_choice": len(prose_with_choice),
            "part_iv_with_choice": len(part_iv_with_choice)
        }

    def _validate_memory_poem(self, questions: List[Dict]):
        """Verify memory poem from prescribed list."""
        memory_questions = [q for q in questions if q.get("lesson_type") == "memory_poem"]
        
        # Check existence
        if len(memory_questions) == 0:
            violation = "Memory poem (Part III-V): Question 45 not found"
            self.violations.append(violation)
            logger.warning(f"  ✗ {violation}")
        elif len(memory_questions) > 1:
            violation = f"Memory poem: {len(memory_questions)} questions found, expected 1"
            self.violations.append(violation)
            logger.warning(f"  ✗ {violation}")
        else:
            # Validate against prescribed list
            memory_q = memory_questions[0]
            unit_name = memory_q.get("unit_name", "")
            
            # Extract poem title from unit_name (e.g., "Memory Poem: The Road Not Taken")
            poem_title = unit_name.replace("Memory Poem:", "").strip() if "Memory Poem:" in unit_name else unit_name
            
            # Check if poem is in prescribed list
            is_valid_poem = any(
                poem_title.lower() in prescribed.lower() or prescribed.lower() in poem_title.lower()
                for prescribed in self.PRESCRIBED_MEMORY_POEMS.keys()
            )
            
            if not is_valid_poem:
                violation = f"Memory poem '{poem_title}' NOT in prescribed curriculum list. Valid poems: {list(self.PRESCRIBED_MEMORY_POEMS.keys())}"
                self.violations.append(violation)
                logger.warning(f"  ✗ {violation}")
            else:
                logger.info(f"  ✓ Memory poem '{poem_title}' is valid (in prescribed list)")
        
        self.coverage_report["memory_poem"] = {
            "count": len(memory_questions),
            "poems": [q.get("unit_name", "") for q in memory_questions],
            "prescribed_list": list(self.PRESCRIBED_MEMORY_POEMS.keys())
        }

    def get_coverage_report(self) -> Dict:
        """Return detailed coverage validation report."""
        report = {
            "is_valid": len(self.violations) == 0,
            "total_violations": len(self.violations),
            "violations": self.violations,
            "coverage_details": self.coverage_report
        }
        return report


# Singleton instance
_coverage_validator = None


def get_coverage_validator() -> CoverageValidator:
    """Get or create the coverage validator singleton."""
    global _coverage_validator
    if _coverage_validator is None:
        _coverage_validator = CoverageValidator()
    return _coverage_validator
