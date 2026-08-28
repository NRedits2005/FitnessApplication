document.addEventListener('DOMContentLoaded', () => {
  const select = document.getElementById('id_exercise');
  const details = document.getElementById('selection-details');
  const weightField = document.getElementById('weight-field');
  const cards = [...document.querySelectorAll('.exercise-card')];
  const update = (card) => {
    select.value = card.dataset.id;
    const bodyweight = card.dataset.bodyweight === 'true';
    weightField.hidden = bodyweight;
    document.getElementById('id_weight').disabled = bodyweight;
    details.innerHTML = `<img src="${card.querySelector('img').src}" alt="${card.querySelector('img').alt}"><div><h3>${card.querySelector('h3').textContent}</h3><p>${card.dataset.description}</p><p><strong>How to perform it:</strong> ${card.dataset.instructions}</p><p><strong>Targets:</strong> ${card.dataset.muscles}</p><p><strong>Beginner tip:</strong> ${card.dataset.tips}</p></div>`;
    cards.forEach(item => item.classList.toggle('selected', item === card));
  };
  cards.forEach(card => card.querySelector('.select-exercise').addEventListener('click', () => update(card)));
  select.addEventListener('change', () => { const card = cards.find(item => item.dataset.id === select.value); if (card) update(card); });
  document.getElementById('exercise-search').addEventListener('input', (event) => filter(event.target.value.toLowerCase()));
  let category = 'All';
  const filter = (term = document.getElementById('exercise-search').value.toLowerCase()) => cards.forEach(card => card.hidden = !(card.dataset.name.includes(term) && (category === 'All' || card.dataset.category === category)));
  document.querySelectorAll('.filter').forEach(button => button.addEventListener('click', () => { category = button.dataset.category; document.querySelectorAll('.filter').forEach(x => x.classList.toggle('active', x === button)); filter(); }));
});
