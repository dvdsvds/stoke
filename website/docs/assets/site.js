document.querySelectorAll(".side-group-toggle").forEach(function (btn) {
  btn.addEventListener("click", function () {
    btn.parentElement.classList.toggle("expanded");
  });
});
