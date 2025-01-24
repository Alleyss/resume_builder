import streamlit as st
import google.generativeai as genai

# Configure the GenAI client with the API key from st.secrets
GOOGLE_API_KEY = st.secrets["GEMINI_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)

def enhance_resume_sections(objective, education, experience, skills, projects):
    """
    Enhances the given resume sections using the Gemini model.

    Args:
        objective (str): The user's objective.
        education (str): The user's education details.
        experience (str): The user's work experience details.
        skills (str): The user's skills.
        projects (str): The user's projects.

    Returns:
        dict: A dictionary containing the enhanced sections.
    """
    try:
        # Initialize the model
        model = genai.GenerativeModel('gemini-2.0-flash-exp')

        enhanced_sections = {}

        # Define prompts for each section with refined instructions
        sections = {
            'objective': objective,
            'education': education,
            'experience': experience,
            'skills': skills,
            'projects': projects
        }

        for section_name, content in sections.items():
            if content.strip():
                # Create the prompt for the current section
                prompt = create_prompt(section_name, content.strip())

                # Generate the enhanced content
                enhanced_text = generate_enhanced_text(model, prompt)
                if enhanced_text:
                    enhanced_sections[section_name] = enhanced_text.strip()
                else:
                    print(f"Failed to enhance section: {section_name}")
                    enhanced_sections[section_name] = content.strip()
            else:
                # If the content is empty, keep it as is
                enhanced_sections[section_name] = content.strip()

        return enhanced_sections

    except Exception as e:
        print(f"Exception in enhance_resume_sections: {e}")
        raise e

def create_prompt(section_name, content):
    """
    Creates a prompt for the LLM based on the section name and content.

    Args:
        section_name (str): The name of the section.
        content (str): The content to enhance.

    Returns:
        str: The generated prompt.
    """
    if section_name in ['objective', 'experience', 'projects']:
        base_prompt = ("As an expert resume writer, enhance the following {section} to be detailed, "
                       "ATS-friendly, and suitable for inclusion in a professional resume. Focus on including "
                       "relevant keywords, quantifiable achievements, and specific details. Do not include any "
                       "LaTeX commands, special characters, or unnecessary symbols. Output the enhanced {section} "
                       "without any additional explanations or remarks.")
    else:  # For 'skills' and 'education'
        base_prompt = ("As an expert resume writer, refine the following {section} to be concise and clear, "
                       "suitable for inclusion in a professional resume. Focus on clarity and brevity, ensuring "
                       "the most important information is highlighted. Do not include any LaTeX commands, special "
                       "characters, or unnecessary symbols. Output the refined {section} without any additional "
                       "explanations or remarks.")

    prompt = base_prompt.format(section=section_name)

    prompt += f"\n\nOriginal {section_name.capitalize()}:\n\"\"\"\n{content}\n\"\"\"\n\nEnhanced {section_name.capitalize()}:\n"

    return prompt

def generate_enhanced_text(model, prompt):
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        return text
    except Exception as e:
        print(f"Exception in generate_enhanced_text: {e}")
        return None