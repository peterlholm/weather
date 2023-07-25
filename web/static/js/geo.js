
function findLocation(resultfunc) {
    // const status = document.querySelector("#status");
    // const mapLink = document.querySelector("#map-link");

    // mapLink.href = "";
    // mapLink.textContent = "";

    function success(position) {
        const latitude = position.coords.latitude;
        const longitude = position.coords.longitude;
        console.log("Position: " + latitude + " " + longitude);
        resultfunc(latitude, longitude);
    }

    function error() {
        status.textContent = "Unable to retrieve your location";
        console.log("Error in finding position");
        resultfunc(NaN, NaN);
    }

    function get_location() {
        if (!navigator.geolocation) {
            status.textContent = "Geolocation is not supported by browser";
        } else {
            status.textContent = "Locating..",
                navigator.geolocation.getCurrentPosition(success, error);
        }
    }
    console.log("findlocation called");
    get_location();
}