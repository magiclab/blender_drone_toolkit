# blender_drone_toolkit
A collection of tools to help with the creation and export of flight path data in blender. 

## Import drone positions from YAML

  - install magiclab_uav_io add on in blender
  - Import UAV positions from magicLab tab (reads crazyflies.yaml)
  
## Import capture volume 

  - visualization of "fly zone" from optitrack motion capture system
  - use our separate app on your Optitrack system to create the captureVolume.ply
  
## Export waypoints as .CSV from Blender

  - create your choreography
  - select all objects you want to export
  - Export waypoints from magicLab tab (writes to .CSV format)
  
  For playback of generated file use sequence-player.py
