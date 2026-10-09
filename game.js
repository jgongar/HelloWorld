/*
  GAME.JS - Snake, controlled by swiping (or arrow keys on a computer)
  ====================================================================
  The board is a GRID x GRID set of cells. The snake is a list of cells.
  Every "tick" the snake moves one cell; eating food makes it longer
  and speeds the game up. Hitting a wall or yourself ends the game.
*/
(function () {
  var GRID = 18;                 // cells per side
  var START_DELAY = 150;         // ms per move at the start
  var MIN_DELAY = 70;            // fastest allowed

  var canvas = document.getElementById('game');
  var ctx = canvas.getContext('2d');
  var overlay = document.getElementById('overlay');
  var titleEl = document.getElementById('title');
  var messageEl = document.getElementById('message');
  var scoreEl = document.getElementById('score');
  var bestEl = document.getElementById('best');

  var snake, dir, nextDir, food, score, delay, timer, running;
  var best = 0;
  // localStorage can be blocked (e.g. private browsing), so always try/catch
  try { best = parseInt(localStorage.getItem('snake-best'), 10) || 0; } catch (e) {}
  bestEl.textContent = best;

  // Size the board to fit the screen, and keep the canvas sharp on Retina displays
  var cell = 20;
  function resize() {
    var size = Math.floor(Math.min(window.innerWidth - 32, window.innerHeight - 200, 520) / GRID) * GRID;
    size = Math.max(size, GRID * 10);
    document.documentElement.style.setProperty('--board-size', size + 'px');
    var dpr = window.devicePixelRatio || 1;
    canvas.width = size * dpr;
    canvas.height = size * dpr;
    cell = canvas.width / GRID;
    draw();
  }

  function reset() {
    var mid = Math.floor(GRID / 2);
    snake = [{ x: mid, y: mid }, { x: mid - 1, y: mid }, { x: mid - 2, y: mid }];
    dir = { x: 1, y: 0 };
    nextDir = dir;
    score = 0;
    delay = START_DELAY;
    scoreEl.textContent = 0;
    placeFood();
  }

  function placeFood() {
    // Pick random cells until we find one the snake isn't on
    do {
      food = { x: Math.floor(Math.random() * GRID), y: Math.floor(Math.random() * GRID) };
    } while (snake.some(function (s) { return s.x === food.x && s.y === food.y; }));
  }

  function start() {
    reset();
    overlay.classList.add('hidden');
    running = true;
    clearTimeout(timer);
    tick();
  }

  function tick() {
    if (!running) return;
    dir = nextDir;
    var head = { x: snake[0].x + dir.x, y: snake[0].y + dir.y };

    var hitWall = head.x < 0 || head.y < 0 || head.x >= GRID || head.y >= GRID;
    var hitSelf = snake.some(function (s) { return s.x === head.x && s.y === head.y; });
    if (hitWall || hitSelf) return gameOver();

    snake.unshift(head);
    if (head.x === food.x && head.y === food.y) {
      score++;
      scoreEl.textContent = score;
      delay = Math.max(MIN_DELAY, delay - 3);
      if (navigator.vibrate) navigator.vibrate(15);
      placeFood();
    } else {
      snake.pop();            // didn't eat: remove the tail so length stays the same
    }
    draw();
    timer = setTimeout(tick, delay);
  }

  function gameOver() {
    running = false;
    if (navigator.vibrate) navigator.vibrate(60);
    if (score > best) {
      best = score;
      bestEl.textContent = best;
      try { localStorage.setItem('snake-best', best); } catch (e) {}
    }
    titleEl.textContent = 'Game over';
    messageEl.textContent = 'Score ' + score + '. Tap to play again.';
    overlay.classList.remove('hidden');
  }

  function draw() {
    if (!snake) reset();
    ctx.fillStyle = '#0f172a';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    // Food
    ctx.fillStyle = '#f87171';
    ctx.beginPath();
    ctx.arc((food.x + 0.5) * cell, (food.y + 0.5) * cell, cell * 0.38, 0, Math.PI * 2);
    ctx.fill();
    // Snake (head is brighter)
    snake.forEach(function (s, i) {
      ctx.fillStyle = i === 0 ? '#86efac' : '#4ade80';
      var pad = cell * 0.06;
      ctx.fillRect(s.x * cell + pad, s.y * cell + pad, cell - pad * 2, cell - pad * 2);
    });
  }

  // Turn, but never straight back into yourself
  function turn(x, y) {
    if (x === -dir.x && y === -dir.y) return;
    nextDir = { x: x, y: y };
  }

  // ----- Controls -----
  var startX = 0, startY = 0, touching = false;

  document.addEventListener('touchstart', function (e) {
    var t = e.touches[0];
    startX = t.clientX; startY = t.clientY; touching = true;
  }, { passive: true });

  // preventDefault stops Safari from scrolling/bouncing the page while swiping
  document.addEventListener('touchmove', function (e) { e.preventDefault(); }, { passive: false });

  document.addEventListener('touchend', function (e) {
    if (!touching) return;
    touching = false;
    var t = e.changedTouches[0];
    var dx = t.clientX - startX, dy = t.clientY - startY;
    if (Math.abs(dx) < 24 && Math.abs(dy) < 24) {      // a tap, not a swipe
      if (!running) start();
      return;
    }
    if (!running) return;
    if (Math.abs(dx) > Math.abs(dy)) turn(dx > 0 ? 1 : -1, 0);
    else turn(0, dy > 0 ? 1 : -1);
  });

  document.addEventListener('keydown', function (e) {
    var keys = { ArrowUp: [0, -1], ArrowDown: [0, 1], ArrowLeft: [-1, 0], ArrowRight: [1, 0] };
    if (keys[e.key]) { e.preventDefault(); if (running) turn(keys[e.key][0], keys[e.key][1]); }
    else if (e.key === ' ' || e.key === 'Enter') { if (!running) start(); }
  });

  // Clicking works too (desktop), but ignore the click iOS fires after a touch
  overlay.addEventListener('click', function () { if (!running && !touching) start(); });

  window.addEventListener('resize', resize);
  resize();
})();
