document.addEventListener('DOMContentLoaded', () => {
  // theme toggle
  const btn = document.getElementById('toggleTheme');
  btn.onclick = () => {
    const html = document.documentElement;
    html.dataset.theme = html.dataset.theme === 'dark' ? 'light' : 'dark';
  };

  // confetti on finish
  window.addEventListener('downloadDone', () => {
    // ✅ use the stable, production URL
    import('https://cdn.skypack.dev/canvas-confetti?min')
      .then(({ default: confetti }) =>
        confetti({ particleCount: 150, spread: 90, origin: { y: 0.6 } })
      );
  });
});
