/* Map lineup pages: open a lineup video in one shared dialog. Videos load only when asked for. */
(function () {
  var dialog = document.getElementById("lineup-video");
  if (!dialog || typeof dialog.showModal !== "function") return; // without <dialog> the links open the video file
  var video = dialog.querySelector("video");
  var title = dialog.querySelector(".video-dialog__title");

  document.addEventListener("click", function (e) {
    var link = e.target.closest("[data-video]");
    if (link) {
      e.preventDefault();
      title.textContent = link.getAttribute("data-title") || "";
      video.src = link.getAttribute("data-video");
      dialog.showModal();
      var p = video.play();
      if (p && p.catch) p.catch(function () {});
      return;
    }
    if (e.target.closest("[data-close]") || e.target === dialog) dialog.close();
  });

  dialog.addEventListener("close", function () {
    video.pause();
    video.removeAttribute("src");
    video.load();
  });
})();
