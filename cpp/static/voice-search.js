class VoiceSearch {
  constructor(inputId) {
    this.input = document.getElementById(inputId);
    this.micBtn = document.getElementById('mic-btn');
    this.recognition = null;
    this.isListening = false;

    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      this.recognition = new SpeechRecognition();
      this.recognition.continuous = false;
      this.recognition.interimResults = true;
      this.recognition.lang = 'en-US';

      this.recognition.onstart = () => {
        this.isListening = true;
        this.micBtn.classList.add('listening');
      };

      this.recognition.onresult = (event) => {
        let finalTranscript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript;
          } else {
            this.input.value = transcript;
          }
        }
        if (finalTranscript) {
          this.input.value = finalTranscript;
          // Trigger search on final result
          const event = new Event('input', { bubbles: true });
          this.input.dispatchEvent(event);
        }
      };

      this.recognition.onend = () => {
        this.isListening = false;
        this.micBtn.classList.remove('listening');
      };

      this.recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        this.micBtn.classList.remove('listening');
        this.isListening = false;
      };

      this.micBtn?.addEventListener('click', () => this.toggle());
    } else {
      if (this.micBtn) {
        this.micBtn.style.display = 'none';
      }
      console.warn('Speech recognition not supported');
    }
  }

  toggle() {
    if (this.isListening) {
      this.recognition.stop();
    } else {
      this.recognition.start();
    }
  }
}


