#!/bin/bash

# Create a temporary SVG file with a modern icon design
cat > temp.svg << 'EOF'
<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg" width="1024" height="1024" viewBox="0 0 1024 1024">
  <!-- Background -->
  <rect x="0" y="0" width="1024" height="1024" rx="200" ry="200" fill="#007AFF"/>
  
  <!-- Plugin icon -->
  <g transform="translate(512,512) scale(0.6)">
    <!-- Plugin body -->
    <path d="M-300,-300 L300,-300 L300,300 L-300,300 Z" 
          fill="white" stroke="none"/>
    
    <!-- Plugin prongs -->
    <rect x="-100" y="-400" width="200" height="100" fill="white"/>
    <rect x="-100" y="300" width="200" height="100" fill="white"/>
    <rect x="-400" y="-100" width="100" height="200" fill="white"/>
    <rect x="300" y="-100" width="100" height="200" fill="white"/>
    
    <!-- Center circle -->
    <circle cx="0" cy="0" r="150" fill="#007AFF"/>
    
    <!-- Inner details -->
    <path d="M-50,-50 L50,-50 L50,50 L-50,50 Z" 
          fill="white" stroke="none"/>
  </g>
</svg>
EOF

# Convert SVG to PNG files of different sizes
mkdir -p ico_temp
for size in 16 32 48 64 128 256; do
  magick convert -background none -resize ${size}x${size} temp.svg "ico_temp/icon_${size}x${size}.png"
done

# Create ICO file with multiple sizes
magick convert ico_temp/icon_*.png app.ico

# Clean up
rm -rf ico_temp temp.svg
