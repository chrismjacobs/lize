/* ─────────────────────────────────────────────
   Li-Ze Academy — Vue.js app
   All Vue components live here and are mounted
   on individual pages by the base template.
   ───────────────────────────────────────────── */

// ── Wake-up screen ──────────────────────────────────────────────────────────
// Shows while Render is waking up from sleep; dismissed once /health responds.

function initWakeScreen() {
  const screen = document.getElementById('wake-screen');
  if (!screen) return;

  const start = Date.now();
  const MIN_DISPLAY = 1000; // always show for at least 1s to avoid flash

  function dismiss() {
    const elapsed = Date.now() - start;
    const delay = Math.max(0, MIN_DISPLAY - elapsed);
    setTimeout(() => {
      screen.style.opacity = '0';
      screen.style.transition = 'opacity 0.5s ease';
      setTimeout(() => screen.remove(), 500);
    }, delay);
  }

  function poll() {
    fetch('/health')
      .then(r => { if (r.ok) dismiss(); else setTimeout(poll, 2000); })
      .catch(() => setTimeout(poll, 2000));
  }

  // If the page loaded quickly, the backend is up — dismiss fast
  if (performance.now() < 2000) {
    dismiss();
  } else {
    poll();
  }
}

document.addEventListener('DOMContentLoaded', initWakeScreen);


// ── Fill-rate bars ─────────────────────────────────────────────────────────
// Animate fill bars on page load (they start at width:0 and animate to data-pct)

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('.fill-bar-inner[data-pct]').forEach(el => {
    const pct = parseInt(el.getAttribute('data-pct'), 10);
    requestAnimationFrame(() => {
      el.style.width = pct + '%';
    });
  });
});


// ── Flash message auto-dismiss ─────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  setTimeout(() => {
    document.querySelectorAll('.auto-dismiss').forEach(el => {
      el.style.opacity = '0';
      el.style.transition = 'opacity 0.5s ease';
      setTimeout(() => el.remove(), 500);
    });
  }, 4000);
});


// ── Audio Recorder (journal form) ─────────────────────────────────────────
// Uses the browser's MediaRecorder API — no libraries needed.

const AudioRecorder = {
  mediaRecorder: null,
  chunks: [],
  stream: null,
  blob: null,

  init() {
    const btn = document.getElementById('record-btn');
    const status = document.getElementById('record-status');
    const preview = document.getElementById('audio-preview');
    const hiddenInput = document.getElementById('audio-data-input');
    const timerEl = document.getElementById('record-timer');

    if (!btn) return; // not on journal page

    let timerInterval = null;
    let seconds = 0;

    function formatTime(s) {
      const m = Math.floor(s / 60).toString().padStart(2, '0');
      const sec = (s % 60).toString().padStart(2, '0');
      return `${m}:${sec}`;
    }

    btn.addEventListener('click', async () => {
      if (this.mediaRecorder && this.mediaRecorder.state === 'recording') {
        this.mediaRecorder.stop();
        return;
      }

      try {
        this.stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        this.chunks = [];

        const mimeType = MediaRecorder.isTypeSupported('audio/webm')
          ? 'audio/webm'
          : 'audio/mp4';

        this.mediaRecorder = new MediaRecorder(this.stream, { mimeType });

        this.mediaRecorder.ondataavailable = e => {
          if (e.data.size > 0) this.chunks.push(e.data);
        };

        this.mediaRecorder.onstop = () => {
          this.blob = new Blob(this.chunks, { type: mimeType });
          const url = URL.createObjectURL(this.blob);
          preview.src = url;
          preview.style.display = 'block';
          status.textContent = 'Recording saved. You can re-record or keep it.';
          btn.classList.remove('recording');
          btn.innerHTML = '🎙';
          clearInterval(timerInterval);
          timerEl.textContent = '';

          this.stream.getTracks().forEach(t => t.stop());

          // Convert blob to base64 and store in hidden input for form submission
          const reader = new FileReader();
          reader.onloadend = () => {
            hiddenInput.value = reader.result;
          };
          reader.readAsDataURL(this.blob);
        };

        this.mediaRecorder.start();
        btn.classList.add('recording');
        btn.innerHTML = '⏹';
        status.textContent = 'Recording... tap again to stop.';

        seconds = 0;
        timerInterval = setInterval(() => {
          seconds++;
          timerEl.textContent = formatTime(seconds);
        }, 1000);

      } catch (err) {
        status.textContent = 'Microphone access denied or unavailable.';
        console.error(err);
      }
    });
  }
};

document.addEventListener('DOMContentLoaded', () => AudioRecorder.init());


// ── Journal form — intercept submit to attach audio blob ─────────────────
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('journal-form');
  if (!form) return;

  form.addEventListener('submit', async (e) => {
    if (!AudioRecorder.blob) return; // no recording, submit normally

    e.preventDefault();
    const fd = new FormData(form);

    // Replace the base64 placeholder with the actual blob file
    fd.delete('audio');
    const ext = AudioRecorder.blob.type.includes('webm') ? 'webm' : 'mp4';
    fd.append('audio', AudioRecorder.blob, `recording.${ext}`);

    const res = await fetch(form.action, { method: 'POST', body: fd });
    // Follow the redirect that Flask returns
    window.location.href = res.url;
  });
});


// ── Photo share toggle (journal form) ─────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  const photoInput = document.getElementById('photo-input');
  const shareSection = document.getElementById('share-photo-section');
  if (!photoInput || !shareSection) return;

  photoInput.addEventListener('change', () => {
    shareSection.style.display = photoInput.files.length ? 'block' : 'none';
  });
});


// ── Staff: confirm delete ──────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-confirm]').forEach(el => {
    el.addEventListener('click', e => {
      const msg = el.getAttribute('data-confirm');
      if (!confirm(msg)) e.preventDefault();
    });
  });
});
