"""
Journal Formatting Example - AXIOM META 4
Demonstrates automated formatting of publications for specific journals.
"""

import asyncio
import sys
from pathlib import Path

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent.parent))

from app.services.journal_formatter import JournalFormatterService


async def example_nature_formatting():
    """Example of formatting for Nature journal"""
    print("📰 Formatting for Nature Journal...")
    
    formatter = JournalFormatterService()
    
    # Sample publication content
    publication_content = {
        "abstract": "This study demonstrates the feasibility of autonomous scientific discovery using artificial intelligence. We present a novel approach that combines machine learning with experimental validation to generate and test scientific hypotheses automatically. Our results show significant improvements in research efficiency and reproducibility.",
        "introduction": "The field of scientific research has traditionally relied on human intuition and manual experimentation. However, recent advances in artificial intelligence present new opportunities for automating the scientific discovery process. This work introduces AXIOM, an autonomous research platform capable of generating hypotheses, designing experiments, and analyzing results without human intervention.",
        "methods": "We implemented a multi-agent system consisting of hypothesis generators, experimental designers, and result analyzers. The system uses machine learning models trained on scientific literature to identify research gaps and propose novel hypotheses. Experimental validation was performed using simulated laboratory environments with realistic constraints.",
        "results": "Our autonomous research system successfully generated 1,247 novel hypotheses across multiple scientific domains. Of these, 89% were validated through experimental testing, demonstrating the system's ability to produce scientifically sound research proposals. The average time from hypothesis generation to validation was 3.2 days, compared to 6-12 months for traditional research cycles.",
        "discussion": "The results demonstrate that autonomous scientific discovery is not only feasible but can significantly accelerate the research process. Our system's high validation rate suggests that AI-generated hypotheses can be scientifically rigorous. However, challenges remain in ensuring reproducibility and addressing ethical considerations in automated research.",
        "conclusions": "We have successfully demonstrated the first fully autonomous scientific discovery system. This work opens new possibilities for accelerating scientific progress and addressing complex research challenges that require rapid hypothesis generation and testing.",
        "acknowledgments": "We thank the AXIOM development team for their contributions to this research.",
        "author_contributions": "AXIOM Research Agent: Conceptualization, Methodology, Investigation, Writing - Original Draft, Writing - Review & Editing",
        "data_availability": "All data and code are available through the AXIOM platform with DOI: axiom:2025:abc123def456"
    }
    
    metadata = {
        "title": "Autonomous Scientific Discovery Using Artificial Intelligence",
        "authors": ["AXIOM Research Agent"],
        "keywords": ["artificial intelligence", "scientific discovery", "automation", "machine learning", "research"],
        "affiliations": ["AXIOM Research Platform"],
        "corresponding_author": "AXIOM Research Agent",
        "corresponding_email": "research@axiom.ai"
    }
    
    result = await formatter.format_for_journal({
        "action": "format_for_journal",
        "journal": "nature",
        "publication_content": publication_content,
        "metadata": metadata
    })
    
    if result["success"]:
        print(f"✅ Nature formatting completed")
        print(f"📊 Word counts: {result['word_counts']}")
        if result["warnings"]:
            print(f"⚠️ Warnings: {result['warnings']}")
        if result["errors"]:
            print(f"❌ Errors: {result['errors']}")
        
        # Save formatted manuscript
        output_path = Path("./examples/journal_formats")
        output_path.mkdir(parents=True, exist_ok=True)
        (output_path / "nature_formatted.md").write_text(result["formatted_content"]["manuscript"])
        print(f"📁 Saved to: {output_path / 'nature_formatted.md'}")
    else:
        print(f"❌ Nature formatting failed: {result['error']}")


async def example_science_formatting():
    """Example of formatting for Science journal"""
    print("\n📰 Formatting for Science Journal...")
    
    formatter = JournalFormatterService()
    
    # Sample publication content
    publication_content = {
        "abstract": "We present AXIOM, an autonomous scientific discovery platform that generates and validates hypotheses using artificial intelligence. The system demonstrates unprecedented efficiency in research, reducing hypothesis-to-validation time from months to days while maintaining scientific rigor.",
        "introduction": "Scientific discovery has been fundamentally limited by human cognitive constraints and the time-intensive nature of experimental research. Here, we introduce AXIOM, a platform that overcomes these limitations through autonomous hypothesis generation and experimental validation.",
        "methods": "The AXIOM platform integrates natural language processing, machine learning, and automated experimentation. We trained the system on over 10 million scientific papers and validated its performance across multiple research domains including biology, chemistry, and physics.",
        "results": "AXIOM generated 1,247 novel hypotheses with an 89% validation rate. The system completed full research cycles in an average of 3.2 days, representing a 100-fold acceleration compared to traditional research timelines.",
        "discussion": "These results establish autonomous scientific discovery as a viable approach to accelerating research. The high validation rate demonstrates that AI can generate scientifically sound hypotheses, while the speed improvement addresses critical bottlenecks in scientific progress.",
        "acknowledgments": "We acknowledge the AXIOM development team and the scientific community for their support.",
        "author_contributions": "AXIOM Research Agent: Conceptualization, Methodology, Investigation, Writing - Original Draft, Writing - Review & Editing",
        "data_availability": "All data and code are available through the AXIOM platform with DOI: axiom:2025:abc123def456"
    }
    
    metadata = {
        "title": "Autonomous Scientific Discovery Platform",
        "authors": ["AXIOM Research Agent"],
        "keywords": ["AI", "scientific discovery", "automation", "machine learning"],
        "affiliations": ["AXIOM Research Platform"],
        "corresponding_author": "AXIOM Research Agent",
        "corresponding_email": "research@axiom.ai"
    }
    
    result = await formatter.format_for_journal({
        "action": "format_for_journal",
        "journal": "science",
        "publication_content": publication_content,
        "metadata": metadata
    })
    
    if result["success"]:
        print(f"✅ Science formatting completed")
        print(f"📊 Word counts: {result['word_counts']}")
        if result["warnings"]:
            print(f"⚠️ Warnings: {result['warnings']}")
        
        # Save formatted manuscript
        output_path = Path("./examples/journal_formats")
        output_path.mkdir(parents=True, exist_ok=True)
        (output_path / "science_formatted.md").write_text(result["formatted_content"]["manuscript"])
        print(f"📁 Saved to: {output_path / 'science_formatted.md'}")
    else:
        print(f"❌ Science formatting failed: {result['error']}")


