// Site-wide chrome behaviour (safe to include on every page — each block
// no-ops if its elements aren't on the current page).

// Mobile menu toggle
(function(){
  var menuToggle = document.getElementById('menuToggle');
  var mobileNav = document.getElementById('mobileNav');
  if(!menuToggle || !mobileNav) return;
  menuToggle.addEventListener('click', function(){
    var isOpen = mobileNav.classList.toggle('nav-open');
    menuToggle.classList.toggle('open', isOpen);
    menuToggle.setAttribute('aria-expanded', String(isOpen));
  });
  mobileNav.querySelectorAll('a').forEach(function(a){
    a.addEventListener('click', function(){
      mobileNav.classList.remove('nav-open');
      menuToggle.classList.remove('open');
      menuToggle.setAttribute('aria-expanded', 'false');
    });
  });
})();

// Hero background parallax on scroll
(function(){
  var heroBg = document.querySelector('.hero-bg');
  if(!heroBg || window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
  window.addEventListener('scroll', function(){
    heroBg.style.transform = 'translateY(' + (window.scrollY * 0.15) + 'px)';
  }, {passive:true});
})();

// Path card 3D tilt
document.querySelectorAll('.path-card').forEach(function(card){
  card.addEventListener('mousemove', function(e){
    var r = card.getBoundingClientRect();
    var x = (e.clientX - r.left) / r.width - 0.5;
    var y = (e.clientY - r.top) / r.height - 0.5;
    card.style.transform = 'rotateY(' + (x*8) + 'deg) rotateX(' + (y*-8) + 'deg) translateY(-4px)';
  });
  card.addEventListener('mouseleave', function(){ card.style.transform = ''; });
});

// Reveal section headers as they scroll into view
if('IntersectionObserver' in window){
  var revealObs = new IntersectionObserver(function(entries){
    entries.forEach(function(en){
      if(en.isIntersecting){ en.target.classList.add('in'); revealObs.unobserve(en.target); }
    });
  }, {threshold:0.2});
  document.querySelectorAll('.section-head').forEach(function(el){ revealObs.observe(el); });
} else {
  document.querySelectorAll('.section-head').forEach(function(el){ el.classList.add('in'); });
}
