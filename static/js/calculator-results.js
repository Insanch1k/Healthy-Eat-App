const modalPairs = [
  ['myBtn', 'myModal'],
  ['myBtn1', 'myModal1'],
  ['myBtn2', 'myModal2'],
  ['myBtn3', 'myModal3'],
];

modalPairs.forEach(([buttonId, modalId]) => {
  const button = document.getElementById(buttonId);
  const modal = document.getElementById(modalId);
  if (!button || !modal) {
    return;
  }
  button.classList.add('icon-button');
  button.addEventListener('click', () => {
    modal.classList.add('is-open');
  });
  modal.addEventListener('click', (event) => {
    if (event.target === modal) {
      modal.classList.remove('is-open');
    }
  });
});
