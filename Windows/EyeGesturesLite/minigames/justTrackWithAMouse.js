function mousemove(event) {
/*     console.log(
      'pageX: ', event.pageX, 'pageY: ', event.pageY,
      'clientX: ', event.clientX, 'clientY:', event.clientY)
     */
    return [event.pageX, event.pageY]

}

window.addEventListener('mousemove', mousemove);