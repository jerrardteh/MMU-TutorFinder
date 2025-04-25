const tutors = [
  {
    name: 'Jonathan P.',
    price: 105,
    rating: 5.0,
    subject: 'english',
    time: 'morning',
    img: 'jonathan.jpg',
    description: 'Experienced English tutor with 10+ years teaching.',
    category: 'Language',
    intro: 'Hello! I’m Jonathan, passionate about helping you achieve fluency.'
  },
  {
    name: 'Craig G.',
    price: 131,
    rating: 4.5,
    subject: 'english',
    time: 'evening',
    img: 'craig.jpg',
    description: 'IELTS and TOEFL preparation expert.',
    category: 'Language',
    intro: 'Let’s make English fun and practical together!'
  },
  {
    name: 'Alice M.',
    price: 45,
    rating: 4.8,
    subject: 'math',
    time: 'afternoon',
    img: 'alice.jpg',
    description: 'Math tutor focused on algebra and calculus.',
    category: 'STEM',
    intro: 'I love helping students see how fun math can be!'
  }
];

const container = document.getElementById('tutorContainer');
const searchInput = document.getElementById('searchInput');
const priceSelect = document.getElementById('priceSelect');
const subjectSelect = document.getElementById('subjectSelect');
const timeSelect = document.getElementById('timeSelect');
const sortSelect = document.getElementById('sortSelect');
const priceRange = document.getElementById('priceRange');

function render(list) {
  container.innerHTML = '';
  list.forEach(t => {
    const card = document.createElement('div');
    card.className = 'card';
    card.dataset.price = t.price < 20 ? 'low' : t.price <= 50 ? 'mid' : 'high';
    card.dataset.subject = t.subject;
    card.dataset.time = t.time;

    card.innerHTML = `
      <img src="${t.img}" alt="Photo of ${t.name}">
      <div class="info">
        <h3>${t.name}</h3>
        <p class="rating">★ ${t.rating.toFixed(1)}</p>
        <p>Category: ${t.category}</p>
        <p>Subject: ${capitalize(t.subject)}</p>
        <p>Description: ${t.description}</p>
        <p>Available: ${capitalize(t.time)}</p>
        <p><em>${t.intro}</em></p>
        <div class="buttons">
          <button>Book trial lesson</button>
          <button>Send message</button>
        </div>
      </div>`;

    container.appendChild(card);
  });
}

function applyFilters() {
  const text = searchInput.value.toLowerCase();
  const priceCat = priceSelect.value;
  const subjectCat = subjectSelect.value;
  const timeCat = timeSelect.value;
  const maxPrice = +priceRange.value;

  let filtered = tutors.filter(t => {
    const matchText = t.name.toLowerCase().includes(text);
    const matchPriceCat = !priceCat || ((t.price < 20 ? 'low' : t.price <= 50 ? 'mid' : 'high') === priceCat);
    const matchSubject = !subjectCat || t.subject === subjectCat;
    const matchTime = !timeCat || t.time === timeCat;
    const matchRange = t.price <= maxPrice;
    return matchText && matchPriceCat && matchSubject && matchTime && matchRange;
  });

  const sortBy = sortSelect.value;
  filtered.sort((a, b) => {
    if (sortBy === 'rating') return b.rating - a.rating;
    if (sortBy === 'priceAsc') return a.price - b.price;
    if (sortBy === 'priceDesc') return b.price - a.price;
    return 0;
  });

  render(filtered);
}

function capitalize(str) {
  return str.charAt(0).toUpperCase() + str.slice(1);
}

[searchInput, priceSelect, subjectSelect, timeSelect, sortSelect, priceRange]
  .forEach(el => el.addEventListener(el.tagName === 'INPUT' && el.type === 'search' ? 'input' : 'change', applyFilters));

render(tutors);
