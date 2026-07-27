#!/usr/bin/env python3
"""
Resume Generator — generates HTML resume from JSON data.

Usage:
  python3 generate_resume.py --data resume_data.json [--template resume_template.html] [--output my_resume]

The script reads your resume data from a JSON file and injects it into
an HTML template. Open the resulting HTML in a browser and use Cmd+P
(or Ctrl+P) to save as PDF.

Data format:
  See references/resume_data_template.json for the expected JSON schema.

Template:
  The HTML template uses {{PLACEHOLDER}} syntax. The script replaces
  these placeholders with actual data from the JSON file.
"""

import sys
import os
import json
import argparse
import webbrowser
from pathlib import Path


def load_data(data_path):
    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_template(template_path):
    with open(template_path, 'r', encoding='utf-8') as f:
        return f.read()


def generate_summary_html(items):
    """Generate <li> items for the summary section."""
    return '\n'.join(f'    <li>{item}</li>' for item in items)


def generate_experience_html(experiences):
    """Generate experience section HTML."""
    html_parts = []
    for exp in experiences:
        details_html = '\n'.join(f'          <li>{d}</li>' for d in exp['details'])
        html_parts.append(f'''  <div class="exp-item">
    <div class="exp-header">
      <div>
        <span class="company">{exp['company']}</span>
        <span class="role">{exp['role']}</span>
      </div>
      <div class="date">{exp['date']}</div>
    </div>
    <div class="exp-detail">
      <ul>
{details_html}
      </ul>
    </div>
  </div>''')
    return '\n'.join(html_parts)


def generate_projects_html(projects):
    """Generate projects section HTML."""
    html_parts = []
    for proj in projects:
        details_html = '\n'.join(f'        <li>{d}</li>' for d in proj['details'])
        html_parts.append(f'''  <div class="proj-item">
    <div class="proj-header">{proj['name']} <span class="proj-role">{proj['role']} | {proj['date']}</span></div>
    <div class="proj-detail">
      <ul>
{details_html}
      </ul>
    </div>
  </div>''')
    return '\n'.join(html_parts)


def generate_skills_html(skills):
    """Generate skills section HTML with categories."""
    html_parts = []
    for category, tags in skills.items():
        tags_html = '\n'.join(f'      <span class="skill-tag">{tag}</span>' for tag in tags)
        display_name = category.replace('_', ' & ')
        html_parts.append(f'''  <div class="skill-category">
    <div class="label">{display_name}</div>
    <div class="skill-tags">
{tags_html}
    </div>
  </div>''')
    return '\n'.join(html_parts)


def generate_honors_html(items):
    """Generate honors list HTML."""
    return '\n'.join(f'    <li>{item}</li>' for item in items)


def fill_template(template, data):
    """Replace all {{PLACEHOLDER}} tags with actual data."""
    replacements = {
        '{{NAME}}': data.get('name', ''),
        '{{NAME_EN}}': data.get('name_en', ''),
        '{{TITLE}}': data.get('title', ''),
        '{{PHONE}}': data.get('phone', ''),
        '{{EMAIL}}': data.get('email', ''),
        '{{WEBSITE}}': data.get('website', ''),
        '{{GITHUB}}': data.get('github', ''),
        '{{SUMMARY_ITEMS}}': generate_summary_html(data.get('summary', [])),
        '{{EXPERIENCE_ITEMS}}': generate_experience_html(data.get('experience', [])),
        '{{PROJECT_ITEMS}}': generate_projects_html(data.get('projects', [])),
        '{{SKILL_ITEMS}}': generate_skills_html(data.get('skills', {})),
        '{{HONOR_ITEMS}}': generate_honors_html(data.get('honors', [])),
    }

    edu = data.get('education', {})
    replacements.update({
        '{{SCHOOL}}': edu.get('school', ''),
        '{{MAJOR}}': edu.get('major', ''),
        '{{DEGREE}}': edu.get('degree', ''),
        '{{EDU_DATE}}': edu.get('date', ''),
    })

    result = template
    for placeholder, value in replacements.items():
        result = result.replace(placeholder, value)

    return result


def main():
    parser = argparse.ArgumentParser(description='Generate HTML resume from JSON data')
    parser.add_argument('--data', required=True, help='Path to resume JSON data file')
    parser.add_argument('--template', help='Path to HTML template (default: auto-detect)')
    parser.add_argument('--output', default='resume', help='Output filename without extension (default: resume)')
    parser.add_argument('--no-open', action='store_true', help="Don't open browser after generation")
    args = parser.parse_args()

    # Auto-detect template path
    script_dir = Path(__file__).resolve().parent
    if args.template:
        template_path = args.template
    else:
        # Try references directory relative to script
        template_path = script_dir.parent / 'references' / 'resume_template.html'
        if not template_path.exists():
            # Try current directory
            template_path = Path('resume_template.html')

    template_path = str(template_path)

    if not os.path.exists(template_path):
        print(f"❌ Template not found: {template_path}")
        print("   Use --template to specify the path to your HTML template.")
        sys.exit(1)

    if not os.path.exists(args.data):
        print(f"❌ Data file not found: {args.data}")
        sys.exit(1)

    template = load_template(template_path)
    data = load_data(args.data)
    html = fill_template(template, data)

    # Write output
    output_dir = os.path.dirname(args.output) or '.'
    output_base = os.path.basename(args.output)
    output_path = os.path.join(output_dir, f"{output_base}.html")

    os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ Resume generated: {output_path}")

    if not args.no_open:
        webbrowser.open(f"file://{os.path.abspath(output_path)}")
        print("🌐 Opened in browser. Press Cmd+P (Mac) or Ctrl+P (Windows) to save as PDF.")


if __name__ == '__main__':
    main()
