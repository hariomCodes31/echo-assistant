import os
import base64
import string
from glob import glob
from groq import Groq
from dotenv import load_dotenv

# Load env variables
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Ensure required directories exist
os.makedirs("screenshots", exist_ok=True)
os.makedirs("images", exist_ok=True)


def get_mime_type(filepath):
    """Determine MIME type based on file extension."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext in [".jpg", ".jpeg"]:
        return "image/jpeg"
    elif ext == ".webp":
        return "image/webp"
    return "image/png"


def is_filepath(target):
    """Determine if a target string is likely a file path/name."""
    if "/" in target or "\\" in target or ":" in target:
        return True
    # Check for typical image extension
    _, ext = os.path.splitext(target.lower())
    if ext in [".png", ".jpg", ".jpeg", ".webp", ".bmp", ".gif"]:
        return True
    return False


def parse_vision_command(command):
    """
    Parse user command to determine if it is a vision command.
    Returns a dict with 'type', 'prompt', and optional 'path', or None if not matched.
    """
    # Clean command: lowercase, strip whitespace, and remove trailing punctuation
    cmd = command.lower().strip()
    while cmd and cmd[-1] in string.punctuation:
        cmd = cmd[:-1].strip()

    # Define words that refer to the active image or screenshots
    active_image_terms = [
        "image", "this image", "the image", "that image", "my image", 
        "uploaded image", "current image", "active image",
        "picture", "this picture", "the picture", "that picture", 
        "photo", "this photo", "the photo", "that photo"
    ]
    
    screenshot_terms = [
        "screenshot", "this screenshot", "the screenshot"
    ]

    # 1. Exact match / simple term matches first
    if cmd in active_image_terms:
        return {
            "type": "general",
            "prompt": "Describe this image in detail."
        }
        
    if cmd in screenshot_terms:
        return {
            "type": "screenshot",
            "prompt": (
                "Analyze this screenshot in detail. Identify visual elements, "
                "overall layout structure, potential text, and describe what is visible."
            )
        }

    # 2. Check "describe <target>"
    if cmd.startswith("describe "):
        target = cmd[9:].strip().strip('"\'')
        # If target points to active image terms or contains them (and isn't a filepath)
        if target in active_image_terms or (any(term in target for term in ["image", "picture", "photo"]) and not is_filepath(target)):
            return {
                "type": "general",
                "prompt": "Describe this image in detail."
            }
        elif target in screenshot_terms or ("screenshot" in target and not is_filepath(target)):
            return {
                "type": "screenshot",
                "prompt": (
                    "Analyze this screenshot in detail. Identify visual elements, "
                    "overall layout structure, potential text, and describe what is visible."
                )
            }
        else:
            # Treat as file path
            original_path = command[9:].strip().strip('"\'')
            return {
                "type": "filepath",
                "path": original_path,
                "prompt": "Describe this image in detail."
            }

    # 3. Check "analyze <target>"
    if cmd.startswith("analyze "):
        target = cmd[8:].strip().strip('"\'')
        if target in active_image_terms or (any(term in target for term in ["image", "picture", "photo"]) and not is_filepath(target)):
            return {
                "type": "general",
                "prompt": "Analyze this image in detail and describe what you see."
            }
        elif target in screenshot_terms or ("screenshot" in target and not is_filepath(target)):
            return {
                "type": "screenshot",
                "prompt": (
                    "Analyze this screenshot in detail. Identify visual elements, "
                    "overall layout structure, potential text, and describe what is visible."
                )
            }
        else:
            # Treat as file path
            original_path = command[8:].strip().strip('"\'')
            return {
                "type": "filepath",
                "path": original_path,
                "prompt": "Analyze this image in detail and describe what you see."
            }

    # 4. Check other commands on the current active image
    if cmd == "read text":
        return {
            "type": "ocr",
            "prompt": "Perform OCR on this image. Extract and list all visible text exactly as it appears. If no text is found, state that."
        }

    if cmd == "how many people":
        return {
            "type": "count_people",
            "prompt": "Count the number of people in this image. Explain your count."
        }

    if cmd == "what objects are there":
        return {
            "type": "objects",
            "prompt": "Identify and list all major objects in this image, along with their general locations."
        }

    if cmd == "what color is the shirt":
        return {
            "type": "color",
            "prompt": "What color is the shirt in this image? Identify the primary colors of shirts worn by people."
        }

    # 5. Check other questions or statements about the image
    if "image" in cmd or "picture" in cmd or "photo" in cmd:
        return {
            "type": "general",
            "prompt": f"Answer this question about the image: {command}"
        }

    # 6. Check for keyword-based vision intents (UI Analysis, Error Detection, Face/Emotion Detection)
    # UI components & forms
    if any(keyword in cmd for keyword in ["ui analysis", "ui components", "detect ui", "buttons", "menus", "forms"]):
        return {
            "type": "ui_analysis",
            "prompt": (
                "Analyze the user interface components in this image. "
                "Identify and describe any buttons, menus, forms, input fields, and other layout elements, "
                "specifying their locations and design."
            )
        }

    # Error & bugs detection
    if any(keyword in cmd for keyword in ["error", "warning", "bug", "console", "stack trace"]):
        return {
            "type": "error_detection",
            "prompt": (
                "Scan this image for any errors, warnings, visual bugs, console logs, stack traces, "
                "or broken UI elements. Report any issues you find in detail."
            )
        }

    # Face & emotion detection
    if any(keyword in cmd for keyword in ["face", "faces", "emotion", "emotions", "expression"]):
        return {
            "type": "faces_emotions",
            "prompt": (
                "Detect any faces in this image. For each face, describe its approximate location, "
                "expression, and detect the person's emotions if possible."
            )
        }

    return None


def get_image_source(command_type, file_path=None):
    """
    Locate and load image bytes based on the command and fallbacks.
    Returns (image_bytes, source_info_or_error_msg, mime_type).
    """
    # Case A: Specific file path requested
    if command_type == "filepath" and file_path:
        if os.path.exists(file_path):
            try:
                with open(file_path, "rb") as f:
                    return f.read(), file_path, get_mime_type(file_path)
            except Exception as e:
                return None, f"❌ Error reading file at {file_path}: {str(e)}", "image/png"
        return None, f"❌ File not found at path: {file_path}", "image/png"

    # Case B: Screenshot command requested
    if command_type == "screenshot":
        screenshots = glob("screenshots/*.png") + glob("screenshots/*.jpg") + glob("screenshots/*.jpeg")
        if not screenshots:
            return None, "❌ No screenshots found in 'screenshots' folder.", "image/png"
        latest_screenshot = max(screenshots, key=os.path.getmtime)
        try:
            with open(latest_screenshot, "rb") as f:
                return f.read(), latest_screenshot, get_mime_type(latest_screenshot)
        except Exception as e:
            return None, f"❌ Error reading screenshot: {str(e)}", "image/png"

    # Case C: General/current image commands - check sources in priority order:
    # 1. Streamlit Uploaded Image (from session state)
    try:
        import streamlit as st
        if "uploaded_image" in st.session_state and st.session_state.uploaded_image:
            mime_type = st.session_state.get("uploaded_image_mime", "image/png")
            return st.session_state.uploaded_image, "Uploaded Image", mime_type
    except Exception:
        pass

    # 2. Newest image inside the 'images' folder
    images_folder = "images"
    image_patterns = [
        os.path.join(images_folder, "*.png"),
        os.path.join(images_folder, "*.jpg"),
        os.path.join(images_folder, "*.jpeg"),
        os.path.join(images_folder, "*.webp")
    ]
    image_files = []
    for pattern in image_patterns:
        image_files.extend(glob(pattern))

    if image_files:
        latest_image = max(image_files, key=os.path.getmtime)
        try:
            with open(latest_image, "rb") as f:
                return f.read(), latest_image, get_mime_type(latest_image)
        except Exception as e:
            return None, f"❌ Error reading latest image from folder: {str(e)}", "image/png"

    # 3. Fallback to newest screenshot from 'screenshots' folder
    screenshots = glob("screenshots/*.png") + glob("screenshots/*.jpg") + glob("screenshots/*.jpeg")
    if screenshots:
        latest_screenshot = max(screenshots, key=os.path.getmtime)
        try:
            with open(latest_screenshot, "rb") as f:
                return f.read(), latest_screenshot, get_mime_type(latest_screenshot)
        except Exception as e:
            return None, f"❌ Error reading screenshot fallback: {str(e)}", "image/png"

    return None, "❌ No active image found. Please upload an image, place one in the 'images' folder, or take a screenshot.", "image/png"


def analyze_screenshot(command):
    """
    Main entry point for handling vision commands.
    Maintains backward compatibility with original function signature.
    """
    parsed = parse_vision_command(command)
    if not parsed:
        return None

    # Retrieve image bytes and source information
    img_bytes, source_info, mime_type = get_image_source(
        parsed["type"],
        file_path=parsed.get("path")
    )

    if img_bytes is None:
        return source_info  # Return the error message

    try:
        # Encode image to base64
        image_data = base64.b64encode(img_bytes).decode()

        # Send to Groq Vision API (using Llama 4 Scout model)
        response = client.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": parsed["prompt"]
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:{mime_type};base64,{image_data}"
                            }
                        }
                    ]
                }
            ],
            temperature=0.2,
            max_tokens=1024
        )
        return f"[Source: {os.path.basename(source_info)}]\n\n{response.choices[0].message.content}"

    except Exception as e:
        return f"❌ Error calling Groq Vision API: {str(e)}"