import os
import subprocess
import tempfile

def _run_js_generator(format_type: str, text: str, output_filename: str):
    """
    Helper to run the Node.js generator script.
    """
    # Create a temp file for content
    # We use a temp file to pass content to avoid command line length limits
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".txt", encoding='utf-8') as tmp_file:
        tmp_file.write(text)
        tmp_path = tmp_file.name
    
    # Path to the JS script
    # Assuming run from root project dir
    script_path = os.path.join("js_reports", "generate_report.js")
    
    try:
        # node js_reports/generate_report.js <format> <outputFile> <contentFile>
        cmd = ["node", script_path, format_type, output_filename, tmp_path]
        
        # Run node script
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        
    except subprocess.CalledProcessError as e:
        print(f"Error running JS generator: {e.stderr}")
        raise e
    except FileNotFoundError:
        print("Error: Node.js is not installed or 'node' command not found.")
        raise
    finally:
        # Cleanup temp file
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except:
                pass
            
    return output_filename

def create_pdf(text: str, filename: str):
    return _run_js_generator("pdf", text, filename)

def create_ppt(text: str, filename: str):
    # JS script handles pptx logic
    return _run_js_generator("ppt", text, filename)

def create_docx(text: str, filename: str):
    return _run_js_generator("docx", text, filename)

def create_markdown(text: str, filename: str):
    with open(filename, 'w') as f:
        f.write(text)
    return filename
