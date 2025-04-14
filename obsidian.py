#!/usr/bin/env python3
import json
import sys
import os
import logging
from pathlib import Path
from src.functions import (
    append_to_note_in_vault,
    find_note_in_vault,
    find_string_in_vault,
    create_note_in_vault,
    generate_daily_url,
    generate_url,
)
import datetime

# Setup logging
log_dir = Path.home() / ".local" / "state" / "pop-launcher-obsidian"
log_dir.mkdir(parents=True, exist_ok=True)
log_file = log_dir / "obsidian.log"

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stderr)
    ]
)

logger = logging.getLogger(__name__)

# Configuration
VAULT_PATH = os.getenv("OBSIDIAN_VAULT_PATH", "~/Documents/Notes")
QUICK_CAPTURE_NOTE = os.getenv("OBSIDIAN_QUICK_CAPTURE_NOTE", "_reminder.md")
NUMBER_OF_NOTES = int(os.getenv("OBSIDIAN_NUMBER_OF_NOTES", "8"))

logger.info(f"Starting plugin with VAULT_PATH={VAULT_PATH}, QUICK_CAPTURE_NOTE={QUICK_CAPTURE_NOTE}")

# Command prefixes
PREFIX_SEARCH_NOTE = "on"
PREFIX_SEARCH_STRING = "of"
PREFIX_OPEN_DAILY = "od"
PREFIX_QUICK_CAPTURE = "oc"

class ObsidianPlugin:
    def __init__(self):
        self.state = "default"
        self.content = ""
        logger.info("Initializing ObsidianPlugin")
        self.process_requests()

    def reset(self):
        logger.debug("Resetting plugin state")
        self.state = "default"
        self.content = ""

    def send_response(self, response):
        try:
            logger.debug(f"Sending response: {response}")
            print(json.dumps(response))
            sys.stdout.flush()
        except BrokenPipeError:
            logger.warning("Broken pipe error while sending response")
            # Ignore broken pipe errors - they happen when the launcher closes
            pass

    def process_requests(self):
        logger.info("Starting request processing loop")
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    logger.info("Received empty line, exiting")
                    break
                
                logger.debug(f"Received request: {line}")
                request = json.loads(line)
                self.handle_request(request)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode JSON: {e}")
                continue
            except Exception as e:
                logger.error(f"Error processing request: {e}", exc_info=True)
                try:
                    self.send_response({"Error": str(e)})
                except:
                    logger.error("Failed to send error response", exc_info=True)
                    sys.exit(1)

    def handle_request(self, request):
        logger.debug(f"Handling request: {request}")
        if "Search" in request:
            query = request["Search"]
            logger.info(f"Processing search query: {query}")
            self.handle_search(query)
        elif "Activate" in request:
            logger.info(f"Processing activate request: {request['Activate']}")
            self.handle_activate(request["Activate"])
        elif "Exit" in request:
            logger.info("Received exit request")
            sys.exit(0)
        elif "Interrupt" in request:
            logger.info("Received interrupt request - resetting state")
            self.reset()
            # Don't exit, just reset state and continue processing
            return

        self.send_response("Finished")

    def handle_search(self, query):
        if not query:
            logger.debug("Empty query received")
            return

        # Clear previous results
        self.send_response("Clear")

        # Handle different search types based on prefix
        if query.startswith(f"{PREFIX_SEARCH_NOTE} "):
            search_term = query[len(PREFIX_SEARCH_NOTE) + 1:]
            logger.info(f"Note search: {search_term}")
            notes = find_note_in_vault(VAULT_PATH, search_term)
            self.send_notes_results(notes, search_term)
        elif query.startswith(f"{PREFIX_SEARCH_STRING} "):
            search_term = query[len(PREFIX_SEARCH_STRING) + 1:]
            logger.info(f"String search: {search_term}")
            notes = find_string_in_vault(VAULT_PATH, search_term)
            self.send_notes_results(notes, search_term)
        elif query.startswith(f"{PREFIX_OPEN_DAILY} "):
            logger.info("Opening daily note")
            self.send_response({
                "Append": {
                    "id": 0,
                    "name": "Open Daily Note",
                    "description": "Open today's daily note",
                    "icon": {"Name": "calendar-today"}
                }
            })
        elif query.startswith(f"{PREFIX_QUICK_CAPTURE} "):
            self.state = "quick-capture"
            self.content = query[len(PREFIX_QUICK_CAPTURE) + 1:]
            logger.info(f"Quick capture mode activated with content: {self.content}")
            # Show the quick capture note as the only option
            quick_capture_path = os.path.join(VAULT_PATH, QUICK_CAPTURE_NOTE)
            self.send_response({
                "Append": {
                    "id": 0,
                    "name": "Quick Capture",
                    "description": f"Append to {QUICK_CAPTURE_NOTE}",
                    "icon": {"Name": "text-x-markdown"}
                }
            })

    def send_notes_results(self, notes, query):
        logger.debug(f"Sending {len(notes)} notes for query: {query}")
        for i, note in enumerate(notes[:NUMBER_OF_NOTES]):
            self.send_response({
                "Append": {
                    "id": i,
                    "name": note.name,
                    "description": note.path,
                    "icon": {"Name": "text-x-markdown"}
                }
            })
        
        # Only show create note option when not in quick capture mode
        if query and self.state != "quick-capture-to-note":
            self.send_response({
                "Append": {
                    "id": NUMBER_OF_NOTES,
                    "name": f"Create Note: {query}",
                    "description": "Create a new note with this name",
                    "icon": {"Name": "document-new"}
                }
            })

    def handle_activate(self, id):
        logger.info(f"Handling activate for id: {id}")
        if self.state == "quick-capture":
            quick_capture_path = os.path.join(VAULT_PATH, QUICK_CAPTURE_NOTE)
            # Get current time in HH:MM:SS format
            timestamp = datetime.datetime.now().strftime("%H:%M:%S")
            # Prepend timestamp to content
            timestamped_content = f"{timestamp} {self.content}"
            logger.info(f"Appending to quick capture note: {timestamped_content}")
            append_to_note_in_vault(VAULT_PATH, quick_capture_path, timestamped_content)
            self.reset()
            self.send_response("Close")
        else:
            if id == NUMBER_OF_NOTES:
                logger.info(f"Creating new note: {self.content}")
                path = create_note_in_vault(VAULT_PATH, self.content)
                url = generate_url(VAULT_PATH, path)
                self.send_response({
                    "DesktopEntry": {
                        "path": url,
                        "gpu_preference": "Default"
                    }
                })
            else:
                note = find_note_in_vault(VAULT_PATH, "")[id]
                logger.info(f"Opening note: {note.path}")
                url = generate_url(VAULT_PATH, note.path)
                self.send_response({
                    "DesktopEntry": {
                        "path": url,
                        "gpu_preference": "Default"
                    }
                })

if __name__ == "__main__":
    ObsidianPlugin() 
