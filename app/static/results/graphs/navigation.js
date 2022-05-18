let graphContainer = document.querySelector("#graph-container")
let pos = { top: 0, left: 0, x: 0, y: 0 };

const mouseDownHandler = (e) => {
  // Change the cursor and prevent user from selecting the text
  graphContainer.style.cursor = 'grabbing';
  graphContainer.style.userSelect = 'none';

  pos = {
    // The current scroll
    left: graphContainer.scrollLeft,
    top: graphContainer.scrollTop,
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
  graphContainer.scrollTop = pos.top - dy;
  graphContainer.scrollLeft = pos.left - dx;
};

const mouseUpHandler = (e) => {
  document.removeEventListener('mousemove', mouseMoveHandler);
  document.removeEventListener('mouseup', mouseUpHandler);

  graphContainer.style.cursor = 'default';
  graphContainer.style.removeProperty('user-select');
};

document.querySelector("#graph-container").addEventListener("mousedown", mouseDownHandler)
