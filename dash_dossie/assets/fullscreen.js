document.addEventListener("DOMContentLoaded", function () {
    const fullscreenButton = document.getElementById("fullscreen-button");
    const container = document.getElementById("fullscreen-container");

    if (fullscreenButton && container) {
        fullscreenButton.addEventListener("click", function () {
            if (!document.fullscreenElement) {
                // Ativar tela cheia
                if (container.requestFullscreen) {
                    container.requestFullscreen();
                } else if (container.webkitRequestFullscreen) { /* Safari */
                    container.webkitRequestFullscreen();
                } else if (container.msRequestFullscreen) { /* IE11 */
                    container.msRequestFullscreen();
                }
            } else {
                // Sair da tela cheia
                if (document.exitFullscreen) {
                    document.exitFullscreen();
                } else if (document.webkitExitFullscreen) { /* Safari */
                    document.webkitExitFullscreen();
                } else if (document.msExitFullscreen) { /* IE11 */
                    document.msExitFullscreen();
                }
            }
        });
    }
});