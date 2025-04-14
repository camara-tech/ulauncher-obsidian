# Ulauncher Dependencies and Isolation Plan

## Direct Dependencies

### 1. `src/items.py`
- **Dependencies:**
  - `ulauncher.api.shared.item.ExtensionResultItem`
  - `ulauncher.api.shared.action.OpenAction`
  - `ulauncher.api.shared.action.ExtensionCustomAction`
- **Required Changes:**
  - Create a new `ResultItem` class to replace `ExtensionResultItem`
  - Create action classes to replace `OpenAction` and `ExtensionCustomAction`
  - Update all functions to use the new classes

### 2. `src/functions.py`
- **Dependencies:**
  - `ulauncher.utils.fuzzy_search.get_score`
- **Required Changes:**
  - Implement our own fuzzy search function or use a different library
  - Consider using `fuzzywuzzy` or `thefuzz` as alternatives

## Indirect Dependencies

### 1. Configuration
- **Current:**
  - Uses ulauncher's preferences system
  - Stored in `manifest.json`
- **Required Changes:**
  - Move to environment variables or a config file
  - Update configuration handling in `obsidian.py`

### 2. Plugin Structure
- **Current:**
  - Follows ulauncher's extension pattern
  - Uses ulauncher's event system
- **Required Changes:**
  - Implement pop-launcher's JSON IPC protocol
  - Create a simpler event handling system

## Action Plan

1. **Create New Base Classes**
   ```python
   class ResultItem:
       def __init__(self, name, description, icon, action):
           self.name = name
           self.description = description
           self.icon = icon
           self.action = action

   class OpenAction:
       def __init__(self, url):
           self.url = url

   class CustomAction:
       def __init__(self, data):
           self.data = data
   ```

2. **Update `items.py`**
   - Replace all ulauncher-specific classes with our new ones
   - Update function signatures to match new classes
   - Remove ulauncher-specific imports

3. **Update `functions.py`**
   - Replace fuzzy search implementation
   - Remove ulauncher-specific imports

4. **Update Configuration**
   - Move all configuration to environment variables
   - Remove `manifest.json` dependency
   - Update `plugin.ron` to reflect new configuration method

5. **Update Main Plugin**
   - Implement pop-launcher's JSON IPC protocol
   - Update event handling system
   - Remove ulauncher-specific code

## Notes
- The core Obsidian functionality (note searching, creation, etc.) is independent of ulauncher
- Most of the work is in replacing the UI/interface layer
- The fuzzy search implementation is the only significant algorithmic dependency 