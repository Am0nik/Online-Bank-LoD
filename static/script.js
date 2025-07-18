

function adjustMainPadding() {
      const header = document.querySelector('header');
      const main = document.querySelector('main');
      const height = header.offsetHeight;
      main.style.paddingTop = height + 'px';
    }
window.addEventListener('load', adjustMainPadding);
window.addEventListener('resize', adjustMainPadding);
