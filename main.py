"""
CLI Entry Point for Engineering Freelance AI Agent.
"""

import argparse
import json
import sys
from pathlib import Path

from modules.intake import EngineeringIntake
from config.manager import ConfigManager


def main():
    parser = argparse.ArgumentParser(
        description="Engineering Freelance AI Agent - Module 1: Intake System"
    )
    parser.add_argument(
        "job_text",
        nargs="?",
        help="Job description text to parse"
    )
    parser.add_argument(
        "-f", "--file",
        help="Path to file containing job description"
    )
    parser.add_argument(
        "--config",
        action="store_true",
        help="Show current configuration"
    )
    parser.add_argument(
        "--save-log",
        action="store_true",
        default=True,
        help="Save intake to audit log (default: True)"
    )
    
    args = parser.parse_args()
    
    # Handle config display
    if args.config:
        config = ConfigManager()
        print("Current Configuration:")
        print(json.dumps(config.get_masked_config(), indent=2))
        return
    
    # Get job text
    job_text = args.job_text
    
    if args.file:
        file_path = Path(args.file)
        if file_path.exists():
            job_text = file_path.read_text(encoding="utf-8")
        else:
            print(f"Error: File not found: {args.file}")
            sys.exit(1)
    
    if not job_text:
        parser.print_help()
        print("\nExample usage:")
        print('  python main.py "Need pile foundation design for residential building in Mumbai"')
        print("  python main.py -f job.txt")
        return
    
    # Process job
    print("Processing job...")
    config = ConfigManager()
    llm_client = config.create_llm_client()
    
    intake = EngineeringIntake(
        raw_text=job_text,
        llm_client=llm_client,
        llm_provider=config.get_llm_provider(),
        base_url=config.get_llm_base_url()
    )
    
    result = intake.parse_to_structured()
    
    # Display results
    print("\n" + "=" * 60)
    print("CLASSIFICATION")
    print("=" * 60)
    print(f"Job Type: {result['classification']['job_type']}")
    print(f"Jurisdiction: {result['classification']['jurisdiction']}")
    print(f"Confidence: {result['classification']['confidence']}")
    
    print("\n" + "=" * 60)
    print("REQUIRED CODES")
    print("=" * 60)
    for code in result['required_codes']['codes']:
        print(f"  [{code['priority'].upper()}] {code['code_id']}: {code['title']}")
    print(f"Source: {result['required_codes']['source']}")
    
    print("\n" + "=" * 60)
    print("REQUIREMENTS")
    print("=" * 60)
    print("Deliverables:")
    for d in result['requirements']['deliverables']:
        print(f"  - {d}")
    print("\nMissing Inputs:")
    for inp in result['requirements']['required_inputs_missing']:
        print(f"  - {inp}")
    lic = result['requirements']['licensing']
    print(f"\nLicense Required: {lic['requires_license']}")
    if lic['requires_license']:
        print(f"License Type: {lic['license_type']}")
    
    print("\n" + "=" * 60)
    print("RISK ASSESSMENT")
    print("=" * 60)
    print(f"Overall Risk: {result['risk_assessment']['overall_risk'].upper()}")
    for flag in result['risk_assessment']['flags']:
        print(f"  - {flag}")
    
    print("\n" + "=" * 60)
    print("NEXT ACTIONS")
    print("=" * 60)
    print(f"First Step: {result['next_actions']['recommended_first_step']}")
    print("\nClarifying Questions:")
    for q in result['next_actions']['clarifying_questions']:
        print(f"  - {q}")
    
    print("\n" + "=" * 60)
    print("COMPLIANCE")
    print("=" * 60)
    print(result['compliance']['disclaimer'])
    
    # Save log
    if args.save_log:
        log_file = intake.save_intake_log()
        print(f"\nLog saved to: {log_file}")


if __name__ == "__main__":
    main()
