const { YoutubeTranscript } = require('youtube-transcript');

const videoId = '2a9Lx9J8uSs';

async function getTranscript() {
  try {
    console.log('Fetching transcript for video:', videoId);
    const transcript = await YoutubeTranscript.fetchTranscript(videoId);
    
    // Combine all text segments
    const fullText = transcript.map(t => t.text).join(' ');
    
    console.log('\n=== TRANSCRIPT ===\n');
    console.log(fullText);
    console.log('\n=== END TRANSCRIPT ===');
    console.log('\nTotal segments:', transcript.length);
    console.log('Approximate duration:', Math.round(transcript[transcript.length-1]?.offset / 1000 / 60), 'minutes');
    
  } catch (error) {
    console.error('Error fetching transcript:', error.message);
  }
}

getTranscript();
