// Convert PNG screenshots to 30-second MP4 videos with Ken Burns effect
const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const VIDEO_DIR = path.join(__dirname, '..', 'videos');

// Create animated zoom effect using ffmpeg
const files = fs.readdirSync(VIDEO_DIR).filter(f => f.endsWith('.png'));

files.forEach(png => {
  const mp4 = png.replace('.png', '.mp4');
  const input = path.join(VIDEO_DIR, png);
  const output = path.join(VIDEO_DIR, mp4);
  
  // Ken Burns slow zoom-in effect, 30 seconds
  const cmd = `ffmpeg -y -loop 1 -i "${input}" -vf "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,zoompan=z='min(zoom+0.0005,1.2)':d=750:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920" -c:v libx264 -t 30 -pix_fmt yuv420p "${output}"`;
  
  try {
    execSync(cmd, { stdio: 'pipe' });
    console.log(`  ✅ ${mp4}`);
  } catch(e) {
    console.log(`  ⚠️ ${png} ffmpeg error (try: winget install ffmpeg)`);
  }
});

console.log('Done!');