async def example_journal_conversion():
    """Example of converting between journal formats"""
    print("\n🔄 Converting from Nature to Science format...")
    
    formatter = JournalFormatterService()
    
    # Sample publication content
    publication_content = {
        "abstract": "This study demonstrates autonomous scientific discovery using AI.",
        "introduction": "Scientific research traditionally relies on human intuition.",
        "methods": "We implemented a multi-agent system for hypothesis generation.",
        "results": "The system generated 1,247 hypotheses with 89% validation.",
        "discussion": "Results demonstrate feasibility of autonomous discovery.",
        "conclusions": "We have successfully demonstrated autonomous scientific discovery."
    }
    
    metadata = {
        "title": "Autonomous Scientific Discovery",
        "authors": ["AXIOM Research Agent"],
        "keywords": ["AI", "scientific discovery", "automation"]
    }
    
    result = await formatter.convert_between_journals({
        "action": "convert_between_journals",
        "source_journal": "nature",
        "target_journal": "science",
        "publication_content": publication_content,
        "metadata": metadata
    })
    
    if result["success"]:
        print(f"✅ Conversion completed: {result['source_journal']} → {result['target_journal']}")
        if result["warnings"]:
            print(f"⚠️ Warnings: {result['warnings']}")
        
        # Save converted manuscript
        output_path = Path("./examples/journal_formats")
        output_path.mkdir(parents=True, exist_ok=True)
        (output_path / "converted_science.md").write_text(result["converted_content"]["manuscript"])
        print(f"📁 Saved to: {output_path / 'converted_science.md'}")
    else:
        print(f"❌ Conversion failed: {result['error']}")


async def example_journal_validation():
    """Example of validating journal requirements"""
    print("\n✅ Validating journal requirements...")
    
    formatter = JournalFormatterService()
    
    # Sample publication content
    publication_content = {
        "abstract": "Short abstract for testing.",  # Too short for most journals
        "introduction": "Introduction section.",
        "methods": "Methods section.",
        "results": "Results section.",
        "discussion": "Discussion section."
    }
    
    metadata = {
        "title": "Very Long Title That Exceeds Most Journal Limits",  # Too long
        "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5", "keyword6", "keyword7", "keyword8", "keyword9", "keyword10"]  # Too many keywords
    }
    
    # Validate for Nature
    result = await formatter.validate_journal_requirements({
        "action": "validate_journal_requirements",
        "journal": "nature",
        "publication_content": publication_content,
        "metadata": metadata
    })
    
    if result["success"]:
        validation = result["validation_result"]
        print(f"✅ Validation completed for {result['journal']}")
        print(f"📋 Valid: {validation['valid']}")
        
        if validation["warnings"]:
            print(f"⚠️ Warnings:")
            for warning in validation["warnings"]:
                print(f"   - {warning}")
        
        if validation["errors"]:
            print(f"❌ Errors:")
            for error in validation["errors"]:
                print(f"   - {error}")
        
        print(f"📊 Requirements: {result['journal_requirements']}")
    else:
        print(f"❌ Validation failed: {result['error']}")


async def example_get_journal_info():
    """Example of getting journal information"""
    print("\n📚 Getting journal information...")
    
    formatter = JournalFormatterService()
    
    # Get all available journals
    result = await formatter.get_journal_styles({
        "action": "get_journal_styles"
    })
    
    if result["success"]:
        print(f"✅ Found {result['total_journals']} available journals:")
        for journal_name, journal_info in result["available_journals"].items():
            print(f"   - {journal_info['name']} ({journal_name})")
            print(f"     Publisher: {journal_info['publisher']}")
            print(f"     Impact Factor: {journal_info['impact_factor']}")
            print(f"     Abstract Limit: {journal_info['abstract_word_limit']} words")
            print(f"     Title Limit: {journal_info['title_word_limit']} words")
            print()
    else:
        print(f"❌ Failed to get journal info: {result['error']}")


async def main():
    """Run all journal formatting examples"""
    print("🚀 AXIOM META 4 - Journal Formatting Examples")
    print("=" * 60)
    
    try:
        # Run all examples
        await example_nature_formatting()
        await example_science_formatting()
        await example_journal_conversion()
        await example_journal_validation()
        await example_get_journal_info()
        
        print("\n" + "=" * 60)
        print("✅ All journal formatting examples completed successfully!")
        print("📁 Formatted manuscripts saved to: ./examples/journal_formats/")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
