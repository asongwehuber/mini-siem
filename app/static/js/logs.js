document.addEventListener(
    "DOMContentLoaded",
    function(){

        loadLogs();

    }
);



function loadLogs(page = 1){

    fetch("/logs?page=" + page)

    .then(response => response.json())

    .then(data => {

        displayLogs(data.logs);

        updatePagination(
            data.page,
            data.pages,
            data.total
        );

    })

    .catch(error => {

        console.error(
            "Error loading logs:",
            error
        );

    });

}




function displayLogs(logs){


    let table =
        document.getElementById(
            "logs-table"
        );


    table.innerHTML = "";


    let rows = "";


    logs.forEach(log => {


        rows += `

        <tr>

            <td>${log.id}</td>

            <td>${log.timestamp}</td>

            <td>${log.source_ip}</td>

            <td>${log.hostname || "-"}</td>

            <td>${log.event_type}</td>

            <td>
                <span class="severity-${log.severity}">
                    ${log.severity}
                </span>
            </td>

            <td>

                <button onclick="viewLog(${log.id})">
                    👁 View
                </button>

            </td>

        </tr>

        `;


    });


    table.innerHTML = rows;

}




function applyFilters(page = 1){


    let source_ip =
        document.getElementById(
            "search-input"
        ).value.trim();



    let severity =
        document.getElementById(
            "severity-filter"
        ).value;



    let event_type =
        document.getElementById(
            "event-filter"
        ).value;



    let period =
        document.getElementById(
            "time-filter"
        ).value;



    let start_time =
        document.getElementById(
            "start-time"
        ).value;



    let end_time =
        document.getElementById(
            "end-time"
        ).value;



    let params = new URLSearchParams();



    params.append(
        "page",
        page
    );



    if(source_ip){

        params.append(
            "source_ip",
            source_ip
        );

    }



    if(severity){

        params.append(
            "severity",
            severity
        );

    }



    if(event_type){

        params.append(
            "event_type",
            event_type
        );

    }



    /*
    TIME FILTER
    */


    if(period && period !== "custom"){

        params.append(
            "period",
            period
        );

    }



    if(period === "custom"){


        if(start_time && end_time){


            params.append(
                "start_time",
                start_time
            );


            params.append(
                "end_time",
                end_time
            );


        }


    }

    window.history.pushState(
        {},
        "",
        "?" + params.toString()
    );


    fetch(
        "/search?" + params.toString()
    )


    .then(response => response.json())


    .then(data => {


        displayLogs(
            data.logs
        );


        updatePagination(
            data.page,
            data.pages,
            data.total
        );


    })


    .catch(error => {


        console.error(
            "Filter error:",
            error
        );


    });


}





function viewLog(id){

    fetch("/log/" + id)

    .then(response => response.json())

    .then(log => {

        alert(

            "LOG DETAILS\n\n" +

            "ID: " + log.id + "\n" +

            "Time: " + log.timestamp + "\n" +

            "Source IP: " + log.source_ip + "\n" +

            "Hostname: " + log.hostname + "\n" +

            "Event: " + log.event_type + "\n" +

            "Severity: " + log.severity + "\n\n" +

            "Message:\n" +

            log.message

        );

    })


    .catch(error => {

        console.error(
            "View log error:",
            error
        );

    });

}






function updatePagination(page, pages, total){


    let info =
        document.getElementById(
            "pagination-info"
        );


    if(info){

        info.innerHTML =
        `
        Showing page ${page} of ${pages}
        (${total} total logs)
        `;

    }



    let buttons =
        document.getElementById(
            "pagination-buttons"
        );


    if(!buttons)
        return;



    buttons.innerHTML = "";



    if(page > 1){

        buttons.innerHTML +=
        `
        <button onclick="changeLogPage(${page-1})">
            ◀ Previous
        </button>
        `;

    }



    if(page < pages){

        buttons.innerHTML +=
        `
        <button onclick="changeLogPage(${page+1})">
            Next ▶
        </button>
        `;

    }

}






function toggleCustomTime(){

    let selected =
        document.getElementById(
            "time-filter"
        ).value;



    let customBox =
        document.getElementById(
            "custom-time-range"
        );



    if(selected === "custom"){

        customBox.style.display = "flex";

    }

    else{


        customBox.style.display = "none";


        document.getElementById(
            "start-time"
        ).value = "";


        document.getElementById(
            "end-time"
        ).value = "";


    }

}

function changeLogPage(page){

    let params =
        new URLSearchParams(
            window.location.search
        );


    params.set(
        "page",
        page
    );


    fetch(
        "/search?" +
        params.toString()
    )


    .then(response => response.json())


    .then(data => {


        displayLogs(
            data.logs
        );


        updatePagination(
            data.page,
            data.pages,
            data.total
        );


    });


}