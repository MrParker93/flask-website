(function () {
    console.log('ready!');
})();

const postElements = document.getElementsByClassName('entry');

for (var i = 0; i < postElements.length; i++) {
  postElements[i].addEventListener('click', function () {
    const postId = this.getElementsByTagName('h2')[0].getAttribute('id');
      const node = this;
      fetch(`/delete/${postId}`)
        .then(function (response) {
          return response.json();
        })
        .then(function (result) {
          if (result.status === 1) {
            node.parentNode.removeChild(node);
            console.log(result);
          }
          location.reload();
        })
        .catch(function (error) {
          console.log(error);
        });
    });
}