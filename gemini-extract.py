# import google.generativeai as genai
from google import genai
from google.genai import types
# import google.ai.generativelanguage as glm # Not needed

import os
import sys
import json
from dotenv import load_dotenv
import time
import mimetypes
import pathlib # Import pathlib

# --- Configuration --- (Keep as is)
SYSTEM_PROMPT_FILE = "prompts/IE-sample-prompt.md"
INPUT_DIR = "pdf-data"
OUTPUT_DIR = "output-json"
MODEL_NAME = "gemini-1.5-flash" # Other models include "gemini-1.5-flash" or "gemini-2.0-flash" or "gemini-2.0-flash-lite"
SUPPORTED_EXTENSIONS = ('.pdf',)
API_CALL_DELAY_SECONDS = 20

# --- Helper Functions --- (Keep as is)
def load_file_content(filepath: str) -> str:
    # ... (same implementation)
    try:
        # Use pathlib here too for consistency
        return pathlib.Path(filepath).read_text(encoding='utf-8')
    except FileNotFoundError:
        print(f"Error: File not found at '{filepath}'")
        return None
    except Exception as e:
        print(f"Error reading file '{filepath}': {e}")
        return None

def save_json_to_file(filepath: str, data: dict or list):
    # ... (same implementation)
    path_obj = pathlib.Path(filepath)
    try:
        path_obj.parent.mkdir(parents=True, exist_ok=True) # Use pathlib for mkdir
        with path_obj.open('w', encoding='utf-8') as f: # Use pathlib open
            json.dump(data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Error writing JSON to file '{filepath}': {e}")

def save_error_file(filepath: str, error_info: dict):
    # ... (same implementation)
    path_obj = pathlib.Path(filepath)
    try:
        path_obj.parent.mkdir(parents=True, exist_ok=True)
        with path_obj.open('w', encoding='utf-8') as f:
             json.dump(error_info, f, indent=4, ensure_ascii=False)
    except Exception as e:
        print(f"Critical Error: Could not write error file to '{filepath}': {e}")


def validate_and_parse_json(json_string: str) -> dict or list or None:
    # ... (same implementation)
    try:
        cleaned_string = json_string.strip()
        if cleaned_string.startswith("```json"):
            cleaned_string = cleaned_string[7:]
        elif cleaned_string.startswith("```"):
             cleaned_string = cleaned_string[3:]
        if cleaned_string.endswith("```"):
            cleaned_string = cleaned_string[:-3]
        cleaned_string = cleaned_string.strip()
        if cleaned_string.lower() == "null":
             print("Warning: Received 'null' string instead of JSON object.")
             return None
        return json.loads(cleaned_string)
    except json.JSONDecodeError:
        print(f"JSON Decode Error. Raw text start: '{json_string[:100]}...'")
        return None
    except Exception as e:
        print(f"Unexpected error during JSON parsing prep: {e}")
        return None


# --- Main Execution ---

def main():
    # 1. Set up Gemini API (Keep as is)
    # ... (load_dotenv, configure API key) ...
    print("Configuring Gemini API...")
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY not found.")
        sys.exit(1)
    # try:
    #     genai.configure(api_key=api_key)
    #     print("Gemini API configured successfully.")
    # except Exception as e:
    #     print(f"Error configuring Gemini API: {e}")
    #     sys.exit(1)


    # --- Use pathlib for paths ---
    input_dir_path = pathlib.Path(INPUT_DIR)
    output_dir_path = pathlib.Path(OUTPUT_DIR)

    # Check Directories
    if not input_dir_path.is_dir():
        print(f"Error: Input directory '{INPUT_DIR}' not found or is not a directory.")
        sys.exit(1)
    output_dir_path.mkdir(exist_ok=True) # Use pathlib mkdir
    print(f"Output will be saved to: {OUTPUT_DIR}")

    # 2. Load system prompt (Keep as is, uses helper function which now uses pathlib)
    print(f"Loading system prompt file: {SYSTEM_PROMPT_FILE}")
    system_prompt = load_file_content(SYSTEM_PROMPT_FILE)
    if system_prompt is None:
        print(f"Error: Failed to load system prompt from '{SYSTEM_PROMPT_FILE}'.")
        sys.exit(1)

    # 3. Initialize Model (Keep as is)
    # ... (initialize GenerativeModel, GenerationConfig) ...
    print(f"Initializing model: {MODEL_NAME}")
    try:
        # model = genai.GenerativeModel(
        #     model_name=MODEL_NAME,
        #     system_instruction=system_prompt
        # )
        # generation_config = genai.types.GenerationConfig(
        #     response_mime_type="text/plain"
        # )
        client=genai.Client()
        print(f"Client for Model {MODEL_NAME} initialized.")
    except Exception as e:
        print(f"Error initializing Gemini model '{MODEL_NAME}': {e}")
        sys.exit(1)


    # 4. Process each PDF file
    print(f"\n--- Processing files in '{INPUT_DIR}' ---")
    processed_count = 0
    error_count = 0

    # --- Iterate using pathlib ---
    for input_filepath in input_dir_path.iterdir():
        # Check if it's a file and has the correct extension
        if not input_filepath.is_file() or not input_filepath.suffix.lower() in SUPPORTED_EXTENSIONS :
             continue

        filename = input_filepath.name # Get filename from path object
        print(f"\nProcessing file: {filename}...")

        base_filename = input_filepath.stem # Get filename without extension
        output_filepath = output_dir_path / f"{base_filename}.json" # Use pathlib / operator
        error_filepath = output_dir_path / f"{base_filename}_error.json"
        # output_filepath = output_dir_path / f"{base_filename}_{MODEL_NAME}.json"
        # error_filepath = output_dir_path / f"{base_filename}_{MODEL_NAME}_error.json"

        # --- Load PDF Data using pathlib --- REVISED SECTION ---
        try:
            # Read the raw bytes directly from the local PDF file using pathlib
            pdf_bytes = input_filepath.read_bytes()

            # Create the Part directly from bytes using the class method
            # pdf_part = genai.types.Part.from_bytes(
            # pdf_part = types.Part.from_bytes(
            #     mime_type="application/pdf",
            #     data=pdf_bytes
            # )
            print(f"  PDF data prepared for {filename} using Part.from_bytes ({len(pdf_bytes) / 1024:.2f} KB).")

        except Exception as e:
            # Catch errors during file reading or Part creation
            print(f"  Error reading or preparing PDF file {filename}: {e}")
            error_info = {
                "error": "Failed to read or prepare PDF file using pathlib/Part.from_bytes",
                "filename": filename,
                "exception_type": type(e).__name__,
                "details": str(e)
            }
            # Use helper function which now uses pathlib
            save_error_file(str(error_filepath), error_info) # Pass path as string to helper
            error_count += 1
            continue # Skip to the next file
        # --- END REVISED SECTION ---


        # --- 5. Call Gemini API with PDF (Keep as is) ---
        try:
            print(f"  Calling Gemini API for {filename}...")
            # response = model.generate_content(
            #     [pdf_part], # Content is the list containing the single PDF part
            #     generation_config=generation_config,
            #     # request_options={'timeout': 600} # Optional timeout
            # )
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=[
                    types.Part.from_bytes(
                        data=pdf_bytes,
                        mime_type='application/pdf',
                    ),
                    system_prompt])

            # Handle response (Keep as is)
            # if not response.parts:
            #      # ... (error handling for empty response) ...
            #      print(f"  Warning: Empty response for {filename}.")
            #      feedback = getattr(response, 'prompt_feedback', 'N/A')
            #      finish_reason = getattr(response, 'finish_reason', 'UNKNOWN')
            #      print(f"  Prompt Feedback: {feedback}")
            #      print(f"  Finish Reason: {finish_reason}")
            #      error_info = {
            #          "error": "No content generated by API", "filename": filename,
            #          "prompt_feedback": str(feedback), "finish_reason": str(finish_reason)
            #      }
            #      save_error_file(str(error_filepath), error_info) # Pass path as string
            #      error_count += 1
            #      continue

            raw_output_text = response.text

            # --- 6. Validate JSON and Save (Keep as is) ---
            parsed_json = validate_and_parse_json(raw_output_text)

            if parsed_json is not None:
                # ... (save valid JSON using helper function) ...
                 print(f"  Response is valid JSON. Saving to: {output_filepath}")
                 save_json_to_file(str(output_filepath), parsed_json) # Pass path as string
                 processed_count += 1
            else:
                # ... (save error for invalid JSON using helper function) ...
                print(f"  Warning: Response for {filename} is NOT valid JSON.")
                feedback = getattr(response, 'prompt_feedback', 'N/A')
                error_info = {
                    "error": "Invalid JSON format received from API", "filename": filename,
                    "raw_response": raw_output_text, "prompt_feedback": str(feedback)
                }
                save_error_file(str(error_filepath), error_info) # Pass path as string
                print(f"  Saving error details to: {error_filepath}")
                error_count += 1


        except Exception as e:
            # ... (handle API call errors using helper function) ...
            print(f"  An error occurred during the Gemini API call for {filename}: {e}")
            error_info = {
                 "error": "API call failed", "filename": filename,
                 "exception_type": type(e).__name__, "details": str(e)
            }
            if hasattr(e, 'response') and hasattr(e.response, 'prompt_feedback'):
                 error_info["prompt_feedback"] = str(e.response.prompt_feedback)
            save_error_file(str(error_filepath), error_info) # Pass path as string
            print(f"  Saving error details to: {error_filepath}")
            error_count += 1


        # Delay (Keep as is)
        if API_CALL_DELAY_SECONDS > 0:
            time.sleep(API_CALL_DELAY_SECONDS)

    # --- Summary (Keep as is) ---
    print("\n--- Batch PDF Processing Summary ---")
    # ... (print summary) ...
    print(f"Successfully processed and saved JSON: {processed_count}")
    print(f"Files with errors (details saved):   {error_count}")
    total_attempted = processed_count + error_count
    print(f"Total PDF files attempted:          {total_attempted}")
    print(f"Check the '{OUTPUT_DIR}' directory for results and error details.")
    print("-" * 35)


if __name__ == "__main__":
    main()