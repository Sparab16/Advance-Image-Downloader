(function (){
    // Handling the min date condition
    var currentDate = new Date();
    var currentMonth = currentDate.getMonth() + 1
    var currentDay = currentDate.getDate()
    var currentYear = currentDate.getFullYear()

    if (currentMonth < 10){
        currentMonth = '0' + currentMonth.toString();
    }

    if (currentDay < 10) {
        currentDay = '0' + currentDay.toString();
    }

    var minDate = currentYear + '-' + currentMonth + '-' + currentDay;
    document.querySelector('#txtDate').min = minDate;
})();

