let displayDiv = document.querySelector("#display")
let pos = { top: 0, left: 0, x: 0, y: 0 };

const mouseDownHandler = (e) => {
  // Change the cursor and prevent user from selecting the text
  displayDiv.style.cursor = 'grabbing';
  displayDiv.style.userSelect = 'none';

  pos = {
    // The current scroll
    left: displayDiv.scrollLeft,
    top: displayDiv.scrollTop,
    // Get the current mouse position
    x: e.clientX,
    y: e.clientY,
  };

  document.addEventListener('mousemove', mouseMoveHandler);
  document.addEventListener('mouseup', mouseUpHandler);
};

const mouseMoveHandler = (e) => {
  // How far the mouse has been moved
  const dx = e.clientX - pos.x;
  const dy = e.clientY - pos.y;

  // Scroll the element
  displayDiv.scrollTop = pos.top - dy;
  displayDiv.scrollLeft = pos.left - dx;
};

const mouseUpHandler = (e) => {
  document.removeEventListener('mousemove', mouseMoveHandler);
  document.removeEventListener('mouseup', mouseUpHandler);

  displayDiv.style.cursor = 'default';
  displayDiv.style.removeProperty('user-select');
};

document.querySelector("#display").addEventListener("mousedown", mouseDownHandler)
