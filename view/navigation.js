let ele = document.querySelector("#display")
let pos = { top: 0, left: 0, x: 0, y: 0 };

const mouseDownHandler = (e) => {
  // Change the cursor and prevent user from selecting the text
  ele.style.cursor = 'grabbing';
  ele.style.userSelect = 'none';

  pos = {
    // The current scroll
    left: ele.scrollLeft,
    top: ele.scrollTop,
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
  ele.scrollTop = pos.top - dy;
  ele.scrollLeft = pos.left - dx;
};

const mouseUpHandler = (e) => {
  document.removeEventListener('mousemove', mouseMoveHandler);
  document.removeEventListener('mouseup', mouseUpHandler);

  ele.style.cursor = 'default';
  ele.style.removeProperty('user-select');
};

document.querySelector("#display").addEventListener("mousedown", mouseDownHandler)
