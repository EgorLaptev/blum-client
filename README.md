# BLUM Client

This document provides a detailed explanation of the configuration parameters for the Blum Client, which helps to carry out automatic farming.

## Configuration Parameters

### Interact

- **interact**: A boolean flag to enable or disable interaction.
  - **Type**: Boolean
  - **Default**: `false`

### Detect

The `detect` section includes parameters related to object detection using HSV color space and other detection criteria.

- **detect**: An object containing detection settings.
  - **hsv**: An object containing HSV color ranges for different object types.
    - **blum**: HSV range for detecting "blum".
      - **lower**: The lower bound of the HSV range.
        - **Type**: Array of 3 integers
        - **Default**: `[40, 100, 100]`
      - **upper**: The upper bound of the HSV range.
        - **Type**: Array of 3 integers
        - **Default**: `[80, 255, 255]`
    - **bomb**: HSV range for detecting "bomb".
      - **lower**: The lower bound of the HSV range.
        - **Type**: Array of 3 integers
        - **Default**: `[0, 0, 87]`
      - **upper**: The upper bound of the HSV range.
        - **Type**: Array of 3 integers
        - **Default**: `[179, 35, 255]`
    - **ice**: HSV range for detecting "ice".
      - **lower**: The lower bound of the HSV range.
        - **Type**: Array of 3 integers
        - **Default**: `[88, 0, 97]`
      - **upper**: The upper bound of the HSV range.
        - **Type**: Array of 3 integers
        - **Default**: `[122, 220, 255]`
  - **types**: An array of object types to detect.
    - **Type**: Array of strings
    - **Default**: `["blum", "ice", "bomb"]`
  - **safe_distance**: The safe distance to maintain from detected objects.
    - **Type**: Integer
    - **Default**: `40`
  - **minimal_area**: The minimal area required for an object to be considered detected.
    - **Type**: Integer
    - **Default**: `60`
  - **frequency**: The frequency of detection.
    - **Type**: Integer
    - **Default**: `0`

### Window

The `window` section specifies the dimensions and position of the window for processing.

- **window**: An object containing window settings.
  - **left**: The x-coordinate of the top-left corner of the window.
    - **Type**: Integer
    - **Default**: `0`
  - **top**: The y-coordinate of the top-left corner of the window.
    - **Type**: Integer
    - **Default**: `300`
  - **width**: The width of the window.
    - **Type**: Integer
    - **Default**: `580`
  - **height**: The height of the window.
    - **Type**: Integer
    - **Default**: `650`

### Render

The `render` section includes settings for rendering the detected objects.

- **render**: An object containing rendering settings.
  - **layers**: An array of layers to render.
    - **Type**: Array of strings
    - **Default**: `["screenshot", "centers", "mask:blum", "mask:bomb", "mask:ice"]`
  - **blum**: Rendering settings for "blum" objects.
    - **color**: The color to use for rendering "blum".
      - **Type**: Array of 3 integers (RGB)
      - **Default**: `[0, 255, 0]`
    - **radius**: The radius of the marker for "blum".
      - **Type**: Integer
      - **Default**: `5`
  - **bomb**: Rendering settings for "bomb" objects.
    - **color**: The color to use for rendering "bomb".
      - **Type**: Array of 3 integers (RGB)
      - **Default**: `[0, 0, 255]`
    - **radius**: The radius of the marker for "bomb".
      - **Type**: Integer
      - **Default**: `5`
  - **ice**: Rendering settings for "ice" objects.
    - **color**: The color to use for rendering "ice".
      - **Type**: Array of 3 integers (RGB)
      - **Default**: `[255, 255, 0]`
    - **radius**: The radius of the marker for "ice".
      - **Type**: Integer
      - **Default**: `5`

---