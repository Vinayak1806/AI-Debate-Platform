// Dynamic topics loader and toggle
document.addEventListener('DOMContentLoaded', function() {
  // Load data
  const categoriesData = debateCategories; // from topics-data.js
  
  const topicsList = document.getElementById('topics-list');
  topicsList.className = 'categories-container';

window.categoryStates = {}; // Track shown count per category per session

  // Fisher-Yates shuffle
  function shuffle(array) {
    const shuffled = [...array];
    for (let i = shuffled.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [shuffled[i], shuffled[j]] = [shuffled[j], shuffled[i]];
    }
    return shuffled;
  }

  // Generate category HTML
  Object.keys(categoriesData).forEach(key => {
    const cat = categoriesData[key];
    categoryStates[key] = {
      shuffled: shuffle(cat.subtopics),
      shown: 0,
      batchSize: 10,
      total: cat.subtopics.length
    };
    
    const categoryDiv = document.createElement('div');
    categoryDiv.className = 'category-item';
    categoryDiv.dataset.category = key;
    categoryDiv.innerHTML = `
      <div class="category-header" onclick="toggleCategory('${key}')">
        <h3>${cat.emoji} ${cat.title} <span class="topic-count">(0/${categoryStates[key].total})</span></h3>
        <span class="toggle-icon">▼</span>
      </div>
      <div class="category-subtopics" id="subtopics-${key}">
        <div class="subtopics-grid" id="subtopics-grid-${key}"></div>
        <button class="load-more-btn" id="load-more-${key}" onclick="loadMore('${key}')">Load More Topics</button>
      </div>
    `;
    topicsList.appendChild(categoryDiv);
  });

  // Initial load first batch
  Object.keys(categoryStates).forEach(key => loadBatch(key));
});

// Load batch of topics
function loadBatch(key) {
  const state = window.categoryStates[key];
  const grid = document.getElementById(`subtopics-grid-${key}`);
  const loadBtn = document.getElementById(`load-more-${key}`);
  const countSpan = document.querySelector(`[data-category="${key}"] .topic-count`) || grid.closest('.category-item').querySelector('.topic-count');

  const start = state.shown;
  const end = Math.min(start + state.batchSize, state.total);
  
  for (let i = start; i < end; i++) {
    const subtopic = state.shuffled[i];
    const slug = window.slugify(subtopic);
    const topicDiv = document.createElement('div');
    topicDiv.className = 'topic-item';
    topicDiv.innerHTML = `<a href="/debate/${slug}" class="debate-link">${subtopic}</a>`;
    grid.appendChild(topicDiv);
  }

  state.shown = end;
  countSpan.textContent = `(${state.shown}/${state.total})`;

  if (end >= state.total) {
    loadBtn.style.display = 'none';
  }
}

// Load more handler
function loadMore(key) {
  loadBatch(key);
}

// Global toggle function (updated for new structure)
function toggleCategory(key) {
  const subtopics = document.getElementById(`subtopics-${key}`);
  const icon = event.target.closest('.category-header').querySelector('.toggle-icon');
  const loadBtn = document.getElementById(`load-more-${key}`);
  
  // Close others
  document.querySelectorAll('.category-subtopics').forEach(s => {
    if (s.id !== `subtopics-${key}`) {
      s.style.display = 'none';
    }
  });
  
  const isActive = subtopics.style.display !== 'none';
  
  if (isActive) {
    subtopics.style.display = 'none';
    icon.textContent = '▼';
  } else {
    subtopics.style.display = 'block';
    icon.textContent = '▲';
    if (window.categoryStates[key].shown < window.categoryStates[key].total) {
      loadBtn.style.display = 'block';
    }
  }
}

// Make categoryStates and slugify global
window.categoryStates = {};
window.slugify = function(text) {
  return text.toLowerCase().replace(/[^a-z0-9\s-]/g, '').replace(/\s+/g, '_').replace(/-+/g, '_');
};

// Search integration (updated for new structure)
function filterTopics(searchTerm) {
  const categories = document.querySelectorAll('.category-item');
  
  categories.forEach(cat => {
    const subtopicsDiv = cat.querySelector('.category-subtopics');
    const topics = cat.querySelectorAll('.topic-item');
    const headerText = cat.querySelector('h3').textContent.toLowerCase();
    
    let catHasMatch = headerText.includes(searchTerm.toLowerCase());
    
    topics.forEach(topic => {
      const text = topic.textContent.toLowerCase();
      if (text.includes(searchTerm.toLowerCase())) {
        topic.style.display = 'block';
        catHasMatch = true;
      } else {
        topic.style.display = 'none';
      }
    });
    
    cat.style.display = catHasMatch ? 'block' : 'none';
  });
  
  if (!searchTerm) {
    document.querySelectorAll('.category-subtopics').forEach(s => s.style.display = 'none');
  }
}

