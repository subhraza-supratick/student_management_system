// script.js

// Smooth fade-in animation for all pages
document.addEventListener("DOMContentLoaded", () => {
  document.body.classList.add("fade-in");
});

// Toast auto-dismiss after 3 seconds
const toastElList = [].slice.call(document.querySelectorAll('.toast'));
const toastList = toastElList.map(toastEl => {
  const toast = new bootstrap.Toast(toastEl);
  toast.show();
  setTimeout(() => toast.hide(), 3000);
});
