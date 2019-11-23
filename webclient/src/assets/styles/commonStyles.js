export const drawerWidthOpen = 260;
export const drawerWidthClosed = 84;
export const primaryColor = ['#9c27b0', '#ab47bc', '#8e24aa', '#af2cc5'];
export const warningColor = ['#ff9800', '#ffa726', '#fb8c00', '#ffa21a'];
export const dangerColor = ['#f44336', '#ef5350', '#e53935', '#f55a4e'];
export const successColor = ['#4caf50', '#66bb6a', '#43a047', '#5cb860'];
export const infoColor = ['#00acc1', '#26c6da', '#00acc1', '#00d3ee'];
export const roseColor = ['#e91e63', '#ec407a', '#d81b60', '#eb3573'];
export const grayColor = [
  '#999',
  '#777',
  '#3C4858',
  '#AAAAAA',
  '#D2D2D2',
  '#DDD',
  '#b4b4b4',
  '#555555',
  '#333',
  '#a9afbb',
  '#eee',
  '#e7e7e7',
];
export const blackColor = '#000';
export const whiteColor = '#FFF';
export const hexToRgb = (input) => {
  let out = input.replace('#', '');
  const hexRegex = /[0-9A-Fa-f]/g;
  if (!hexRegex.test(out) || (out.length !== 3 && out.length !== 6)) {
    throw new Error('input is not a valid hex color.');
  }
  if (out.length === 3) {
    const first = out[0];
    const second = out[1];
    const last = out[2];
    out = first + first + second + second + last + last;
  }
  out = out.toUpperCase();
  const first = out[0] + out[1];
  const second = out[2] + out[3];
  const last = out[4] + out[5];
  return (
    `${parseInt(first, 16)
    }, ${
      parseInt(second, 16)
    }, ${
      parseInt(last, 16)}`
  );
};
export const boxShadow = {
  boxShadow:
    `0 10px 30px -12px rgba(${
      hexToRgb(blackColor)
    }, 0.42), 0 4px 25px 0px rgba(${
      hexToRgb(blackColor)
    }, 0.12), 0 8px 10px -5px rgba(${
      hexToRgb(blackColor)
    }, 0.2)`,
};
export const transition = {
  transition: 'all 0.33s cubic-bezier(0.685, 0.0473, 0.346, 1)',
};
