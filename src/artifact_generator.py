import os
from datetime import datetime
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

class ArtifactGenerator:
    def __init__(self, output_dir: str = "artifacts"):
        self.output_dir = output_dir
        self.llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.2)
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_artifact(self, phase: str, description: str, project: str, client: str) -> str:
        """Generate a structured document based on the detected SDLC phase using LLM & templates."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        feature_name = description[:30] + "..." if len(description) > 30 else description

        # 1. Ask LLM to flesh out phase-specific content points
        content_details = self._get_llm_content(phase, description)

        # 2. Select and format the template based on phase
        template = self._get_phase_template(phase)
        
        document_text = template.format(
            project=project,
            client=client,
            feature_name=feature_name,
            description=description,
            date=date_str,
            content_details=content_details
        )

        # 3. Save to an organized folder structure (e.g., artifacts/requirements/)
        phase_folder = os.path.join(self.output_dir, phase.lower())
        os.makedirs(phase_folder, exist_ok=True)
        
        safe_project_name = "".join(c if c.isalnum() else "_" for c in project)
        filename = f"{safe_project_name}_{phase.lower()}_doc.md"
        filepath = os.path.join(phase_folder, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(document_text)

        return filepath

    def _get_llm_content(self, phase: str, description: str) -> str:
        """Use LLM to generate relevant sub-points for the template."""
        prompt = f"""Based on this feature request: "{description}"
Generate 3 to 4 bullet points appropriate for the '{phase}' phase of SDLC. Keep them concise, professional, and practical."""

        try:
            response = self.llm.invoke(prompt)
            return response.content.strip()
        except Exception:
            return "- Analyze request details\n- Coordinate with team\n- Prepare next steps"

    def _get_phase_template(self, phase: str) -> str:
        """Return the markdown template corresponding to the SDLC phase."""
        phase = phase.lower()
        
        templates = {
            "requirements": """# Requirements Document

**Project:** {project}  
**Client:** {client}  
**Date:** {date}  

## Description:
{description}

## Key Requirements & User Stories:
{content_details}

## Next Steps:
- Review with stakeholders and sign off
- Transition to the design phase
""",
            "design": """# Technical Design Outline

**Project:** {project}  
**Client:** {client}  
**Date:** {date}  

## Feature Scope:
{description}

## Architecture & Design Specifications:
{content_details}

## Review Checklist:
- [ ] Security implications checked
- [ ] UI/UX wireframes aligned
""",
            "implementation": """# Implementation Task List

**Project:** {project}  
**Client:** {client}  
**Date:** {date}  

## Task Overview for:
{description}

## Development Steps & Code Tasks:
{content_details}

## Definition of Done:
- [ ] Code written and peer-reviewed
- [ ] Unit tests added
""",
            "testing": """# Testing & QA Plan

**Project:** {project}  
**Client:** {client}  
**Date:** {date}  

## Feature Under Test:
{description}

## Test Cases & Validation Scenarios:
{content_details}

## Sign-off Criteria:
- [ ] All test cases passing
- [ ] Zero critical bugs reported
""",
            "deployment": """# Deployment & Release Checklist

**Project:** {project}  
**Client:** {client}  
**Date:** {date}  

## Release Target:
{description}

## Deployment Steps & Verification:
{content_details}

## Post-Release Monitoring:
- [ ] Monitor system logs and error rates
- [ ] Confirm client notification
"""
        }
        
        # Default fallback template if phase is unmatched
        return templates.get(phase, templates["requirements"])