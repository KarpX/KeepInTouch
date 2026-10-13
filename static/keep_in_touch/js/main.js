/**
 * KeepInTouch - Пользовательский JavaScript проекта (ПР6)
 * Отвечает за динамическое поведение интерфейса.
 */

document.addEventListener("DOMContentLoaded", function () {
  // 1. Динамическое отображение текущего года в футере сайта
  const yearElement = document.getElementById("current-year");
  if (yearElement) {
    yearElement.textContent = new Date().getFullYear();
  }

  // 2. Автоматическое скрытие всплывающих сообщений через 5 секунд
  const alertMessages = document.querySelectorAll(".django-alert");
  if (alertMessages.length > 0) {
    setTimeout(function () {
      alertMessages.forEach(function (alert) {
        alert.style.transition = "opacity 0.4s ease, transform 0.4s ease";
        alert.style.opacity = "0";
        alert.style.transform = "translateY(-6px)";
        setTimeout(function () {
          alert.remove();
        }, 400);
      });
    }, 5000);
  }
});
