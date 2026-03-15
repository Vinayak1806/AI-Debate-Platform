// ============================================================
// topics.js — Category grid + topic panel + search
// Loads all debate topics from topics-data.js and displays them
// as clickable cards. Clicking a category shows all its debate
// topics in a full-width panel below. Search filters inline.
// ============================================================

window.slugify = function(text) {
    return text.toLowerCase()
               .replace(/[^a-z0-9\s]/g, '')
               .replace(/\s+/g, '_');
};

document.addEventListener('DOMContentLoaded', function() {

    var data    = debateCategories;        // from topics-data.js
    var grid    = document.getElementById('category-grid');
    var panel   = document.getElementById('topic-panel');
    var panelTitle  = document.getElementById('panel-title');
    var panelGrid   = document.getElementById('topic-panel-grid');
    var closeBtn    = document.getElementById('panel-close-btn');
    var searchInput = document.getElementById('topic-search');
    var searchBtn   = document.querySelector('.search-btn');
    var searchResults     = document.getElementById('search-results');
    var searchResultsList = document.getElementById('search-results-list');

    var activeCategory = null;

    // ----------------------------------------------------------
    // 1. BUILD CATEGORY CARDS
    // ----------------------------------------------------------
    Object.keys(data).forEach(function(key) {
        var cat = data[key];
        var card = document.createElement('div');
        card.className = 'cat-card';
        card.setAttribute('data-key', key);
        card.innerHTML =
            '<span class="cat-emoji">' + cat.emoji + '</span>' +
            '<div class="cat-name">' + cat.title + '</div>' +
            '<div class="cat-count">' + cat.subtopics.length + ' topics</div>';

        card.addEventListener('click', function() {
            // If clicking the already-active card, close the panel
            if (activeCategory === key) {
                closePanel();
                return;
            }
            openCategory(key);
        });

        grid.appendChild(card);
    });

    // ----------------------------------------------------------
    // 2. OPEN A CATEGORY PANEL — shows debate topic links
    // ----------------------------------------------------------
    function openCategory(key) {
        var cat = data[key];

        // Mark the active card
        document.querySelectorAll('.cat-card').forEach(function(c) {
            c.classList.remove('active');
        });
        var activeCard = document.querySelector('[data-key="' + key + '"]');
        if (activeCard) activeCard.classList.add('active');

        // Populate the topic panel
        panelTitle.textContent = cat.emoji + '  ' + cat.title + '  (' + cat.subtopics.length + ' topics)';
        panelGrid.innerHTML = '';

        cat.subtopics.forEach(function(subtopic) {
            var slug = window.slugify(subtopic);
            var link = document.createElement('a');
            link.href = '/debate/' + slug;
            link.className = 'topic-link-card';
            link.textContent = subtopic;
            panelGrid.appendChild(link);
        });

        // Hide search results, show topic panel
        searchResults.style.display = 'none';
        panel.style.display = 'block';

        // Scroll panel into view smoothly
        panel.scrollIntoView({ behavior: 'smooth', block: 'nearest' });

        activeCategory = key;
    }

    // ----------------------------------------------------------
    // 3. CLOSE PANEL
    // ----------------------------------------------------------
    function closePanel() {
        panel.style.display = 'none';
        activeCategory = null;
        document.querySelectorAll('.cat-card').forEach(function(c) {
            c.classList.remove('active');
        });
    }

    closeBtn.addEventListener('click', closePanel);

    // ----------------------------------------------------------
    // 4. SEARCH — searches across ALL topics in all categories
    // ----------------------------------------------------------
    function runSearch() {
        var term = (searchInput ? searchInput.value.trim() : '').toLowerCase();

        if (!term) {
            // Clear search — restore grid
            searchResults.style.display = 'none';
            grid.style.display = '';
            // Re-open active category if there was one
            if (activeCategory) openCategory(activeCategory);
            return;
        }

        // Close the topic panel while searching
        panel.style.display = 'none';
        activeCategory = null;
        document.querySelectorAll('.cat-card').forEach(function(c) { c.classList.remove('active'); });

        // Search all categories
        searchResultsList.innerHTML = '';
        var totalMatches = 0;

        Object.keys(data).forEach(function(key) {
            var cat = data[key];
            var matches = cat.subtopics.filter(function(t) {
                return t.toLowerCase().includes(term);
            });

            if (matches.length === 0) return;
            totalMatches += matches.length;

            var section = document.createElement('div');
            section.className = 'search-result-section';
            section.innerHTML = '<h4>' + cat.emoji + ' ' + cat.title + ' (' + matches.length + ' match' + (matches.length > 1 ? 'es' : '') + ')</h4>';

            var topicGrid = document.createElement('div');
            topicGrid.className = 'search-result-topics';

            matches.forEach(function(subtopic) {
                var slug = window.slugify(subtopic);
                var link = document.createElement('a');
                link.href = '/debate/' + slug;
                link.className = 'topic-link-card';
                link.textContent = subtopic;
                topicGrid.appendChild(link);
            });

            section.appendChild(topicGrid);
            searchResultsList.appendChild(section);
        });

        if (totalMatches === 0) {
            searchResultsList.innerHTML = '<div class="no-results">No topics found for "' + searchInput.value.trim() + '"</div>';
        }

        searchResults.style.display = 'block';
        searchResults.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }

    if (searchInput) {
        searchInput.addEventListener('input', runSearch);
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') runSearch();
        });
    }
    if (searchBtn) searchBtn.addEventListener('click', runSearch);

    // ----------------------------------------------------------
    // 5. VOICE SEARCH (mic button)
    // ----------------------------------------------------------
    var micBtn = document.getElementById('mic-btn');
    if (micBtn && ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window)) {
        var SR = window.SpeechRecognition || window.webkitSpeechRecognition;
        micBtn.addEventListener('click', function() {
            var recognition = new SR();
            recognition.lang = 'en-US';
            micBtn.style.color = '#a855f7'; // highlight while listening
            recognition.onresult = function(e) {
                var spoken = e.results[0][0].transcript;
                if (searchInput) searchInput.value = spoken;
                micBtn.style.color = '';
                runSearch();
            };
            recognition.onerror = function() { micBtn.style.color = ''; };
            recognition.onend   = function() { micBtn.style.color = ''; };
            recognition.start();
        });
    }
});
