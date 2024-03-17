function countdown(element, datetime) {
    var countdownDate = new Date(datetime).getTime();
    var el = document.getElementById(element);

    var interval = setInterval(function() {
        var now = new Date().getTime();
        var distance = countdownDate - now;

        var days = Math.floor(distance / (1000 * 60 * 60 * 24));
        var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
        var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        var seconds = Math.floor((distance % (1000 * 60)) / 1000);

        el.innerHTML = days + "d " + hours + "h " +
            minutes + "m ";

        if (distance < 0) {
            el.innerHTML = "EXPIRED";
            clearInterval(interval);
        }
    }, 1000);
}