document.addEventListener(
    "DOMContentLoaded",
    function(){

        loadAlerts(1);

    }
);



let allAlerts = [];




function loadAlerts(page = 1){


    fetch(
        "/alerts?page=" + page
    )


    .then(response => response.json())


    .then(data => {


        allAlerts = data.alerts;


        displayAlerts(
            data.alerts
        );


        updateAlertPagination(
            data.page,
            data.pages,
            data.total
        );


    })


    .catch(error => {


        console.error(
            "Error loading alerts:",
            error
        );


    });


}






function displayAlerts(alerts){


    let table =
        document.getElementById(
            "alerts-table"
        );


    table.innerHTML = "";


    let rows = "";



    alerts.forEach(alert => {



        rows += `

        <tr>


            <td>
                ${alert.id}
            </td>



            <td>
                ${alert.timestamp}
            </td>



            <td>

                <strong>
                ${alert.alert_name}
                </strong>

                <br>

                <small>
                ${alert.description || ""}
                </small>

            </td>




            <td>

                <span class="severity-${alert.severity}">

                    ${alert.severity.toUpperCase()}

                </span>

            </td>




            <td>

                ${alert.source_ip || "-"}

            </td>




            <td>

                ${alert.event_count}

            </td>




            <td>

                ${alert.status}

            </td>




            <td>


                ${
                    alert.status === "OPEN"

                    ?

                    `

                    <button onclick="resolveAlert(${alert.id})">

                        ✅ Resolve

                    </button>

                    `

                    :

                    `✔ Closed`

                }



            </td>


        </tr>

        `;



    });



    table.innerHTML = rows;


}








function applyAlertFilters(page = 1){


    let search =
        document.getElementById(
            "search-input"
        )
        .value
        .trim();



    let severity =
        document.getElementById(
            "severity-filter"
        )
        .value;



    let status =
        document.getElementById(
            "status-filter"
        )
        .value;



    let period =
        document.getElementById(
            "time-filter"
        )
        .value;



    let start_time =
        document.getElementById(
            "start-time"
        )
        .value;



    let end_time =
        document.getElementById(
            "end-time"
        )
        .value;





    let params = new URLSearchParams();



    params.append(
        "page",
        page
    );





    if(search){

        params.append(
            "source_ip",
            search
        );

    }





    if(severity){

        params.append(
            "severity",
            severity
        );

    }





    if(status){

        params.append(
            "status",
            status
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






    fetch(
        "/alerts/search?" + params.toString()
    )


    .then(response => response.json())


    .then(data => {


        displayAlerts(
            data.alerts
        );


        updateAlertPagination(
            data.page,
            data.pages,
            data.total
        );


    })


    .catch(error => {


        console.error(
            "Alert filter error:",
            error
        );


    });



}








function resolveAlert(id){


    fetch(
        "/resolve-alert/" + id,
        {
            method:"POST"
        }
    )



    .then(response => response.json())


    .then(data => {


        alert(
            data.message
        );


        loadAlerts();


    })



    .catch(error => {


        console.error(
            "Resolve error:",
            error
        );


    });



}








function updateAlertPagination(
    page,
    pages,
    total
){


    let info =
        document.getElementById(
            "alerts-info"
        );



    if(info){


        info.innerHTML =

        `
        Showing page ${page} of ${pages}
        (${total} total alerts)
        `;


    }





    let buttons =
        document.getElementById(
            "alerts-pagination-buttons"
        );



    if(!buttons)
        return;





    buttons.innerHTML = "";





    if(page > 1){


        buttons.innerHTML +=


        `

        <button onclick="loadAlerts(${page-1})">

            ◀ Previous

        </button>

        `;


    }





    if(page < pages){


        buttons.innerHTML +=


        `

        <button onclick="loadAlerts(${page+1})">

            Next ▶

        </button>

        `;


    }


}








function toggleCustomTime(){


    let selected =
        document.getElementById(
            "time-filter"
        )
        .value;




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