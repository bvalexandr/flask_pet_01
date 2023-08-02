// Настройки для Bootstrap
var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
  return new bootstrap.Tooltip(tooltipTriggerEl)
})
// 

function copyLink() {
    link = document.querySelector('#link')
    navigator.clipboard.writeText(link.placeholder)
}

const copyIcon = document.querySelector('#copyIcon')
if (copyIcon) {
  copyIcon.addEventListener('click', copyLink)
}