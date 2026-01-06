document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('tts-form');
    const textInput = document.getElementById('text-input');
    const charCount = document.getElementById('char-count');
    const convertBtn = document.getElementById('convert-btn');
    const btnText = convertBtn.querySelector('.btn-text');
    const btnLoading = convertBtn.querySelector('.btn-loading');
    const errorMessage = document.getElementById('error-message');
    const subtitlesCheckbox = document.getElementById('subtitles-checkbox');
    const voiceSelect = document.getElementById('voice-select');

    // Load available voices
    loadVoices();

    // Update character count
    textInput.addEventListener('input', function() {
        charCount.textContent = this.value.length;
    });

    // Handle form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();

        const text = textInput.value.trim();
        if (!text) {
            showError('Please enter some text to convert.');
            return;
        }

        // Show loading state
        setLoading(true);
        hideError();

        try {
            const includeSubtitles = subtitlesCheckbox.checked;
            const selectedVoice = voiceSelect.value;

            const formData = new FormData();
            formData.append('text', text);
            formData.append('voice', selectedVoice);
            formData.append('subtitles', includeSubtitles);

            const response = await fetch('/api/convert', {
                method: 'POST',
                body: formData
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Conversion failed');
            }

            // Get the blob and trigger download
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = includeSubtitles ? 'speech.zip' : 'speech.mp3';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            window.URL.revokeObjectURL(url);

        } catch (error) {
            showError(error.message);
        } finally {
            setLoading(false);
        }
    });

    async function loadVoices() {
        try {
            const response = await fetch('/api/voices');
            if (!response.ok) {
                throw new Error('Failed to load voices');
            }

            const voices = await response.json();

            // Group voices by language
            const grouped = {};
            for (const voice of voices) {
                const lang = voice.locale;
                if (!grouped[lang]) {
                    grouped[lang] = [];
                }
                grouped[lang].push(voice);
            }

            // Build dropdown with optgroups
            voiceSelect.innerHTML = '';

            // Add English voices first (most common use case)
            const englishLocales = Object.keys(grouped).filter(k => k.startsWith('en-')).sort();
            const otherLocales = Object.keys(grouped).filter(k => !k.startsWith('en-')).sort();

            for (const locale of [...englishLocales, ...otherLocales]) {
                const optgroup = document.createElement('optgroup');
                optgroup.label = locale;

                for (const voice of grouped[locale]) {
                    const option = document.createElement('option');
                    option.value = voice.name;
                    option.textContent = `${voice.name.split('-').pop().replace('Neural', '')} (${voice.gender})`;

                    // Set default voice
                    if (voice.name === 'en-US-ChristopherNeural') {
                        option.selected = true;
                    }

                    optgroup.appendChild(option);
                }

                voiceSelect.appendChild(optgroup);
            }

        } catch (error) {
            console.error('Failed to load voices:', error);
            voiceSelect.innerHTML = '<option value="en-US-ChristopherNeural">Default (Christopher)</option>';
        }
    }

    function setLoading(loading) {
        convertBtn.disabled = loading;
        voiceSelect.disabled = loading;
        btnText.style.display = loading ? 'none' : 'inline';
        btnLoading.style.display = loading ? 'inline' : 'none';
    }

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
    }

    function hideError() {
        errorMessage.style.display = 'none';
    }
});
