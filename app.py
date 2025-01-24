import streamlit as st
from jinja2 import Environment, FileSystemLoader
import subprocess
import os
import base64
from PyPDF2 import PdfReader
from pdf2image import convert_from_bytes
from gemini_api import enhance_resume_sections  # Updated import

# Set page configuration
st.set_page_config(
    page_title="Resume Builder",
    page_icon=":briefcase:",
    layout="centered",
    initial_sidebar_state="auto",
)

st.title("Resume Builder App")

st.write("Fill in your details to generate your resume.")

# Sidebar for navigation
st.sidebar.title("Navigation")
nav = st.sidebar.radio("Go to", ["Build Resume", "About"])

if nav == "Build Resume":
    # Form for user input
    with st.form(key='resume_form'):
        st.header("Personal Information")
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone Number")

        with col2:
            address = st.text_input("Address")
            objective = st.text_area("Objective")

        st.header("Education")
        education = st.text_area("Education Details", help="Separate entries with new lines")

        st.header("Experience")
        experience = st.text_area("Work Experience", help="Separate entries with new lines")

        st.header("Skills")
        skills = st.text_area("Your Skills", help="Separate skills with commas")

        st.header("Projects")
        projects = st.text_area("Projects", help="Separate entries with new lines")

        submit = st.form_submit_button(label='Generate Resume')

    if submit:
        # Check if all fields are filled
        if not all([name, email, phone, address, objective, education, experience, skills, projects]):
            st.error("Please fill out all the fields.")
        else:
            with st.spinner('Enhancing your inputs using the Gemini LLM...'):
                try:
                    # Enhance all sections using the function from gemini_api.py
                    enhanced_sections = enhance_resume_sections(
                        objective, education, experience, skills, projects
                    )

                    st.success("Your inputs have been enhanced successfully!")

                except Exception as e:
                    st.error("An error occurred while enhancing your inputs.")
                    st.exception(e)
                    st.stop()  # Stop execution if there's an error

            with st.spinner('Generating your resume...'):
                # Create Jinja2 environment with custom delimiters
                env = Environment(
                    loader=FileSystemLoader('.'),
                    block_start_string='\BLOCK{',
                    block_end_string='}',
                    variable_start_string='\VAR{',
                    variable_end_string='}',
                    comment_start_string='\#',
                    comment_end_string='}',
                )
                template = env.get_template('templates/resume_template.tex')

                def escape_latex(text):
                    """
                    Escapes special LaTeX characters in the given text.
                    """
                    # Map of special LaTeX characters and their escaped versions
                    special_chars = {
                        '&': r'\&',
                        '%': r'\%',
                        '$': r'\$',
                        '#': r'\#',
                        '_': r'\_',
                        '{': r'\{',
                        '}': r'\}',
                        '~': r'\textasciitilde{}',
                        '^': r'\^{}',
                        '\\': r'\textbackslash{}',  # Correctly escape backslash
                        '<': r'\textless{}',
                        '>': r'\textgreater{}',
                        '|': r'\textbar{}',
                        '"': r"''",
                        '`': r'\textasciigrave{}',
                        "'": r"`",
                    }

                    # Escape each special character
                    for char, escape in special_chars.items():
                        text = text.replace(char, escape)
                    return text

                # Process user inputs for LaTeX formatting
                def format_list(text, itemize=False):
                    items = text.strip().split('\n')
                    if itemize:
                        formatted = '\n'.join([f'\\item {escape_latex(item.strip())}' for item in items if item.strip()])
                    else:
                        formatted = '\n'.join([escape_latex(item.strip()) for item in items if item.strip()])
                    return formatted

                # Escape LaTeX special characters in the enhanced text
# Get the enhanced inputs and escape LaTeX characters
                objective_enhanced = escape_latex(enhanced_sections['objective'])
                education_enhanced = escape_latex(enhanced_sections['education'])
                experience_enhanced = escape_latex(enhanced_sections['experience'])
                skills_enhanced = escape_latex(enhanced_sections['skills'])
                projects_enhanced = escape_latex(enhanced_sections['projects'])

# Proceed with formatting and rendering as before

                # Format the enhanced inputs
                # Format the enhanced inputs
                education_formatted = format_list(education_enhanced, itemize=True)
                experience_formatted = format_list(experience_enhanced, itemize=True)
                projects_formatted = format_list(projects_enhanced, itemize=True)
                skills_formatted = ', '.join([skill.strip() for skill in skills_enhanced.split(',') if skill.strip()])
                                # Render template with user data
                # Render template with user data
                latex_content = template.render(
                    name=escape_latex(name),
                    email=escape_latex(email),
                    phone=escape_latex(phone),
                    address=escape_latex(address),
                    objective=objective_enhanced,  # Already escaped
                    education=education_formatted,
                    experience=experience_formatted,
                    skills=skills_formatted,
                    projects=projects_formatted
                )

                # Save the rendered LaTeX content to a file
                with open("resume.tex", "w", encoding='utf-8') as f:
                    f.write(latex_content)

                # Compile LaTeX file to PDF
                try:
                    # Run pdflatex command
                    subprocess.run(['pdflatex', '-interaction=nonstopmode', 'resume.tex'], check=True)
                    # Read the PDF file
                    with open("resume.pdf", "rb") as pdf_file:
                        PDFbyte = pdf_file.read()

                    # Show PDF preview
                    st.header("Here is your generated resume:")
                    with st.expander("Preview Resume"):
                        images = convert_from_bytes(PDFbyte)
                        for image in images:
                            st.image(image, width=700)

                    # Download button
                    b64 = base64.b64encode(PDFbyte).decode()
                    href = f'<a href="data:application/octet-stream;base64,{b64}" download="resume.pdf">Download Resume PDF</a>'
                    st.markdown(href, unsafe_allow_html=True)

                except subprocess.CalledProcessError as e:
                    st.error("An error occurred while generating your resume.")
                    st.error("LaTeX Error:")
                    st.text(e.output)
                except Exception as e:
                    st.error("An unexpected error occurred.")
                    st.exception(e)
                finally:
                    # Clean up auxiliary files
                    aux_files = ['resume.aux', 'resume.log', 'resume.out', 'resume.tex']
                    for file in aux_files:
                        if os.path.exists(file):
                            os.remove(file)
else:
    st.header("About This App")
    st.write("This is a simple resume builder app built with Streamlit and LaTeX.")
    st.write("You can fill in your details, and it will generate a professional PDF resume for you.")